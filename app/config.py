from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"

    mysql_host: str = "localhost"
    mysql_port: int = 3307
    mysql_database: str = "supportops"
    mysql_user: str = "supportops_user"
    mysql_password: str = "supportops_password"

    internal_api_base_url: str = "http://localhost:8001"

    mcp_server_host: str = "127.0.0.1"
    mcp_server_port: int = 8000

    current_user_id: int = 1

    llm_provider: str = "ollama"

    ollama_mode: str = "local"

    ollama_local_base_url: str = "http://localhost:11434"
    ollama_local_model: str = "qwen2.5:7b"

    ollama_cloud_base_url: str = "https://ollama.com"
    ollama_cloud_model: str = "qwen3.5:397b-cloud"
    ollama_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def ollama_base_url(self) -> str:
        if self.ollama_mode == "local":
            return self.ollama_local_base_url

        if self.ollama_mode == "cloud":
            return self.ollama_cloud_base_url

        raise ValueError(
            f"Invalid OLLAMA_MODE='{self.ollama_mode}'. "
            "Expected 'local' or 'cloud'."
        )

    @property
    def ollama_model(self) -> str:
        if self.ollama_mode == "local":
            return self.ollama_local_model

        if self.ollama_mode == "cloud":
            return self.ollama_cloud_model

        raise ValueError(
            f"Invalid OLLAMA_MODE='{self.ollama_mode}'. "
            "Expected 'local' or 'cloud'."
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()