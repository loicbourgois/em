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


HOME = os.environ['HOME']


def function(x):
    r = oai.get(x['content'], x['model'])
    write_force(
        f"{x['path']}.{x['model']}.md",
        r['response'],
    )
    return x


@async_wrap
def function_async(x, done_set, total_count):
    return function(x)


def main():
    print("wip")
    path_main = f"{HOME}/github.com/loicbourgois/em/corbeau_renard/corbeau_renard.txt"
    # path = f"{HOME}/github.com/loicbourgois/em/1923_Delly_Dans-les-ruines/1923_Delly_Dans-les-ruines.md"
    content = read(path_main)
    lines = content.split("\n")
    # lines = lines[0:20]
    groups = []
    group_size = 3*15
    stride = int(group_size/3)
    group_i = 0
    for i in range(0, len(lines), stride):
        group = lines[i : i + group_size]
        content = read(f"{HOME}/github.com/loicbourgois/em/template.md").format(
            input="\n".join(group)
        )
        path = "/".join(path_main.split("/")[0:-1]) + f"/split/{group_i}.md"
        groups.append({
            "i": group_i,
            "group": group,
            "path": path,
            "content": content,
        })
        write_force(
            path,
            content,
        )
        if len(group) < group_size:
            break
        group_i += 1
    logger.info(f"groups: {len(groups)}")
    models = [
        "gpt-5-chat-latest",
        "gpt-5.3-codex",
        # "gpt-5.5-high", # ~3mins per group
        "gpt-5.5-low",
        "gpt-5.5-medium",
    ]
    data = []
    for group in groups:
        for model in models:
            data.append({
                "model": model,
                **group,
            })
    output = parallel_v4(
        data,
        function_async,
        concurrency = 100,
    )
    for x in data:
        print(x)
        txt = read(f"{x['path']}.{x['model']}.md")
        json_ = json.loads(txt.replace("```yaml", "").replace("```", ""))
        write_force(
            f"{x['path']}.{x['model']}.sacr",
            "\n".join(json_['sacr']).replace("__PER__", '"PER"') + "\n",
        )
    
    # logger.info("generate_tokens_and_entities_from_sacr - gold")
    # generate_tokens_and_entities_from_sacr(
    #     file_name="corbeau_renard.sacr",
    #     files_directory=f"{HOME}/github.com/loicbourgois/em/corbeau_renard/",
    #     end_directory=f"{HOME}/github.com/loicbourgois/em/corbeau_renard/gold/",
    # )
    gold_df = pandas.read_csv(f"{HOME}/github.com/loicbourgois/em/corbeau_renard/gold/corbeau_renard.sacr.entities", sep='\t')
    gold_coreference_matrix = initialize_gold_coreference_matrix_from_entities_df(gold_df)


    for model in models:
        logger.info("generate_tokens_and_entities_from_sacr - silver")
        silver_name = f"0.md.{model}.sacr"
        generate_tokens_and_entities_from_sacr(
            # file_name="0.md.gpt-5.3-codex.sacr",
            file_name=silver_name,
            files_directory=f"{HOME}/github.com/loicbourgois/em/corbeau_renard/split/",
            end_directory=f"{HOME}/github.com/loicbourgois/em/corbeau_renard/silver/",
        )
        logger.info("score")
        silver_df = pandas.read_csv(f"{HOME}/github.com/loicbourgois/em/corbeau_renard/silver/{silver_name}.entities", sep='\t')
        silver_coreference_matrix = initialize_gold_coreference_matrix_from_entities_df(silver_df)
        coreference_metrics_df = coreference_resolution_metrics(gold_coreference_matrix, silver_coreference_matrix)


if __name__ == '__main__':
    main()
