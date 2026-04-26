from . import oai 
import json
import os
import pandas
from .io import read, write_force
from .parallel_v4 import parallel_v4, async_wrap
from .logger import logger
from .propp.propp_fr.src.propp_fr.propp_fr_generate_tokens_and_entities_from_sacr import generate_tokens_and_entities_from_sacr
from .propp.propp_fr.src.propp_fr.propp_fr_coreference_resolution_module import (
    initialize_gold_coreference_matrix_from_entities_df,
    coreference_resolution_metrics,
)
import yaml


HOME = os.environ['HOME']
RUN_OAI = True
group_size = 3*30


def function(x):
    r = oai.get(x['content'], x['model'])
    write_force(
        f"{x['path']}.llm.md",
        r['response'],
    )
    return x


@async_wrap
def function_async(x, done_set, total_count):
    return function(x)


def main():
    print("start")
    
    
    # path_main = f"{HOME}/github.com/loicbourgois/em/data/les_fables_de_la_fontaine/02"
    # path_main = f"{HOME}/github.com/loicbourgois/em/data/1823_Duras-Claire-de_Ourika/full"
    path_main = f"{HOME}/github.com/loicbourgois/em/data/1823_Duras-Claire-de_Ourika/half"
    # path_main = f"{HOME}/github.com/loicbourgois/em/data/1823_Duras-Claire-de_Ourika/small"
    # path_main = f"{HOME}/github.com/loicbourgois/em/data/1823_Duras-Claire-de_Ourika/quarter"


    content = read(f"{path_main}/gold/02.sacr")
    for x in reversed(range(100)):
        content = content.replace(f'{x}:EN="PER" ', f'')
    write_force(
        f"{path_main}/gold/02_prettagged.sacr",
        content,
    )

    mode = f"pretagged-relationship-{group_size}"
    # model = "gpt-5.5-low"
    # model = "gpt-5.5-medium"
    model = "gpt-5.5-high"
    # model = "gpt-5.5-low-verbose"
    # model = "gpt-5.5-pro-medium"


    path_main_2 = f"{path_main}/{model}/{mode}"


    content = read(f"{path_main}/gold/02_prettagged.sacr")
    lines = content.split("\n")
    data = []
    stride = int(group_size/3)
    group_i = 0
    for i in range(0, len(lines), stride):
        group = lines[i : i + group_size]
        content = read(f"{HOME}/github.com/loicbourgois/em/template_4.md").format(
            input=json.dumps(group, indent=2, ensure_ascii=False),
        )
        path = f"{path_main_2}/03_{group_i}.md"
        data.append({
            "i": group_i,
            "group": group,
            "path": path,
            "content": content,
            "model": model,
        })
        write_force(
            path,
            content,
        )
        if len(group) < group_size:
            break
        group_i += 1
    

    # raise Exception("wip")


    if RUN_OAI:
        output = parallel_v4(
            data,
            function_async,
            concurrency = 100,
        )


    input_part2 = []
    for x in data:
        txt = read(f"{x['path']}.llm.md")
        yaml_ = yaml.safe_load(txt.replace("```yaml", "").replace("```json", "").replace("```", ""))
        sacr = yaml_['sacr']
        if len(sacr) > 100:
            write_force(
                f"{x['path']}.llm.sacr".replace("03_", "04_"),
                yaml_['sacr'].replace("__PER__", '"PER"') + "\n",
            )
        else:
            write_force(
                f"{x['path']}.llm.sacr".replace("03_", "04_"),
                "\n".join(yaml_['sacr']).replace("__PER__", '"PER"') + "\n",
            )
        write_force(
            f"{x['path']}.llm.json".replace("03_", "05_g_"),
            json.dumps(yaml_['entities'], indent=2) + "\n",
        )
        input_part2.append(
            {
                "entities": {
                    k: v['description']
                    for k, v in yaml_['entities'].items()
                },
                "relationships": yaml_['relationships']
            }
        )
    write_force(
        f"{path_main_2}/06.json",
        json.dumps(input_part2, indent=2, ensure_ascii=False) + "\n",
    )
    write_force(
        f"{path_main_2}/07.md",
        read(f"{HOME}/github.com/loicbourgois/em/template_2.md").format(
            input=read(f"{path_main_2}/06.json")
        )
    )


    # raise Exception("wip")


    if RUN_OAI:
        r = oai.get(read(f"{path_main_2}/07.md"), "gpt-5.5-medium")
        write_force(
            f"{path_main_2}/08.md",
            r['response'],
        )


    txt = read(f"{path_main_2}/08.md",)
    yaml_ = yaml.safe_load(txt.replace("```yaml", "").replace("```json", "").replace("```", ""))
    yaml_['entities_count'] = len(yaml_['groups'])
    write_force(
        f"{path_main_2}/09.json",
        json.dumps(yaml_, indent=2)
    )


    # raise Exception("wip")


    txts = []
    for i, x in enumerate(data):
        path_in = f"{path_main_2}/04_{i}.md.llm.sacr"
        path_out = f"{path_main_2}/10_{i}.md.llm.sacr"
        txt = read(path_in)
        if yaml_.get('reference_to_group'):
            aa = yaml_['reference_to_group']
        else:
            aa = yaml_['reference to group']
        for k, v in aa.items():
            k = k.split(".")[-1]
            txt = txt.replace(f'{k}:EN="PER"', f'{v}:EN="PER"')
        write_force(path_out, txt)
        if i == 0:
            txts.append("\n".join(txt.split("\n")[0:-1]))
        elif i == len(data)-1:
            # txts.append("\n".join(txt.split("\n")[-(stride+2-3):]))
            aa = stride - len(txt.split("\n")) - 1
            txts.append("\n".join(txt.split("\n")[-aa:-1]))
        else:
            # aa = stride - len(txt.split("\n"))
            txts.append("\n".join(txt.split("\n")[-(stride+2):-1]))
    write_force(
        f"{path_main_2}/11.sacr", 
        "".join(txts)
    )


    # raise Exception("wip")


    generate_tokens_and_entities_from_sacr(
        file_name="02.sacr",
        files_directory=f"{path_main}/gold/",
        end_directory=f"{path_main}/gold/",
    )
    gold_df = pandas.read_csv(f"{path_main}/gold/02.sacr.entities", sep='\t')
    gold_coreference_matrix = initialize_gold_coreference_matrix_from_entities_df(gold_df)


    # generate_tokens_and_entities_from_sacr(
    #     file_name="02.sacr",
    #     files_directory=f"{path_main}/gold_bad/",
    #     end_directory=f"{path_main}/gold_bad/",
    # )
    # gold_bad_df = pandas.read_csv(f"{path_main}/gold_bad/02.sacr.entities", sep='\t')
    # gold_bad_coreference_matrix = initialize_gold_coreference_matrix_from_entities_df(gold_bad_df)
    # coreference_metrics_df = coreference_resolution_metrics(
    #     gold_coreference_matrix, 
    #     gold_bad_coreference_matrix,
    # )
    # coreference_metrics_df.to_csv(f"{path_main}/gold_bad/00_result.tsv", sep="\t")


    silver_name = f"11.sacr"
    generate_tokens_and_entities_from_sacr(
        file_name=silver_name,
        files_directory=f"{path_main_2}",
    )
    silver_df = pandas.read_csv(f"{path_main_2}/{silver_name}.entities", sep='\t')
    silver_coreference_matrix = initialize_gold_coreference_matrix_from_entities_df(silver_df)
    coreference_metrics_df = coreference_resolution_metrics(
        gold_coreference_matrix, 
        silver_coreference_matrix,
    )
    coreference_metrics_df.to_csv(f"{path_main_2}/00_result.tsv", sep="\t")


if __name__ == '__main__':
    main()
