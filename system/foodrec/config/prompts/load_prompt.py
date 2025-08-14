# Noah Meißner 06.08.2025

from enum import Enum
from foodrec.config.structure.paths import AGENT_PROMPTS_BIASED, AGENT_PROMPTS_UNBIASED

class PromptEnum(Enum):
    REFLECTOR = "reflector.txt"
    ITEM_ANALYST = "item_analyst.txt"
    SEARCH = "search.txt"
    THOUGHT = "manager_thought.txt"
    ACTION = "manager_action.txt"
    INTERPRETER = "interpreter.txt"
    SEARCH_AGAIN = "search_again.txt"

    


def get_base_prompt(filename: str, biased: bool) -> str:
    base = AGENT_PROMPTS_BIASED if biased else AGENT_PROMPTS_UNBIASED
    path = base / filename
    with open(path, "r") as file:
        return file.read()


PROMPTS = {prompt: get_base_prompt(prompt.value, biased=False) for prompt in PromptEnum}
BIASED_PROMPTS = {prompt: get_base_prompt(prompt.value, biased=True) for prompt in PromptEnum}


def get_prompt(prompt_name: PromptEnum, biased: bool = False) -> str:
    return BIASED_PROMPTS[prompt_name] if biased else PROMPTS[prompt_name]
