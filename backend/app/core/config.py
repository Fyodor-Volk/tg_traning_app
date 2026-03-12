from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Fitness Training Diary API"
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    debug: bool = Field(default=True, validation_alias="DEBUG")

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/fitness_diary",
        validation_alias="DATABASE_URL",
    )

    telegram_bot_token: str = Field(default="CHANGE_ME", validation_alias="TELEGRAM_BOT_TOKEN")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

