import os
import json
import pandas
from ..io import read, write_force
from ..parallel_v4 import parallel_v4, async_wrap
import yaml
import re
from .. import llm


HOME = os.environ['HOME']


RUN_LLM_1 = True
# RUN_LLM_1 = False
RUN_LLM_2 = True
# RUN_LLM_2 = False
RUN_lbl = True
# RUN_lbl = False


# model = "gpt-5.5-high"
# model = "gpt-5.5-medium"
# model = "gpt-5.5-low"
# model = "gpt-5-chat-latest"
# model = "google/gemma-4-E4B-it"
model = "google/gemma-4-31B-it"


mode = "pretagged"


# size = "full"
# size = "half"
# size = "quarter"
size = "eighth"
# size = "sixteenth"
# size = "10"
# size = "5"


# book = "1823_Duras-Claire-de_Ourika"
book = "1830_Balzac-Honoré-de_Sarrasine"
# book = "1832_Sand-George_Indiana_PER-ONLY"
# book = "1731_Prévost-Antoine-François_Manon-Lescaut"


sacr_full = read(f"{HOME}/github.com/loicbourgois/em/SACR_PER/{book}.generated_sacr")
folder = f"{HOME}/github.com/loicbourgois/em/v5/{book}/{mode}-{size}-{model}"


paragraphs = [ x for x in sacr_full.split("\n") if len(x) ]
if size == "full":
    paragraphs = paragraphs
elif size == "half":
    paragraphs = paragraphs[0:len(paragraphs) // 2]
elif size == "quarter":
    paragraphs = paragraphs[0:len(paragraphs) // 4]
elif size == "eighth":
    paragraphs = paragraphs[0:len(paragraphs) // 8]
elif size == "sixteenth":
    paragraphs = paragraphs[0:len(paragraphs) // 16]
elif size == "10":
    paragraphs = paragraphs[0:10]
elif size == "5":
    paragraphs = paragraphs[0:5]
else:
    raise Exception("not implemented")
write_force(f"{folder}/01_gold.sacr", "\n".join(paragraphs) + "\n")



content = read(f"{folder}/01_gold.sacr")
pattern = r"(\{[A-Za-z0-9_]+:EN\=\"PER\" )"
matches = re.findall(pattern, content)
for matche in matches:
    content = content.replace(matche, '{____ ')
write_force(
    f"{folder}/02_prettagged.sacr",
    content,
)


s1 = read(f"{folder}/01_gold.sacr")
s2 = read(f"{folder}/02_prettagged.sacr")
c1 = s1.count("{")
c2_1 = s2.count("{")
c2_2 = s2.count("{____")
print(f"mentions: {c1} | {c2_1} | {c2_2}")


# exit(1)


# 03
content = read(f"{folder}/02_prettagged.sacr")
content_split = content.split("\n")
content_split_len = len(content_split)
for i, x in enumerate(content_split):
    if len(x):
        write_force(
            f"{folder}/03_{i}.md",
            read(f"{HOME}/github.com/loicbourgois/em/v5/template.md").format(
                input=json.dumps([x], indent=2, ensure_ascii=False)
            ),
        )


# 04
def function(x):
    prompt = read(f"{folder}/03_{x['i']}.md")
    r = llm.get(prompt, x['model'])
    write_force(
        f"{folder}/04_{x['i']}.md",
        r,
    )
    return x
@async_wrap
def function_async(x, done_set, total_count):
    return function(x)
data = []
for i in range(content_split_len-1):
    data.append({
        "model": model,
        "i": i,
    })
if RUN_LLM_1:
    output = parallel_v4(
        data,
        function_async,
        concurrency = 100,
    )


def update_count():
    sacr_lines = []
    for i in range(content_split_len-1):
        content = read(f"{folder}/04_{i}.md")
        try:
            yaml_ = yaml.safe_load(content.replace("```yaml", "").replace("```json", "").replace("```", ""))
            sacr_lines.append(yaml_['sacr'][0].replace("{", "{"+f"{i}_"))
        except:
            sacr_lines.append("")
    write_force(
        f"{folder}/05.sacr",
        "\n".join(sacr_lines) + "\n",
    )
    status = "ok"
    counts = []
    c1 = read(f"{folder}/01_gold.sacr").split("\n")
    c5 = read(f"{folder}/05.sacr").split("\n")
    for i in range(content_split_len-1):
        count_1 = c1[i].count("{")
        count_5 = c5[i].count("{")
        if count_1 != count_5:
            status = "error"
        counts.append({
            "i": i,
            "count": count_5-count_1
        })
    df = pandas.DataFrame(counts)
    df.to_csv(f"{folder}/00_counts.tsv", sep="\t", index=False)
    return status


def run_one(i):
    print(f"run_one - {i}")
    prompt = read(f"{folder}/03_{i}.md")
    r = llm.get(prompt, model)
    write_force(
        f"{folder}/04_{i}.md",
        r,
    )


@async_wrap
def run_one_async(i, done_set, total_count):
    return run_one(i)


for n in range(10):
    status = update_count()
    if status == "ok":
        break
    df_count = pandas.read_csv(f"{folder}/00_counts.tsv", sep="\t")
    data = []
    for _, row in df_count.iterrows():
        if row["count"] != 0:
            data.append(row['i'])
    print(data)
    parallel_v4(
        data,
        run_one_async,
        concurrency = 100,
    )


status = update_count()
if status != "ok":
    print("ERROR in 00_counts.tsv")
    # exit(1)
else:
    print("OK 00_counts.tsv")


# 06
lines = []
c1 = read(f"{folder}/01_gold.sacr").split("\n")
c5 = read(f"{folder}/05.sacr").split("\n")
for i in range(content_split_len-1):
    l1 = c1[i].count("{")
    l5 = c5[i].count("{")
    lines.append(f"{l5-l1}")
write_force(
    f"{folder}/06.md",
    "\n".join(lines) + "\n",
)


print("07")
data = []
for i in range(content_split_len-1):
    content = read(f"{folder}/04_{i}.md")
    yaml_ = yaml.safe_load(content.replace("```yaml", "").replace("```json", "").replace("```", ""))
    data.append(
        {
            "relationships": [
                {
                    "entity_1": f"{i}_" + x['entity_1'],
                    "entity_2": f"{i}_" + x['entity_2'],
                    "relationship": x['relationship'],
                } for x in yaml_['relationships']
            ],
            "entities": yaml_['entities'],
            "sacr": yaml_['sacr'][0].replace("{", "{"+f"{i}_")
        }
    )
write_force(
    f"{folder}/07.md",
    read(f"{HOME}/github.com/loicbourgois/em/v5/template_2.md").format(
        input=json.dumps(data, indent=2, ensure_ascii=False)
    ),
)


# exit(1)


if RUN_LLM_2:
    print("08 - run ai 2")
    prompt = read(f"{folder}/07.md")
    r = llm.get(prompt, model)
    write_force(
        f"{folder}/08.md",
        r,
    )


print("09")
groups = yaml.safe_load(read(f"{folder}/08.md").replace("```yaml", "").replace("```json", "").replace("```", ""))["groups"]
sacr = read(f"{folder}/05.sacr")
for k, v in groups.items():
    for ref in v['references']:
        sacr = sacr.replace(f"{ref} ", k + ':EN="PER" ')
pattern = r"\{([A-Za-z0-9_]+ )\b"
matches = re.findall(pattern, sacr)
for match in matches:
    sacr = sacr.replace(match, match[:-1] + ':EN="PER" ')
write_force(
    f"{folder}/09.sacr",
    sacr,
)


print("10")
groups = yaml.safe_load(read(f"{folder}/08.md").replace("```yaml", "").replace("```json", "").replace("```", ""))["groups"]
sacr = read(f"{folder}/05.sacr")
for k, v in groups.items():
    for ref in v['references']:
        sacr = sacr.replace(f"{ref} ", ref + ':EN="PER" ')
write_force(
    f"{folder}/10.sacr",
    sacr,
)


print("score")


from ..propp.propp_fr.src.propp_fr.propp_fr_generate_tokens_and_entities_from_sacr import (
    generate_tokens_and_entities_from_sacr
)
from ..propp.propp_fr.src.propp_fr.propp_fr_coreference_resolution_module import (
    initialize_gold_coreference_matrix_from_entities_df,
    coreference_resolution_metrics,
)



# exit(1)


generate_tokens_and_entities_from_sacr(
    file_name="01_gold.sacr",
    files_directory=folder,
)
gold_df = pandas.read_csv(f"{folder}/01_gold.sacr.entities", sep='\t')
gold_coreference_matrix = initialize_gold_coreference_matrix_from_entities_df(gold_df)


generate_tokens_and_entities_from_sacr(
    file_name="09.sacr",
    files_directory=folder,
)
silver_df = pandas.read_csv(f"{folder}/09.sacr.entities", sep='\t')
silver_coreference_matrix = initialize_gold_coreference_matrix_from_entities_df(silver_df)
coreference_metrics_df = coreference_resolution_metrics(
    gold_coreference_matrix, 
    silver_coreference_matrix,
)
coreference_metrics_df.to_csv(f"{folder}/00_result.tsv", sep="\t")


generate_tokens_and_entities_from_sacr(
    file_name="10.sacr",
    files_directory=folder,
)
silver_df = pandas.read_csv(f"{folder}/10.sacr.entities", sep='\t')
silver_coreference_matrix = initialize_gold_coreference_matrix_from_entities_df(silver_df)
coreference_metrics_df = coreference_resolution_metrics(
    gold_coreference_matrix, 
    silver_coreference_matrix,
)
coreference_metrics_df.to_csv(f"{folder}/11.tsv", sep="\t")



if RUN_lbl:
    print("score - line by line")
    lines = []
    c1 = read(f"{folder}/01_gold.sacr").split("\n")
    c5 = read(f"{folder}/05.sacr").split("\n")
    for i in range(content_split_len-1):
        print(f"{i}")
        l1 = c1[i]
        count_1 = l1.count("{")
        l5 = c5[i]
        write_force(
            f"{folder}/lbl/{i}.gold.sacr",
            l1,
        )
        for k, v in groups.items():
            for ref in v['references']:
                l5 = l5.replace(f"{ref} ", ref + ':EN="PER" ')
        pattern = r"\{([A-Za-z0-9_]+ )\b"
        matches = re.findall(pattern, l5)
        for match in matches:
            l5 = l5.replace(match, match[:-1] + ':EN="PER" ')
        count_5 = l5.count(':EN="PER"')
        write_force(
            f"{folder}/lbl/{i}.silver.sacr",
            l5,
        )
        score = None
        try:
            generate_tokens_and_entities_from_sacr(
                file_name=f"{i}.gold.sacr",
                files_directory=f"{folder}/lbl",
            )
            generate_tokens_and_entities_from_sacr(
                file_name=f"{i}.silver.sacr",
                files_directory=f"{folder}/lbl",
            )
            coreference_metrics_df = coreference_resolution_metrics(
                initialize_gold_coreference_matrix_from_entities_df(
                    pandas.read_csv(f"{folder}/lbl/{i}.gold.sacr.entities", sep='\t')
                ), 
                initialize_gold_coreference_matrix_from_entities_df(
                    pandas.read_csv(f"{folder}/lbl/{i}.silver.sacr.entities", sep='\t')
                ),
            )
            coreference_metrics_df.to_csv(f"{folder}/lbl/{i}.tsv", sep="\t")
            score = coreference_metrics_df.loc['CONLL', 'f1_score']
        except Exception as e:
            print("ERROR")
            print(e)
        lines.append(f"{i} | {count_5-count_1} | {score}")


    write_force(
        f"{folder}/lbl/01_counts.md",
        "\n".join(lines),
    )
