"""LLM factory for provider switching."""
import logging

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from config import Settings
from core.interfaces import LLMProvider

logger = logging.getLogger(__name__)


class OpenAILLMProvider(LLMProvider):
    """OpenAI-based LLM provider.
    
    Args:
        settings: Validated environment configuration.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._llm: ChatOpenAI | None = None

    def get_llm(self) -> ChatOpenAI:
        """Return OpenAI LLM (lazy-loaded, temperature=0 for RAG).
        
        Temperature 0 → deterministic and strictly factual responses.
        """
        if self._llm is None:
            logger.info("Initializing OpenAI LLM: %s", self._settings.llm_model)
            self._llm = ChatOpenAI(
                model=self._settings.llm_model,
                temperature=0,
                api_key=self._settings.api_key,
            )
        return self._llm


class GroqLLMProvider(LLMProvider):
    """Groq-based LLM provider.
    
    Args:
        settings: Validated environment configuration.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._llm: ChatGroq | None = None

    def get_llm(self) -> ChatGroq:
        """Return Groq LLM (lazy-loaded, temperature=0 for RAG).
        
        Temperature 0 → deterministic and strictly factual responses.
        """
        if self._llm is None:
            logger.info("Initializing Groq LLM: %s", self._settings.llm_model)
            self._llm = ChatGroq(
                model=self._settings.llm_model,
                temperature=0,
                api_key=self._settings.api_key,
            )
        return self._llm


def get_llm_provider(settings: Settings) -> LLMProvider:
    """Factory function to get the correct LLM provider based on configuration."""
    if settings.llm_provider == "groq":
        return GroqLLMProvider(settings)
    elif settings.llm_provider == "openai":
        return OpenAILLMProvider(settings)
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


# Export
__all__ = ["OpenAILLMProvider", "GroqLLMProvider", "get_llm_provider"]
