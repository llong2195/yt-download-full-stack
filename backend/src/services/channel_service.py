"""Channel service with business logic."""

from pathlib import Path
from typing import Dict, Literal

import yt_dlp
import yt_dlp.utils
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.models.download_history import DownloadHistory
from src.repository import channel_repo, settings_repo
from src.utils.config import settings
from src.utils.logger import get_logger
from src.utils.validators import (
    extract_channel_id,
    is_youtube_url,
    sanitize_filename,
    validate_download_path,
    validate_subtitle_language,
    validate_video_quality,
)

logger = get_logger(__name__)


class ChannelServiceError(Exception):
    """Base exception for channel service errors."""

    pass


class InvalidChannelURLError(ChannelServiceError):
    """Raised when channel URL is invalid."""

    pass


class DuplicateChannelError(ChannelServiceError):
    """Raised when channel already exists."""

    pass


class DuplicateNameError(ChannelServiceError):
    """Raised when custom channel name already exists."""

    pass


class ValidationError(ChannelServiceError):
    """Raised when validation fails."""

    pass


class MetadataFetchError(ChannelServiceError):
    """Raised when YouTube metadata cannot be fetched."""

    pass


def extract_channel_info(url: str) -> Dict[str, str]:
    """Extract channel information using yt-dlp.

    Args:
        url: YouTube channel URL

    Returns:
        Dictionary with channel_id, name, url

    Raises:
        MetadataFetchError: If extraction fails
    """
    try:
        ydl_opts: yt_dlp._Params = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": "True",
            "extract_flat": "in_playlist",  # Fastest flat extraction mode
            "lazy_playlist": True,  # Don't load all entries at once
            # Disable all unnecessary processing
            "writesubtitles": False,
            "writeautomaticsub": False,
            "writeinfojson": False,
            "writedescription": False,
            "write_all_thumbnails": False,
            "noplaylist": False,
            "ignoreerrors": True,  # Continue on errors
            "nocheckcertificate": True,
            "ignore_no_formats_error": True,
            "skip_unavailable_fragments": True,
            # Minimal extractor work
            "extractor_args": {
                "youtube": {
                    "lang": ["ja"],
                    "player_skip": ["js", "configs", "webpage"],
                    "skip": ["hls", "dash", "translated_subs", "comments", "webpage"],
                }
            },
            "compat_opts": {
                "no-youtube-channel-redirect": True,
                "no-youtube-staleness-check": True,
            },
            # No cookies/auth
            "cookiefile": None,
            "usenetrc": False,
            "cookiesfrombrowser": None,
            "force_generic_extractor": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if not info:
                raise MetadataFetchError("Could not extract channel information")

            # Get channel ID and name
            channel_id = info.get("channel_id") or info.get("id")
            channel_name = (
                info.get("channel") or info.get("uploader") or info.get("title")
            )

            if not channel_id:
                raise MetadataFetchError("Could not extract channel ID")

            if not channel_name:
                channel_name = channel_id  # Fallback to ID as name

            # Normalize URL to canonical form
            canonical_url = f"https://www.youtube.com/channel/{channel_id}"

            return {
                "channel_id": channel_id,
                "name": channel_name,
                "url": canonical_url,
            }

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp error extracting channel info: {e}")
        raise MetadataFetchError(f"Failed to fetch channel metadata: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error extracting channel info: {e}")
        raise MetadataFetchError(f"Unexpected error: {str(e)}")


def create_channel_directory(channel_id: str) -> str:
    """Create download directory for channel.

    Args:
        channel_id: YouTube channel ID

    Returns:
        Absolute path to channel directory
    """
    # Sanitize channel ID for filesystem
    safe_channel_id = sanitize_filename(channel_id)

    # Create path
    channel_path = Path(settings.DOWNLOAD_DIR) / safe_channel_id
    channel_path.mkdir(parents=True, exist_ok=True)

    return str(channel_path.absolute())


def validate_and_add_channel(
    db: Session,
    url: str,
    custom_name: str,
    download_path: str | None = None,
    subtitle_language: str | None = None,
    video_quality: str | None = None,
) -> Dict:
    """Validate URL, extract metadata, and add channel to database.

    Args:
        db: Database session
        url: YouTube channel URL
        custom_name: User-defined custom channel name
        download_path: Optional custom download path
        subtitle_language: Optional subtitle language preference
        video_quality: Optional video quality preference

    Returns:
        Dictionary with channel info

    Raises:
        InvalidChannelURLError: If URL is invalid
        DuplicateChannelError: If channel already exists
        DuplicateNameError: If custom name already exists
        ValidationError: If validation fails
        MetadataFetchError: If metadata cannot be fetched
    """
    # Validate URL format
    if not is_youtube_url(url, "channel"):
        raise InvalidChannelURLError("Invalid YouTube channel URL")

    # Validate custom name uniqueness
    if channel_repo.get_channel_by_name(db, custom_name):
        raise DuplicateNameError(
            f"A channel with the name '{custom_name}' already exists"
        )

    # Validate subtitle language if provided
    if subtitle_language and not validate_subtitle_language(subtitle_language):
        raise ValidationError(
            f"Invalid subtitle language: '{subtitle_language}'. "
            "Must be a 2-letter ISO 639-1 code (e.g., 'en', 'ja')"
        )

    # Validate video quality if provided
    if video_quality and not validate_video_quality(video_quality):
        raise ValidationError(
            f"Invalid video quality: '{video_quality}'. "
            "Allowed values: best, worst, 1080p, 720p, 480p, 360p, 240p, 144p"
        )

    # Extract channel information from YouTube
    channel_info = extract_channel_info(url)

    # Check for duplicate YouTube channel
    existing = channel_repo.get_channel_by_youtube_id(db, channel_info["channel_id"])
    if existing:
        raise DuplicateChannelError(
            f"This YouTube channel is already tracked as '{existing.name}'"
        )

    # Determine download path
    if download_path:
        # Validate custom path
        is_valid_path, path_error = validate_download_path(download_path)
        if not is_valid_path:
            raise ValidationError(f"Invalid download path: {path_error}")
        final_download_path = download_path
    else:
        # Use global default + custom name
        global_settings = settings_repo.get_settings(db)
        base_path = (
            global_settings.default_download_path
            if global_settings
            else settings.DOWNLOAD_DIR
        )
        final_download_path = str(Path(base_path) / sanitize_filename(custom_name))

    # Create download directory
    Path(final_download_path).mkdir(parents=True, exist_ok=True)

    # Save to database
    channel = channel_repo.create_channel(
        db=db,
        channel_id=channel_info["channel_id"],
        title=channel_info["name"],  # YouTube's channel title
        name=custom_name,  # User's custom name
        url=channel_info["url"],
        download_path=final_download_path,
        subtitle_language=subtitle_language,
        video_quality=video_quality,
    )

    logger.info(
        f"Added channel: '{custom_name}' (YouTube: {channel_info['name']}, "
        f"ID: {channel.channel_id})"
    )

    return {
        "id": channel.id,
        "channel_id": channel.channel_id,
        "title": channel.title,
        "name": channel.name,
        "url": channel.url,
        "download_path": channel.download_path,
        "subtitle_language": channel.subtitle_language,
        "video_quality": channel.video_quality,
        "date_added": channel.date_added,
        "last_updated": channel.last_updated,
    }


def update_channel(
    db: Session,
    channel_id: int,
    name: str | None = None,
    download_path: str | None = None,
    subtitle_language: str | None = None,
    video_quality: str | None = None,
) -> Dict | None:
    """Update channel settings.

    Args:
        db: Database session
        channel_id: Internal channel ID
        name: New custom name (optional)
        download_path: New download path (optional)
        subtitle_language: New subtitle language (optional)
        video_quality: New video quality (optional)

    Returns:
        Updated channel info

    Raises:
        DuplicateNameError: If new name already exists
        ValidationError: If validation fails
    """
    # Get existing channel
    channel = channel_repo.get_channel_by_id(db, channel_id)
    if not channel:
        return None

    # Validate name uniqueness if changing
    if name and name != channel.name:
        existing = channel_repo.get_channel_by_name(db, name)
        if existing:
            raise DuplicateNameError(
                f"A channel with the name '{name}' already exists"
            )

    # Validate download path if provided
    if download_path:
        is_valid_path, path_error = validate_download_path(download_path)
        if not is_valid_path:
            raise ValidationError(f"Invalid download path: {path_error}")

    # Validate subtitle language if provided
    if subtitle_language and not validate_subtitle_language(subtitle_language):
        raise ValidationError(
            f"Invalid subtitle language: '{subtitle_language}'. "
            "Must be a 2-letter ISO 639-1 code (e.g., 'en', 'ja')"
        )

    # Validate video quality if provided
    if video_quality and not validate_video_quality(video_quality):
        raise ValidationError(
            f"Invalid video quality: '{video_quality}'. "
            "Allowed values: best, worst, 1080p, 720p, 480p, 360p, 240p, 144p"
        )

    # Update channel
    updated_channel = channel_repo.update_channel(
        db=db,
        channel_id=channel_id,
        name=name,
        download_path=download_path,
        subtitle_language=subtitle_language,
        video_quality=video_quality,
    )
    
    if not updated_channel:
        return None

    if updated_channel:
        logger.info(f"Updated channel: {updated_channel.name} (ID: {channel_id})")

    return {
        "id": updated_channel.id,
        "channel_id": updated_channel.channel_id,
        "title": updated_channel.title,
        "name": updated_channel.name,
        "url": updated_channel.url,
        "download_path": updated_channel.download_path,
        "subtitle_language": updated_channel.subtitle_language,
        "video_quality": updated_channel.video_quality,
        "date_added": updated_channel.date_added,
        "last_updated": updated_channel.last_updated,
    }


def get_all_channels_with_stats(db: Session):
    """Get all channels with download statistics.

    Args:
        db: Database session

    Returns:
        List of channels with video counts
    """
    channels = channel_repo.get_all_channels(db)
    result = []

    for channel in channels:
        # Count successful downloads for this channel
        video_count = (
            db.query(func.count(DownloadHistory.id))
            .filter(
                DownloadHistory.channel_id == channel.id,
                DownloadHistory.success,
            )
            .scalar()
        )

        result.append(
            {
                "id": channel.id,
                "channel_id": channel.channel_id,
                "title": channel.title,
                "name": channel.name,
                "url": channel.url,
                "download_path": channel.download_path,
                "subtitle_language": channel.subtitle_language,
                "video_quality": channel.video_quality,
                "date_added": channel.date_added,
                "last_updated": channel.last_updated,
                "video_count": video_count or 0,
            }
        )

    return result


def delete_channel_with_files(db: Session, channel_id: int) -> bool:
    """Delete channel and optionally its downloaded files.

    Args:
        db: Database session
        channel_id: Internal channel ID

    Returns:
        True if deleted, False if not found
    """
    channel = channel_repo.get_channel_by_id(db, channel_id)
    if not channel:
        return False

    # Delete from database (cascade will handle related records)
    success = channel_repo.delete_channel(db, channel_id)

    if success:
        logger.info(f"Deleted channel: {channel.name} (ID: {channel.channel_id})")
        # Note: Files are NOT deleted automatically to preserve user data
        # Users can manually delete the directory if needed

    return success
