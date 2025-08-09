# 13.06.2025 @Noah Meissner

"""
This file tests if the llms are working correctly
"""

import os
from foodrec.llms.gemini import AnyGeminiLLM  
from foodrec.llms.openai import AnyOpenAILLM
from dotenv import load_dotenv


def test_any_gemini_llm():
    if "GOOGLE_API_KEY" not in os.environ:
        load_dotenv()
        os.environ["GOOGLE_API_KEY"] = os.getenv('GEMINI')

    llm = AnyGeminiLLM()

    prompt = "Erkläre kurz den Unterschied zwischen KI und Machine Learning."

    output = llm(prompt)

    print("Antwort des Modells:", output)

def test_openai_llm():
    if "OPENAI_API_KEY" not in os.environ:
        load_dotenv()
        os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI')

    llm = AnyOpenAILLM()

    prompt = "Erkläre kurz den Unterschied zwischen KI und Machine Learning."

    output = llm(prompt)

    print("Antwort des Modells:", output)

