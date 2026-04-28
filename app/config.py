from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    llm_provider: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    
    current_user_id: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()