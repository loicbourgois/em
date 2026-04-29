import requests
import json


def gemma4_get(prompt, model):
    url = {
        "google/gemma-4-E4B-it": "http://localhost:9090/v1/chat/completions",
        "google/gemma-4-31B-it": "http://localhost:9091/v1/chat/completions",
    }[model]
    r = requests.post(
        url = url,
        json = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "chat_template_kwargs": {
                "enable_thinking": True
            },
            "skip_special_tokens": False
        }
    )
    print(r)
    return r.json()['choices'][0]['message']["content"]
