import json
from openai import OpenAI
from datetime import datetime, timezone
import os
from .io import read


HOME = os.environ['HOME']


secrets = json.loads(read(f"{HOME}/github.com/loicbourgois/em/secrets.json"))
oai_secrets = json.loads(read(secrets['openai_path'].format(HOME=HOME)))
client = OpenAI(
    api_key=oai_secrets['code_review'],
)


# https://platform.openai.com/docs/pricing?latest-pricing=standard
million = 1000000.0
pricing = {
    "2026-02-26": {
        "text": {
            "default": {
                "gpt-4.1-mini": {
                    "input": 0.40 / million,
                    "input_cached": 0.10 / million,
                    "output": 1.60 / million,
                },
                "gpt-4.1": {
                    "input": 2.00 / million,
                    "input_cached": 0.50 / million,
                    "output": 8.00 / million,
                },
                "gpt-5-chat-latest": {
                    "input": 1.25 / million,
                    "input_cached": 0.125 / million,
                    "output": 10.00 / million,
                },
                "gpt-5.1-chat-latest": {
                    "input": 1.25 / million,
                    "input_cached": 0.125 / million,
                    "output": 10.00 / million,
                },
                "gpt-5-nano": {
                    "input": 0.05 / million,
                    "input_cached": 0.005 / million,
                    "output": 0.40 / million,
                },
                "gpt-5-mini": {
                    "input": 0.25 / million,
                    "input_cached": 0.025 / million,
                    "output": 2.00 / million,
                },
                "gpt-5.3-codex": {
                    "input": 1.75 / million,
                    "input_cached": 0.175 / million,
                    "output": 14.00 / million,
                },
                "gpt-5.5": {
                    "input": 1.75 / million,
                    "input_cached": 0.175 / million,
                    "output": 14.00 / million,
                },
            },
        }
    }
}


def get_reasoning(prompt, model, effort):
    return client.responses.create(
        model=model,
        input=[
            {"role": "user", "content": prompt},
        ],
        text={"format": {"type": "text"}, "verbosity": "medium"},
        reasoning={"effort": effort, "summary": "auto"},
    )


def get_reasoning_web_search(prompt, model, effort):
    return client.responses.create(
        model=model,
        input=[
            {"role": "user", "content": prompt},
        ],
        text={"format": {"type": "text"}, "verbosity": "medium"},
        reasoning={"effort": effort, "summary": "auto"},
        tools=[
            {
                "type": "web_search",
                # "user_location": {
                #     "type": "approximate"
                # },
                # "search_context_size": "medium"
            }
        ],
        include=[
            "web_search_call.action.sources",
        ],
    )


def get_default(prompt, model, max_output_tokens):
    return client.responses.create(
        model=model,
        input=[
            {"role": "user", "content": prompt},
        ],
        text={},
        reasoning={},
        tools=[],
        temperature=1,
        top_p=1,
        store=True,
        max_output_tokens=max_output_tokens,
    )


def get_structured(prompt, model, response_format):
    """
    Get structured output using a Pydantic model.

    Args:
        prompt: The prompt text
        model: Model name (must be in default_models list)
        response_format: Pydantic model class defining the expected response structure

    Returns:
        Tuple of (parsed_response, cost_estimate) where parsed_response is an
        instance of the response_format class
    """
    r = client.responses.parse(
        model=model,
        input=[
            {"role": "user", "content": prompt},
        ],
        text_format=response_format,
        temperature=1,
        top_p=1,
        store=True,
    )
    pricing_detail = pricing["2026-02-26"]["text"][r.service_tier][model]
    parsed = r.output_parsed
    cost_estimate = (
        r.usage.input_tokens * pricing_detail["input"]
        + r.usage.output_tokens * pricing_detail["output"]
    )
    return parsed, cost_estimate


def get(prompt, model, max_output_tokens=None):
    start_utc = datetime.now(timezone.utc)
    default_models = [
        "gpt-5-chat-latest",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-5.1-chat-latest",
    ]
    if max_output_tokens is not None and model not in default_models:
        raise Exception("invalid args")
    if model == "gpt-5-mini-minimal":
        r = get_reasoning(prompt, "gpt-5-mini", "minimal")
        pricing_model = "gpt-5-mini"
    elif model == "gpt-5-mini-low":
        r = get_reasoning(prompt, "gpt-5-mini", "low")
        pricing_model = "gpt-5-mini"
    elif model == "gpt-5-mini-medium":
        r = get_reasoning(prompt, "gpt-5-mini", "medium")
        pricing_model = "gpt-5-mini"
    elif model == "gpt-5-mini-high":
        r = get_reasoning(prompt, "gpt-5-mini", "high")
        pricing_model = "gpt-5-mini"
    elif model == "gpt-5-nano-minimal":
        r = get_reasoning(prompt, "gpt-5-nano", "minimal")
        pricing_model = "gpt-5-nano"
    elif model == "gpt-5-nano-low":
        r = get_reasoning(prompt, "gpt-5-nano", "low")
        pricing_model = "gpt-5-nano"
    elif model == "gpt-5-nano-medium":
        r = get_reasoning(prompt, "gpt-5-nano", "medium")
        pricing_model = "gpt-5-nano"
    elif model == "gpt-5-nano-high":
        r = get_reasoning(prompt, "gpt-5-nano", "high")
        pricing_model = "gpt-5-nano"
    elif model == "gpt-5-mini-low-with-internet":
        pricing_model = "gpt-5-mini"
        r = get_reasoning_web_search(prompt, pricing_model, "low")
    elif model == "gpt-5-mini-medium-with-internet":
        pricing_model = "gpt-5-mini"
        r = get_reasoning_web_search(prompt, pricing_model, "medium")
    elif model in default_models:
        r = get_default(prompt, model, max_output_tokens)
        pricing_model = model
    elif model in ["gpt-5.3-codex"]:
        r = client.responses.create(
            model=model,
            input=[
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
            temperature=0,
        )
        pricing_model = model
    elif model in ["gpt-5.5-low"]:
        r = client.responses.create(
            model="gpt-5.5",
            input=[
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
            reasoning ={"effort": "low"},
            store=False,
        )
        pricing_model = model
    elif model in ["gpt-5.5-low-verbose"]:
        r = client.responses.create(
            model="gpt-5.5",
            input=[
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
            reasoning ={"effort": "low"},
            text={
                "verbosity": "high"
            },
            store=False,
        )
        pricing_model = model
    elif model in ["gpt-5.5-medium"]:
        r = client.responses.create(
            model="gpt-5.5",
            input=[
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
            reasoning ={"effort": "medium"},
            store=False,
        )
        pricing_model = model
    elif model in ["gpt-5.5-high"]:
        r = client.responses.create(
            model="gpt-5.5",
            input=[
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
            reasoning ={"effort": "high"},
            store=False,
        )
        pricing_model = model
    elif model in ["gpt-5.5-pro-medium"]:
        r = client.responses.create(
            model="gpt-5.5-pro",
            input=[
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
            reasoning ={"effort": "medium"},
            store=False,
        )
        pricing_model = model
    else:
        raise Exception(f"invalid model: {model}")
    text = r.output[-1].content[-1].text
    try:
        print(r.usage)
        pricing_detail = pricing["2026-02-26"]["text"][r.service_tier][pricing_model]
        cost_estimate = (
            r.usage.input_tokens * pricing_detail["input"]
            + r.usage.output_tokens * pricing_detail["output"]
        )
    except:
        cost_estimate = None
    end_utc = datetime.now(timezone.utc)
    return {
        "response": text,
        "cost_estimate": cost_estimate,
        "duration": str(end_utc - start_utc),
        "start_utc": str(start_utc),
        "end_utc": str(end_utc),
    }
