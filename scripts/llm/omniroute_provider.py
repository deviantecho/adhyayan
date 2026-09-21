"""
OmniRoute LLM provider implementation.

Uses OpenAI-compatible API for local model access.
"""

from typing import Iterator
from openai import OpenAI
from .provider import LLMProvider


class OmniRouteProvider(LLMProvider):
    """
    OmniRoute provider using OpenAI-compatible API.

    Connects to a local OmniRoute instance at http://127.0.0.1:20128/v1
    and routes to the configured model.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:20128/v1",
        api_key: str = "",
        model: str = "default"
    ):
        """
        Initialize OmniRoute provider.

        Args:
            base_url: OmniRoute base URL (default: http://127.0.0.1:20128/v1)
            api_key: API key (optional for local OmniRoute)
            model: Model identifier configured in OmniRoute
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key or "not-needed"
        )
        self.model = model

    def generate(self, prompt: str) -> str:
        """
        Generate a complete response using OmniRoute.

        Args:
            prompt: The prompt text

        Returns:
            Complete generated text

        Raises:
            Exception: If OmniRoute API call fails
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def generate_stream(self, prompt: str) -> Iterator[str]:
        """
        Generate a streaming response using OmniRoute.

        Uses OpenAI-compatible streaming API for true token-by-token streaming.

        Args:
            prompt: The prompt text

        Yields:
            Text chunks as they are generated

        Raises:
            Exception: If OmniRoute API call fails
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
