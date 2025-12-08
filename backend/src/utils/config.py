"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///D:/DEV/yt-download-full-stack/data/ytdownloader.db"

    # Huey Task Queue
    HUEY_DB: str = "D:/DEV/yt-download-full-stack/data/huey.db"

    # Download Configuration
    DOWNLOAD_DIR: str = "D:/DEV/yt-download-full-stack/downloads"

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
        # Handle both Unix and Windows paths in DATABASE_URL
        db_path = self.DATABASE_URL.replace("sqlite:///", "")
        # Remove leading slash on Windows absolute paths
        if db_path.startswith("/") and ":" in db_path:
            db_path = db_path[1:]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
