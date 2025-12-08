"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///./data/ytdownloader.db"

    # Huey Task Queue
    HUEY_DB: str = "./data/huey.db"

    # Download Configuration
    DOWNLOAD_DIR: str = "./downloads"

    # API Configuration
    API_PORT: int = 8000
    DEBUG: bool = False

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,chrome-extension://*"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def ensure_directories(self):
        """Create required directories if they don't exist."""
        Path(self.DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.HUEY_DB).parent.mkdir(parents=True, exist_ok=True)
        Path(self.DATABASE_URL.replace("sqlite:///", "")).parent.mkdir(
            parents=True, exist_ok=True
        )


# Global settings instance
settings = Settings()
