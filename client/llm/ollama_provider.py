from typing import Any

import ollama

from app.config import get_settings
from client.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama provider supporting local and cloud modes."""

    def __init__(self) -> None:
        settings = get_settings()

        self.mode = settings.ollama_mode.lower().strip()
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.api_key = settings.ollama_api_key.strip()

        if self.mode not in {"local", "cloud"}:
            raise ValueError(
                f"Invalid OLLAMA_MODE='{self.mode}'. "
                "Expected 'local' or 'cloud'."
            )

        if self.mode == "local" and "ollama.com" in self.base_url:
            raise ValueError(
                "Invalid config: OLLAMA_MODE=local cannot use ollama.com. "
                "Check OLLAMA_LOCAL_BASE_URL."
            )

        if self.mode == "cloud":
            if "localhost" in self.base_url or "127.0.0.1" in self.base_url:
                raise ValueError(
                    "Invalid config: OLLAMA_MODE=cloud cannot use localhost. "
                    "Check OLLAMA_CLOUD_BASE_URL."
                )

            if not self.api_key:
                raise ValueError(
                    "OLLAMA_API_KEY is required when OLLAMA_MODE=cloud."
                )

        headers: dict[str, str] = {}

        if self.mode == "cloud":
            headers["Authorization"] = f"Bearer {self.api_key}"

        self.client = ollama.Client(
            host=self.base_url,
            headers=headers or None,
        )

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            kwargs["tools"] = tools

        response = self.client.chat(**kwargs)
        return dict(response)