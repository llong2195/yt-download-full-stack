"""Huey task queue instance."""

from huey import SqliteHuey
from src.utils.config import settings

# Initialize Huey task queue
# immediate=True means tasks execute immediately without needing a consumer
# Set to False in production and run consumer separately: python -m huey.consumer main.huey
huey = SqliteHuey(filename=settings.HUEY_DB, immediate=settings.HUEY_IMMEDIATE_MODE)
