from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_db_url: str = ""

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Embedding
    embedding_model: str = "openai/text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Paths
    models_config_path: str = "config/models.yaml"
    prompts_dir: str = "config/prompts"
    chunking_config_path: str = "config/chunking.yaml"

    # App
    log_level: str = "INFO"


def load_yaml_config(path: str) -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


settings = Settings()
