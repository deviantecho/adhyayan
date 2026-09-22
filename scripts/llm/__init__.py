"""
LLM Provider abstraction layer for Adhyayan.

Supports multiple LLM backends:
- Gemini (production)
- OmniRoute (local development)
"""

from .provider import LLMProvider
from .gemini_provider import GeminiProvider
from .omniroute_provider import OmniRouteProvider

__all__ = ['LLMProvider', 'GeminiProvider', 'OmniRouteProvider', 'get_provider']


def get_provider() -> LLMProvider:
    """
    Factory function to get the configured LLM provider.

    Returns the provider based on LLM_PROVIDER environment variable:
    - "gemini" -> GeminiProvider (production)
    - "omniroute" -> OmniRouteProvider (local development)

    Raises:
        ValueError: If LLM_PROVIDER is not set or invalid
        RuntimeError: If required configuration is missing
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    provider_name = os.getenv("LLM_PROVIDER", "").lower()

    if not provider_name:
        raise ValueError(
            "LLM_PROVIDER environment variable not set. "
            "Set to 'gemini' or 'omniroute'."
        )

    if provider_name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable not set")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        return GeminiProvider(api_key=api_key, model=model)

    elif provider_name == "omniroute":
        base_url = os.getenv("OMNIROUTE_BASE_URL", "http://127.0.0.1:20128/v1")
        api_key = os.getenv("OMNIROUTE_API_KEY", "")
        model = os.getenv("OMNIROUTE_MODEL")

        if not model:
            raise RuntimeError(
                "OMNIROUTE_MODEL environment variable not set. "
                "Specify the model configured in OmniRoute."
            )

        return OmniRouteProvider(
            base_url=base_url,
            api_key=api_key,
            model=model
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider_name}'. "
            f"Supported providers: 'gemini', 'omniroute'"
        )
