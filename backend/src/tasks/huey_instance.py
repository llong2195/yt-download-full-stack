"""Huey task queue instance."""

from huey import SqliteHuey
from src.utils.config import settings

# Initialize Huey task queue
huey = SqliteHuey(filename=settings.HUEY_DB)
