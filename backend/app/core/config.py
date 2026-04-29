from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int
    algorithm: str = "HS256"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    firebase_service_account_path: str | None = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    @field_validator("gemini_api_key", "firebase_service_account_path", mode="before")
    @classmethod
    def _strip_optional_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

settings = Settings()
