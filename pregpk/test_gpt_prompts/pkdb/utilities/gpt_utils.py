import os
import tiktoken
from openai import OpenAI


def num_tokens_from_string(string: str, gpt_model: str="gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(gpt_model)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def num_tokens_from_list(obj, gpt_model:str):
    # TODO: maybe add functionality for nested lists through recursion
    return [num_tokens_from_string(i, gpt_model) for i in obj]


def cost_per_token(gpt_version:str, output:bool=False) -> float:

    if gpt_version == 'gpt-4':
        if output:
            return 60./1e6
        else:
            return 30./1e6

    if gpt_version == 'gpt-4-0125-preview' or gpt_version == 'gpt-4-1106-preview':
        if output:
            return 30./1e6
        else:
            return 10./1e6

    if gpt_version == 'gpt-3.5-turbo-0125':
        if output:
            return 1.5/1e6
        else:
            return 0.5/1e6

    return float('inf')

