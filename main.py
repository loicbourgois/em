from . import oai 
import json
import os
from .io import read, write_force
from .parallel_v4 import parallel_v4, async_wrap


HOME = os.environ['HOME']


def function(x):
    r = oai.get(x['content'], x['model'])
    write_force(
        f"{HOME}/github.com/loicbourgois/em/1923_Delly_Dans-les-ruines/split/{x['i']}.md.{x['model']}.md",
        r['response'],
    )


@async_wrap
def function_async(x, done_set, total_count):
    return function(x)


def main():
    print("wip")
    content = read(f"{HOME}/github.com/loicbourgois/em/1923_Delly_Dans-les-ruines/1923_Delly_Dans-les-ruines.md")
    lines = content.split("\n\n")
    lines = lines[0:20]
    # print(json.dumps(lines, indent=2, ensure_ascii=False))
    # todo: split into groups
        # lines[0:8], lines[4:12], ... 
        # params should be 
        #   - group size, here 8
        #   - ___, here 4
    groups = []
    group_size = 9
    stride = int(group_size/3)
    group_i = 0
    for i in range(0, len(lines), stride):
        group = lines[i : i + group_size]
        content = read(f"{HOME}/github.com/loicbourgois/em/template.md").format(
            input="\n\n".join(group)
        )
        path = f"{HOME}/github.com/loicbourgois/em/1923_Delly_Dans-les-ruines/split/{group_i}.md"
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
    models = [
        "gpt-5.5-high", # ~3mins per group
        "gpt-5.5-medium",
        "gpt-5.5-low",
        "gpt-5-chat-latest",
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


if __name__ == '__main__':
    main()
