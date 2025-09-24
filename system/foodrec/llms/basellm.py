# 13.06.2025 @Noah Meissner

"""
Base LLM how we define it
"""
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    def __init__(self) -> None:
        self.model_name: str
        self.max_tokens: int
        self.max_context_length: int
        self.json_mode: bool

    @property
    def tokens_limit(self) -> int:
        """Limit of tokens that can be fed into the LLM under the current context length.

        Returns:
            `int`: The limit of tokens that can be fed into the LLM under the current context length.
        """
        return self.max_context_length - 2 * self.max_tokens - 50

    @abstractmethod
    def __call__(self, prompt: str, *args, **kwargs) -> str:
        """Forward pass of the LLM.

        Args:
            `prompt` (`str`): The prompt to feed into the LLM.
        Raises:
            `NotImplementedError`: Should be implemented in subclasses.
        Returns:
            `str`: The LLM output.
        """
        raise NotImplementedError("BaseLLM.__call__() not implemented")

