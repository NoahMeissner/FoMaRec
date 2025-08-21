# Noah Meissner 26.07.2025

from enum import Enum

class DatasetEnum(Enum):
    ALL_RECIPE = 1
    KOCHBAR = 2

class ModelEnum(Enum):
    OpenAI = 1
    Gemini = 2
    LLAMA = 3
    GEMMA = 4
    DeepSeek = 5
    GPT_OPEN_SOURCE = 6

