"""Database configuration and session management."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from src.utils.config import settings

# Create engine with SQLite WAL mode for better concurrency
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    echo=settings.DEBUG,
)


# Enable WAL mode for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Create declarative base for models
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def verify_indexes():
    """Verify that all required indexes exist in the database.

    Expected indexes from data-model.md:
    - Channel: idx_channel_channel_id (channel_id)
    - DownloadTask: idx_task_video_id (video_id), idx_task_status (status)
    - DownloadHistory: idx_history_video_id (video_id), idx_history_channel (channel_id),
                      idx_history_date (download_date), idx_history_success (success)

    Returns:
        dict: Index verification results
    """
    from sqlalchemy import inspect

    inspector = inspect(engine)
    results = {}

    # Check each table's indexes
    for table_name in ["channel", "download_task", "download_history"]:
        indexes = inspector.get_indexes(table_name)
        results[table_name] = {
            "indexes": [idx["name"] for idx in indexes],
            "count": len(indexes),
        }

    return results


# Dependency for FastAPI routes
def get_db():
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
