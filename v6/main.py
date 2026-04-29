import os
import json
import pandas
from ..io import read, write_force, file_exists
from ..parallel_v4 import parallel_v4, async_wrap
import yaml
import re
from .. import llm


HOME = os.environ['HOME']


version = "v6"


models = [
    # "gpt-5-chat-latest",
    # "gpt-5.5-low",
    # "gpt-5.5-medium",
    # "gpt-5.5-high",
    "google/gemma-4-31B-it",
]


mode = "pretagged"


# size = "full"
# size = "half"
# size = "quarter"
size = "eighth"
# size = "sixteenth"
# size = "10"
# size = "5"


books = [
    # "1823_Duras-Claire-de_Ourika",
    # "1830_Balzac-Honoré-de_Sarrasine",
    "1731_Prévost-Antoine-François_Manon-Lescaut_PER-ONLY",
    "1832_Sand-George_Indiana_PER-ONLY",
]


split_size = 2
grouping = split_size*3
overlap = split_size*2


concurrency = 32


def jdump(x):
    return json.dumps(x, indent=2, ensure_ascii=0)


def run(model, book):
    splitter = ". "

    sacr_full = read(f"{HOME}/github.com/loicbourgois/em/SACR_PER/{book}.generated_sacr")
    folder = f"{HOME}/github.com/loicbourgois/em/{version}/{book}/{mode}-{size}-{model}"
    print(folder)
    parts = sacr_full.split(splitter)
    if size == "full":
        parts = parts
    elif size == "sixteenth":
        parts = parts[0:len(parts) // 16]
    elif size == "eighth":
        parts = parts[0:len(parts) // 8]
    elif size == "half":
        parts = parts[0:len(parts) // 2]
    elif size == "5":
        parts = parts[0:5]
    else:
        raise Exception("not implemented")
    gold = splitter.join(parts) + "."
    write_force(f"{folder}/01_gold.sacr", gold)


    silver = read(f"{folder}/01_gold.sacr")
    pattern = r"(\{[A-Za-z0-9_\-]+:EN\=\"PER\" )"
    matches = re.findall(pattern, silver)
    for matche in matches:
        silver = silver.replace(matche, '{____ ')
    parts = [  x + "." for x in silver.split(splitter) ]
    l = len(parts)
    if parts[l-1][-1] == "." and parts[l-1][-2] == ".":
        parts[l-1] = parts[l-1][0:-1]
    merged_parts = []
    skip_next = False
    for i, p in enumerate(parts):
        if skip_next:
            skip_next = False
            continue
        if p.strip() == "{____":
            if i + 1 < len(parts):
                merged_parts.append(p + parts[i + 1])
                skip_next = True
            else:
                merged_parts.append(p)
        else:
            merged_parts.append(p)
    parts = merged_parts
    write_force(f"{folder}/02_parts.json", jdump(parts))




    step = grouping - overlap
    groups = []
    for i in range(0, len(parts), step):
        chunk = parts[i:i + grouping]
        uu = []
        for aa in range(0, len(chunk), step):
            uu.append(" ".join(chunk[aa:aa+step]))
        if len(uu) == 3:
            groups.append(uu)
    assert 'EN="PER"' not in jdump(groups)
    write_force(f"{folder}/03_groups.json", jdump(groups))


    # exit(1)


    for i, group in enumerate(groups):
        write_force(
            f"{folder}/04_request_{i}.md",
            read(f"{HOME}/github.com/loicbourgois/em/{version}/template.md").format(
                input=jdump(group)
            ),
        )


    def function(i):
        groups_ = json.loads(read(f"{folder}/03_groups.json"))
        out_path = f"{folder}/05_response_{i}.json"
        if file_exists(out_path) and False:
            pass
        else:
            prompt = read(f"{folder}/04_request_{i}.md")
            r = llm.get(prompt, model)
            try:
                yaml_ = yaml.safe_load(r.replace("```yaml", "").replace("```json", "").replace("```", ""))
            except:
                yaml_ = {"sacr": []}
            entity_count_out = []
            entity_count_in = []
            for l in yaml_['sacr']:
                entity_count_out.append(l.count("{"))
            for l in groups_[i]:
                entity_count_in.append(l.count("{____"))
            write_force(
                out_path,
                jdump({
                    "in_out": {
                        "in": groups_[i],
                        "out": [ 
                            re.sub(
                                r"\{([A-Za-z0-9_À-ÖØ-öø-ÿŒœ\-]+ )",
                                "{____ ",
                                x
                            )
                            for x in yaml_['sacr']
                        ]
                    },
                    "metadata": {
                        "entity_count_in": entity_count_in,
                        "entity_count_out": entity_count_out,
                    },
                    "data": yaml_,
                }),
            )
    @async_wrap
    def function_async(x, done_set, total_count):
        return function(x)
    data = []
    for i in range(len(groups)):
        try:
            j = json.loads(read(f"{folder}/05_response_{i}.json"))
        except:
            data.append(i)
    
    if len(data):
        print("model warmup")
        r = llm.get("Hello", model)
        print(r)

    parallel_v4(
        data,
        function_async,
        concurrency = concurrency,
    )


    for rerun_i in range(4):
        rerun = []
        for i in range(len(groups)):
            j = json.loads(read(f"{folder}/05_response_{i}.json"))
            if json.dumps(j['metadata']['entity_count_in']) != json.dumps(j['metadata']['entity_count_out']):
                rerun.append(i)
                continue
            
            input_ = "".join(json.loads(read(f"{folder}/03_groups.json"))[i])
            output_ = re.sub(
                r"\{([A-Za-z0-9_À-ÖØ-öø-ÿŒœ]+ )",
                "{____ ",
                "".join(j['data']['sacr'])
            )
            if input_ != output_:
                rerun.append(i)
        if len(rerun):
            print(f"rerun #{rerun_i} - {rerun}")
            parallel_v4(
                rerun,
                function_async,
                concurrency = concurrency,
            )
        else:
            break


    aa = [[] for _ in range(len(groups)+2)]
    for i in range(len(groups)):
        j = json.loads(read(f"{folder}/05_response_{i}.json"))
        sacr = j['data']['sacr']
        try:
            aa[i].append(sacr[0])
            aa[i+1].append(sacr[1])
            aa[i+2].append(sacr[2])
        except:
            pass
    write_force(
        f"{folder}/06_mentions.json",
        jdump(aa),
    )


    sacr_split = json.loads(read(f"{folder}/06_mentions.json"))
    for i in range(len(groups)):
        s1 = ""
        s2 = ""
        s3 = ""
        try:
            s1 = sacr_split[i][-1]
            s2 = sacr_split[i+1][-2]
            s3 = sacr_split[i+2][-3]
        except:
            pass
        pattern = r"\{([A-Za-z0-9_À-ÖØ-öø-ÿŒœ]+ )\b"
        matches = re.findall(pattern, s1)
        for match in matches:
            s1 = s1.replace("{"+match, "{"+f"{i}_" + match)
        matches = re.findall(pattern, s2)
        for match in matches:
            s2 = s2.replace("{"+match, "{"+f"{i}_" + match)
        matches = re.findall(pattern, s3)
        for match in matches:
            s3 = s3.replace("{"+match, "{"+f"{i}_" + match)
        try:
            sacr_split[i][-1] = s1
            sacr_split[i+1][-2] = s2
            sacr_split[i+2][-3] = s3
        except:
            pass
    write_force(
        f"{folder}/07_unique_mentions.json",
        jdump(sacr_split),
    )


    unique_mentions = json.loads(read(f"{folder}/07_unique_mentions.json"))
    pairs = []
    for j in range(len(unique_mentions)):
        aa = unique_mentions[j]
        pattern = r"\{([A-Za-z0-9_À-ÖØ-öø-ÿŒœ]+ )\b"
        m1 = re.findall(pattern, aa[0])
        m2 = []
        m3 = []
        try:
            m2 = re.findall(pattern, aa[1])
            m3 = re.findall(pattern, aa[2])
        except:
            pass
        # print(f"{j} {len(m1)} {len(m2)} {len(m3)}")
        for i in range(len(m1)):
            if len(m2):
                assert len(m1) == len(m2)
                pairs.append([m1[i], m2[i]])
            if len(m3):
                assert len(m1) == len(m2) == len(m3)
                pairs.append([m1[i], m3[i]])
    write_force(
        f"{folder}/08_pairs.json",
        jdump(pairs),
    )


    mentions = json.loads(read(f"{folder}/07_unique_mentions.json"))
    pairs = json.loads(read(f"{folder}/08_pairs.json"))
    for i, m1 in enumerate(mentions):
        for j, m2 in enumerate(m1):
            for pair in pairs:
                mentions[i][j] = mentions[i][j].replace("{"+pair[0], "{"+pair[1])
    write_force(
        f"{folder}/09_mentions.json",
        jdump(mentions),
    )


    mentions = json.loads(read(f"{folder}/09_mentions.json"))
    mentions_final = []
    for ls in mentions:
        kv = {}
        for l in ls:
            if kv.get(l):
                kv[l] += 1
            else:
                kv[l] = 1
        top = sorted(kv.items(), key=lambda x: x[1], reverse=True)[0][0]
        mentions_final.append(top)
    write_force(
        f"{folder}/10_mentions_final.json",
        jdump(mentions_final),
    )



    sacr = " ".join(mentions_final)
    pattern = r"\{([A-Za-z0-9_À-ÖØ-öø-ÿŒœ]+ )"
    matches = re.findall(pattern, sacr)
    for match in matches:
        sacr = sacr.replace(match, match[:-1] + ':EN="PER" ')
    write_force(
        f"{folder}/11_silver.sacr",
        sacr,
    )


    pattern = r"\{([A-Za-z0-9_À-ÖØ-öø-ÿŒœ]+:)"
    matches = set(re.findall(pattern, read(f"{folder}/11_silver.sacr")))
    print(matches)


    from ..propp.propp_fr.src.propp_fr.propp_fr_generate_tokens_and_entities_from_sacr import (
        generate_tokens_and_entities_from_sacr
    )
    generate_tokens_and_entities_from_sacr(
        file_name=f"01_gold.sacr",
        files_directory=folder,
    )
    generate_tokens_and_entities_from_sacr(
        file_name="11_silver.sacr",
        files_directory=folder,
    )
    l1 = len(read(f"{folder}/01_gold.sacr.txt"))
    l2 = len(read(f"{folder}/11_silver.sacr.txt"))
    assert l1 == l2, f"{l1} != {l2}"
    
    
    from ..propp.propp_fr.src.propp_fr.propp_fr_coreference_resolution_module import (
        initialize_gold_coreference_matrix_from_entities_df,
        coreference_resolution_metrics,
    )
    coreference_metrics_df = coreference_resolution_metrics(
        initialize_gold_coreference_matrix_from_entities_df(
            pandas.read_csv(f"{folder}/01_gold.sacr.entities", sep='\t')
        ), 
        initialize_gold_coreference_matrix_from_entities_df(
            pandas.read_csv(f"{folder}/11_silver.sacr.entities", sep='\t')
        ),
    )
    coreference_metrics_df.to_csv(f"{folder}/12_results.tsv", sep="\t")


for model in models:
    for book in books:
        run(model, book)
