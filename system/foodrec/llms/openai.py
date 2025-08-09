# 13.06.2025 @Noah Meissner

"""
Request OpenAI API
"""

from loguru import logger
from langchain_openai import ChatOpenAI, OpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv
import os


from foodrec.llms.basellm import BaseLLM

class AnyOpenAILLM(BaseLLM):
    def __init__(self, model_name: str = 'o4-mini-2025-04-16', json_mode: bool = False, *args, **kwargs):
        """Initialize the OpenAI LLM.

        Args:
            `model_name` (`str`, optional): The name of the OpenAI model. Defaults to `gpt-3.5-turbo`.
            `json_mode` (`bool`, optional): Whether to use the JSON mode of the OpenAI API. Defaults to `False`.
        """
        self.model_name = model_name
        self.json_mode = json_mode
        load_dotenv() 
        api_key = os.getenv("OPENAI") 
        if api_key is None:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        kwargs['api_key'] = api_key


        if json_mode and self.model_name not in ['o4-mini-2025-04-16']:
            raise ValueError("json_mode is only available for o4-mini-2025-04-16")
        self.max_tokens: int = kwargs.get('max_tokens', 256)
        self.max_context_length: int = 16384 if '16k' in model_name else 32768 if '32k' in model_name else 4096
        if model_name.split('-')[0] == 'text' or model_name == 'gpt-3.5-turbo-instruct':
            self.model = OpenAI(model_name=model_name, *args, **kwargs)
            self.model_type = 'completion'
        else:
            if json_mode:
                logger.info("Using JSON mode of OpenAI API.")
                if 'model_kwargs' in kwargs:
                    kwargs['model_kwargs']['response_format'] = {
                        "type": "json_object"
                    }
                else:
                    kwargs['model_kwargs'] = {
                        "response_format": {
                            "type": "json_object"
                        }
                    }
            self.model = ChatOpenAI(model_name=model_name, *args, **kwargs)
            self.model_type = 'chat'

    def __call__(self, prompt: str, *args, **kwargs) -> str:
        """Forward pass of the OpenAI LLM.

        Args:
            `prompt` (`str`): The prompt to feed into the LLM.
        Returns:
            `str`: The OpenAI LLM output.
        """
        if self.model_type == 'completion':
            return self.model.invoke(prompt).content.replace('\n', ' ').strip()
        else:
            return self.model.invoke(
                [
                    HumanMessage(
                        content=prompt,
                    )
                ]
            ).content.replace('\n', ' ').strip()
