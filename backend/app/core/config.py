from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DocuLens"
    api_prefix: str = ""
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/documents"
    )
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    upload_dir: Path = Path("uploads")
    max_upload_bytes: int = 15 * 1024 * 1024
    chroma_host: str | None = None
    chroma_port: int = 8000
    chroma_persist_dir: Path = Path(".chroma")
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    request_limit_per_minute: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings
