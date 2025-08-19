from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """
    Application settings loaded from environment variables.

    Note:
        Do not read .env directly. Orchestrator sets environment variables.
        You may use the accompanying .env.example as a reference for required variables.
    """
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    CORS_ALLOW_ORIGINS: str

    # Execution sandbox limits
    EXEC_TIMEOUT_SECONDS: int
    EXEC_MEMORY_MB: int

    # Hashing/JWT parameters
    JWT_ALGORITHM: str = "HS256"


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return application settings loaded from environment variables with safe defaults."""
    return Settings(
        SECRET_KEY=os.getenv("SECRET_KEY", "change-me-in-production"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./app.db"),
        CORS_ALLOW_ORIGINS=os.getenv("CORS_ALLOW_ORIGINS", "*"),
        EXEC_TIMEOUT_SECONDS=int(os.getenv("EXEC_TIMEOUT_SECONDS", "2")),
        EXEC_MEMORY_MB=int(os.getenv("EXEC_MEMORY_MB", "128")),
    )
