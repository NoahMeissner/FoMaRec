# Noah Meißner 06.08.2025

"""
    This Method should overhand the right model, depending which LLM you need
"""

from foodrec.llms.gemini import AnyGeminiLLM
from foodrec.llms.open_source import OpenSource
from foodrec.llms.openai import OpenAI
from foodrec.config.structure.dataset_enum import ModelEnum

def _get_gemini():
    model = AnyGeminiLLM()
    return model

def _get_gpt_4omini():
    model = OpenAI()
    return model

def _get_llama3():
    model = OpenSource(model_name="llama-3.3-70b-instruct")
    return model

def get_model(model_name: ModelEnum):
    if model_name == ModelEnum.Gemini:
        return _get_gemini()
    if model_name == ModelEnum.OpenAI:
        return _get_gpt_4omini
    if model_name == ModelEnum.LLAMA:
        return _get_llama3()