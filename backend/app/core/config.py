from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "sqlite+aiosqlite:///./clinready.db"
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    GOOGLE_CANCEL_MODE: str = "soft"  # "delete" | "soft"

    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

    FRONTEND_URL: str = "http://localhost:5173"
    LOG_LEVEL: str = "INFO"


settings = Settings()
