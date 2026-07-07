from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Tiktok AI Product Selection Backend"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://radar:radar@localhost:5432/ai_product_radar"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_prefix="BACKEND_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
