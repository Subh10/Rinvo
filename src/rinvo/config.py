"""Environment-backed settings for Rinvo."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RINVO_", env_file=".env", extra="ignore")

    backend: str = "mock"
    model_id: str = "chatterbox-turbo"
    device: str = "auto"
    max_text_chars: int = 5000
    host: str = "127.0.0.1"
    port: int = 8000


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
