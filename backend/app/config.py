from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'  # Ekstra alanları yoksay
    )

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/dropspot"

    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Seed configuration
    project_seed: str = "567298819101"
    seed_a: int = 8
    seed_b: int = 15
    seed_c: int = 5


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
