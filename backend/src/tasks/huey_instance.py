"""Huey task queue instance."""

from pathlib import Path
from huey import SqliteHuey
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Ensure Huey database exists before initializing
try:
    settings.ensure_huey_database()
    logger.info(f"Huey database ready: {settings.HUEY_DB}")
except Exception as e:
    logger.error(f"Failed to initialize Huey database: {e}")
    raise

# Initialize Huey task queue
# immediate=True means tasks execute immediately without needing a consumer
# Set to False in production and run consumer separately: python -m huey.consumer main.huey
# huey = SqliteHuey(filename=settings.HUEY_DB, immediate=settings.HUEY_IMMEDIATE_MODE)
huey = SqliteHuey(filename=settings.HUEY_DB)

logger.info(
    f"Huey initialized - Immediate mode: {settings.HUEY_IMMEDIATE_MODE}, "
    f"DB: {settings.HUEY_DB}"
)
