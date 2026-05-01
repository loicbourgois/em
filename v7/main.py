import os
import json
import pandas
from ..io import read, write_force, file_exists
from ..parallel_v4 import parallel_v4, async_wrap
import yaml
import re
from .. import llm


HOME = os.environ['HOME']


version = "v7"


models = [
    # "gpt-5-chat-latest",
    "gpt-5.5-none",
    # "gpt-5.5-low",
    # "gpt-5.5-medium",
    # "gpt-5.5-high",
    # "google/gemma-4-31B-it",
]


mode = "pretagged"


sizes = [
    "sixteenth",
    "eighth",
    # "quarter",
    # "half",
    # "full",
]


books = [
    "1823_Duras-Claire-de_Ourika",
    "1830_Balzac-Honoré-de_Sarrasine",
    "1731_Prévost-Antoine-François_Manon-Lescaut_PER-ONLY",
    "1832_Sand-George_Indiana_PER-ONLY",
]


split_size = 2
grouping = split_size*3
overlap = split_size*2


concurrency = 32


def jdump(x):
    return json.dumps(x, indent=2, ensure_ascii=0)


def jread(path):
    return json.loads(read(path))


def run(model, book, size):
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
    elif size == "quarter":
        parts = parts[0:len(parts) // 4]
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


    i = 0
    while True:
        if parts[i].count("{") != parts[i].count("}"):
            parts[i] = parts[i] + " " + parts[i + 1]
            parts.pop(i + 1)
            i -= 1
        else:
            i += 1
        if i >= len(parts):
            break


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
    write_force(f"{folder}/02_parts.txt", " ".join(parts).replace('{____ ', "").replace('}', "") )
    

    for p in parts:
        # TODO: better way to assert everything open and close properly : { -> }
        # eg, incorrect : "le chevalier de B.}, {____ qui} en était gouverneur."
        assert p.count("{") == p.count("}"), p
        assert ".. " not in p, p


    from ..propp.propp_fr.src.propp_fr.propp_fr_generate_tokens_and_entities_from_sacr import (
        generate_tokens_and_entities_from_sacr
    )
    generate_tokens_and_entities_from_sacr(
        file_name=f"01_gold.sacr",
        files_directory=folder,
    )
    print(len(read(f"{folder}/01_gold.sacr.txt")))
    print(len(read(f"{folder}/02_parts.txt")))
    assert read(f"{folder}/02_parts.txt") == read(f"{folder}/01_gold.sacr.txt")
    write_force(f"{folder}/02_parts.json", jdump(parts))


    print("setup done")


    parts = jread(f"{folder}/02_parts.json")
    l = len(parts)
    i = 0
    retry = 0
    cache_allowed = True
    while True:
        print(f"{i}/{l} - {retry}")
        parts_formatted = jread(f"{folder}/02_parts.json")
        for j in range(i):
            parts_formatted[j] = jread(f"{folder}/03_{j}_out.json")['focus_formatted']
        prompt = read(f"{HOME}/github.com/loicbourgois/em/v7/template.md").format(
            input=jdump({
                "text": parts_formatted,
                "focus": parts[i],
            })
        )
        write_force(f"{folder}/03_{i}_in.md", prompt)
        if "{____" not in parts[i]:
            write_force(f"{folder}/03_{i}_out.json", jdump({
                "focus_formatted": parts[i],
            }))
        elif cache_allowed and file_exists(f"{folder}/03_{i}_out.json") and retry == 0:
            jresponse = jread(f"{folder}/03_{i}_out.json")
        else:
            response = llm.get(prompt, model)
            jresponse = yaml.safe_load(response.replace("```yaml", "").replace("```json", "").replace("```", ""))
            write_force(f"{folder}/03_{i}_out.json", jdump(jresponse))


        focus = parts[i]
        focus_formatted = jread(f"{folder}/03_{i}_out.json")['focus_formatted']
        focus_formatted_back = re.sub(
            r"\{([A-Za-z0-9_À-ÖØ-öø-ÿŒœê\-É]+ )",
            "{____ ",
            focus_formatted
        )
        try:
            assert focus.count("{") == focus_formatted.count("{")
            assert focus.count("}") == focus_formatted.count("}")
            assert focus == focus_formatted_back
            i += 1
            retry = 0
        except:
            print(focus)
            print(focus_formatted_back)
            retry += 1
        if i >= l:
            break

    
    parts_formatted = jread(f"{folder}/02_parts.json")
    for j in range(len(parts_formatted)):
        parts_formatted[j] = jread(f"{folder}/03_{j}_out.json")['focus_formatted']
    sacr = " ".join(parts_formatted)
    pattern = r"\{([A-Za-z0-9_À-ÖØ-öø-ÿŒœê\-É]+ )"
    matches = re.findall(pattern, sacr)
    for match in matches:
        sacr = sacr.replace("{"+match, "{"+match[:-1] + ':EN="PER" ')
    write_force(
        f"{folder}/04_silver.sacr",
        sacr,
    )


    from ..propp.propp_fr.src.propp_fr.propp_fr_generate_tokens_and_entities_from_sacr import (
        generate_tokens_and_entities_from_sacr
    )
    generate_tokens_and_entities_from_sacr(
        file_name="04_silver.sacr",
        files_directory=folder,
    )
    assert 'EN="PER"' not in read(f"{folder}/04_silver.sacr.txt")
    l1 = len(read(f"{folder}/01_gold.sacr.txt"))
    l2 = len(read(f"{folder}/04_silver.sacr.txt"))
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
            pandas.read_csv(f"{folder}/04_silver.sacr.entities", sep='\t')
        ),
    )
    coreference_metrics_df.to_csv(f"{folder}/05_results.tsv", sep="\t")



for model in models:
    for book in books:
        for size in sizes:
            run(model, book, size)
