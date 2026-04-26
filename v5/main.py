# setup
import os
import json
import pandas
from ..io import read, write_force
from ..parallel_v4 import parallel_v4, async_wrap
from .. import oai
import yaml
import re
HOME = os.environ['HOME']


RUN_OAI_1 = True
RUN_OAI_1 = False
RUN_OAI_2 = True
# RUN_OAI_2 = False
RUN_lbl = True
# RUN_lbl = False


# model = "gpt-5.5-high"
model = "gpt-5.5-medium"
# model = "gpt-5-chat-latest"
mode = "pretagged"
size = "full"
# size = "half"
# size = "quarter"
folder = f"{HOME}/github.com/loicbourgois/em/v5/{mode}-{size}-{model}"
sacr = read(f"{HOME}/github.com/loicbourgois/em/gold/1823_Duras-Claire-de_Ourika/{size}.sacr")


def run_one(i):
    print(f"run_one - {i}")
    prompt = read(f"{folder}/03_{i}.md")
    r = oai.get(prompt, model)
    write_force(
        f"{folder}/04_{i}.md",
        r['response'],
    )


# if `error in 00_counts.md`
# check 00_counts.md, and rerun only needed paragraphs
# run_one(21)
# run_one(58)


# 01
paragraphs = [ x for x in sacr.split("\n") if len(x) ]
write_force(f"{folder}/01_gold.sacr", "\n".join(paragraphs) + "\n")


# 02
content = read(f"{folder}/01_gold.sacr")
for x in reversed(range(100)):
    content = content.replace(f'{x}:EN="PER" ', f'____ ')
write_force(
    f"{folder}/02_prettagged.sacr",
    content,
)


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
    r = oai.get(prompt, x['model'])
    write_force(
        f"{folder}/04_{x['i']}.md",
        r['response'],
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
if RUN_OAI_1:
    output = parallel_v4(
        data,
        function_async,
        concurrency = 100,
    )


# 05
sacr_lines = []
for i in range(content_split_len-1):
    content = read(f"{folder}/04_{i}.md")
    yaml_ = yaml.safe_load(content.replace("```yaml", "").replace("```json", "").replace("```", ""))
    sacr_lines.append(yaml_['sacr'][0].replace("{", "{"+f"{i}_"))
write_force(
    f"{folder}/05.sacr",
    "\n".join(sacr_lines) + "\n",
)


def update_count():
    status = "ok"
    lines = []
    c1 = read(f"{folder}/01_gold.sacr").split("\n")
    c5 = read(f"{folder}/05.sacr").split("\n")
    for i in range(content_split_len-1):
        count_1 = c1[i].count("{")
        count_5 = c5[i].count("{")
        if count_1 != count_5:
            status = "error"
        lines.append(f"{i} | {count_5-count_1}")
    write_force(
        f"{folder}/00_counts.md",
        "\n".join(lines),
    )
    return status
status = update_count()
if status != "ok":
    print("error in 00_counts.md")
    exit(1)


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


if RUN_OAI_2:
    print("08 - run ai 2")
    prompt = read(f"{folder}/07.md")
    r = oai.get(prompt, model)
    write_force(
        f"{folder}/08.md",
        r['response'],
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


# run_one(19)

