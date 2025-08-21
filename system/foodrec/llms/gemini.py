from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv
import os


from foodrec.llms.basellm import BaseLLM

class AnyGeminiLLM(BaseLLM):
    def __init__(self, model_name: str = 'gemini-2.5-pro', *args, **kwargs):
        """Initialize the Gemini LLM.
gemini-2.5-pro
        'gemini-2.0-flash'
        Args:
            model_name (str, optional): The name of the Gemini model. Defaults to 'gemini-2.0-flash'.
        """
        load_dotenv()
        api_key = os.getenv("GEMINI")

        self.model_name = model_name
        self.max_tokens: int = kwargs.get('max_tokens', 256)
        # Kontextlänge ist je nach Gemini-Modell unterschiedlich, hier exemplarisch
        self.max_context_length: int = 16384 if '16k' in model_name else 32768 if '32k' in model_name else 8192

        self.model = ChatGoogleGenerativeAI(model=model_name,google_api_key=api_key, *args, **kwargs)
        self.model_type = 'chat'

    def __call__(self, prompt: str, *args, **kwargs) -> str:
        """Forward pass of the Gemini LLM.

        Args:
            prompt (str): The prompt to feed into the LLM.

        Returns:
            str: The Gemini LLM output.
        """
        # Gemini erwartet eine Liste von Nachrichten im Chat-Format
        response = self.model.invoke(
            [
                HumanMessage(content=prompt)
            ]
        )
        # Antworttext bereinigen und zurückgeben
        return response.content.replace('\n', ' ').strip()
