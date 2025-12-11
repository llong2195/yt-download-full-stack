"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///./data/ytdownloader.db"

    # Huey Task Queue
    HUEY_DB: str = "./data/huey.db"
    HUEY_IMMEDIATE_MODE: bool = (
        False  # Set to True for development (tasks run immediately)
    )

    # Download Configuration
    DOWNLOAD_DIR: str = "D:/DEV/yt-download-full-stack/downloads"

    # API Configuration
    API_PORT: int = 8000
    DEBUG: bool = False

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,chrome-extension://*"
    YT_DLP_COOKIES_FILE: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def yt_dlp_cookies_path(self) -> Path | None:
        """Return expanded Path to yt-dlp cookies file, if configured."""
        if not self.YT_DLP_COOKIES_FILE:
            return None
        return Path(self.YT_DLP_COOKIES_FILE).expanduser()

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
        if cookies_path := self.yt_dlp_cookies_path:
            cookies_path.parent.mkdir(parents=True, exist_ok=True)

    def ensure_huey_database(self):
        """Ensure Huey database file exists and is initialized.

        SQLite will create the file automatically, but we ensure
        the parent directory exists and the file is accessible.
        """
        huey_db_path = Path(self.HUEY_DB)

        # Ensure parent directory exists
        huey_db_path.parent.mkdir(parents=True, exist_ok=True)

        # If file doesn't exist, SQLite will create it on first connection
        # but we can touch it to verify write permissions
        if not huey_db_path.exists():
            try:
                huey_db_path.touch(exist_ok=True)
                return True
            except Exception as e:
                raise RuntimeError(
                    f"Cannot create Huey database at {self.HUEY_DB}: {e}"
                )

        # Verify file is writable
        if not os.access(huey_db_path, os.W_OK):
            raise RuntimeError(f"Huey database at {self.HUEY_DB} is not writable")

        return True


# Global settings instance
settings = Settings()
