"""Settings repository for database operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from src.models.global_settings import GlobalSettings


def get_settings(db: Session) -> Optional[GlobalSettings]:
    """Get global settings (singleton row).

    Args:
        db: Database session

    Returns:
        GlobalSettings object or None if not found
    """
    return db.query(GlobalSettings).filter_by(id=1).first()


def update_settings(
    db: Session,
    default_download_path: str,
    default_subtitle_language: Optional[str] = None,
    default_video_quality: Optional[str] = None,
) -> GlobalSettings:
    """Update global settings.

    Args:
        db: Database session
        default_download_path: Base download directory
        default_subtitle_language: Default subtitle language code
        default_video_quality: Default video quality

    Returns:
        Updated GlobalSettings object
    """
    settings = get_settings(db)
    if not settings:
        # Create if doesn't exist (safety fallback)
        settings = GlobalSettings(
            id=1,
            default_download_path=default_download_path,
            default_subtitle_language=default_subtitle_language,
            default_video_quality=default_video_quality,
        )
        db.add(settings)
    else:
        settings.default_download_path = default_download_path
        settings.default_subtitle_language = default_subtitle_language
        settings.default_video_quality = default_video_quality
        settings.updated_at = datetime.now()

    db.commit()
    db.refresh(settings)
    return settings
