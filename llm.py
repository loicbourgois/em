from .gemma4.get import gemma4_get
from . import oai


def get(prompt, model):
    if model in ("google/gemma-4-E4B-it", "google/gemma-4-31B-it"):
        return gemma4_get(prompt, model)
    else:
        return oai.get(prompt, model)['response']
