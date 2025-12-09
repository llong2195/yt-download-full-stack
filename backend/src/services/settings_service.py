"""Settings service with business logic."""

from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session
from src.repository import settings_repo
from src.utils.logger import get_logger
from src.utils.validators import (
    validate_download_path,
    validate_subtitle_language,
    validate_video_quality,
)

logger = get_logger(__name__)


class SettingsServiceError(Exception):
    """Base exception for settings service errors."""

    pass


class ValidationError(SettingsServiceError):
    """Raised when validation fails."""

    pass


def get_global_settings(db: Session):
    """Get global settings.

    Args:
        db: Database session

    Returns:
        GlobalSettings object or None

    Raises:
        SettingsServiceError: If settings not found
    """
    settings = settings_repo.get_settings(db)
    if not settings:
        raise SettingsServiceError("Global settings not found")
    return settings


def update_global_settings(
    db: Session,
    default_download_path: str,
    default_subtitle_language: Optional[str] = None,
    default_video_quality: Optional[str] = None,
):
    """Update global settings with validation.

    Args:
        db: Database session
        default_download_path: Base download directory
        default_subtitle_language: Default subtitle language code
        default_video_quality: Default video quality

    Returns:
        Updated GlobalSettings object

    Raises:
        ValidationError: If any validation fails
    """
    # Validate download path
    is_valid_path, path_error = validate_download_path(default_download_path)
    if not is_valid_path:
        raise ValidationError(f"Invalid download path: {path_error}")

    # Validate subtitle language
    if not validate_subtitle_language(default_subtitle_language):
        raise ValidationError(
            f"Invalid subtitle language: '{default_subtitle_language}'. "
            "Must be a 2-letter ISO 639-1 code (e.g., 'en', 'ja')"
        )

    # Validate video quality
    if not validate_video_quality(default_video_quality):
        raise ValidationError(
            f"Invalid video quality: '{default_video_quality}'. "
            "Allowed values: best, worst, 1080p, 720p, 480p, 360p, 240p, 144p"
        )

    # Update settings
    settings = settings_repo.update_settings(
        db=db,
        default_download_path=default_download_path,
        default_subtitle_language=default_subtitle_language,
        default_video_quality=default_video_quality,
    )

    logger.info("Updated global settings")
    return settings


def get_effective_settings(
    channel,
    global_settings,
    setting_name: str,
    hardcoded_default,
):
    """Get effective setting value using fallback chain.

    Priority: channel-specific > global default > hardcoded default

    Args:
        channel: Channel object (can be None)
        global_settings: GlobalSettings object
        setting_name: Name of the setting (e.g., 'subtitle_language')
        hardcoded_default: Hardcoded fallback value

    Returns:
        Effective setting value
    """
    # Try channel-specific value first
    if channel:
        channel_value = getattr(channel, setting_name, None)
        if channel_value is not None:
            return channel_value

    # Try global default
    if global_settings:
        global_value = getattr(global_settings, f"default_{setting_name}", None)
        if global_value is not None:
            return global_value

    # Fall back to hardcoded default
    return hardcoded_default
