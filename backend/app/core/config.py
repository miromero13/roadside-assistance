from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int
    algorithm: str = "HS256"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"
settings = Settings()
