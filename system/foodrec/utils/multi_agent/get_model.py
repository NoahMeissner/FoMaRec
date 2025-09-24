# Noah Meißner 06.08.2025

"""
    This Method should overhand the right model, depending which LLM you need
"""

from foodrec.llms.gemini import AnyGeminiLLM
from foodrec.llms.open_source import OpenSource
from foodrec.llms.openai import AnyOpenAILLM
from foodrec.config.structure.dataset_enum import ModelEnum

def _get_gemini(test):
    model = AnyGeminiLLM(test=test)
    return model

def _get_gpt_4omini(test):
    model = AnyOpenAILLM(test=test)
    return model

def get_gemini_pro(test):
    model = AnyGeminiLLM(model_name="gemini-2.5-pro", test=test)
    return model

def get_deepseek(test):
    model = OpenSource(model_name="deepseek-r1", test=test)
    return model
def get_gpt_open_source(test):
    model = OpenSource(model_name="openai-gpt-oss-120b", test=test)
    return model



def get_model(model_name: ModelEnum, test=False):
    if model_name == ModelEnum.Gemini:
        return _get_gemini(test)
    if model_name == ModelEnum.OpenAI:
        return _get_gpt_4omini(test)
    if model_name == ModelEnum.GEMINIPRO:
        return get_gemini_pro(test)
    if model_name == ModelEnum.DeepSeek:
        return get_deepseek(test)
    if model_name == ModelEnum.GPT_OPEN_SOURCE:
        return get_gpt_open_source(test)
