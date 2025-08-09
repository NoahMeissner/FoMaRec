# Noah Meißner 06.08.2025

from enum import Enum
from foodrec.config.structure.paths import AGENT_PROMPTS

class PromptEnum(Enum):
    REFLECTOR = "reflector.txt"
    ITEM_ANALYST = "item_analyst.txt"
    SEARCH = "search.txt"
    MANAGER = "manager.txt"
    INTERPRETER = "interpreter.txt"

    def biased_filename(self):
        return self.value.replace(".txt", "_biased.txt")


def get_base_prompt(filename: str) -> str:
    path = AGENT_PROMPTS / filename
    with open(path, "r") as file:
        return file.read()


PROMPTS = {prompt: get_base_prompt(prompt.value) for prompt in PromptEnum}
BIASED_PROMPTS = {prompt: get_base_prompt(prompt.biased_filename()) for prompt in PromptEnum}


def get_prompt(prompt_name: PromptEnum, biased: bool = False) -> str:
    return BIASED_PROMPTS[prompt_name] if biased else PROMPTS[prompt_name]
