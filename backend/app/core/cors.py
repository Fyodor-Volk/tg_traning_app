from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CorsSettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:8080"])

