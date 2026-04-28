from app.config import get_settings
from client.llm.base import LLMProvider
from client.llm.ollama_provider import OllamaProvider
#from client.llm.anthropic_provider import AnthropicProvider
#from client.llm.openai_provider import OpenAIProvider

def create_llm_provider() -> LLMProvider:
    settings = get_settings()

    provider = settings.llm_provider.lower().strip()

    if provider == "ollama":
        return OllamaProvider()

    raise ValueError(
        f"Unsupported LLM_PROVIDER='{settings.llm_provider}'. "
        "Currently supported: ollama"
    )