"""
Abstract base class for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Iterator


class LLMProvider(ABC):
    """
    Abstract interface for LLM providers.

    All providers must support both normal and streaming generation.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a complete response from the LLM.

        Args:
            prompt: The prompt text

        Returns:
            Complete generated text

        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    def generate_stream(self, prompt: str) -> Iterator[str]:
        """
        Generate a streaming response from the LLM.

        Yields text chunks as they are generated.
        This must be TRUE streaming, not simulated by splitting
        a completed response.

        Args:
            prompt: The prompt text

        Yields:
            Text chunks as they are generated

        Raises:
            Exception: If generation fails
        """
        pass
