from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Base interface for all LLM providers."""

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send chat messages to the LLM and return a normalized response."""
        raise NotImplementedError