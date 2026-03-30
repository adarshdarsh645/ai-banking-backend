from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ───────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/ai_banking"
    )

    # ── JWT ───────────────────────────────────────────────────
    SECRET_KEY: str = "super-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── App ───────────────────────────────────────────────────
    PROJECT_NAME: str = "AI Banking"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # ── CORS ──────────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: list[str] = ["*"]


settings = Settings()
