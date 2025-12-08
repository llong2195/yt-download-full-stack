"""Channel service with business logic."""

from pathlib import Path
from typing import Dict

import yt_dlp
import yt_dlp.utils
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.models.download_history import DownloadHistory
from src.repository import channel_repo
from src.utils.config import settings
from src.utils.logger import get_logger
from src.utils.validators import extract_channel_id, is_youtube_url, sanitize_filename

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
            "extract_flat": True,
            "skip_download": "True",
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


def validate_and_add_channel(db: Session, url: str) -> Dict:
    """Validate URL, extract metadata, and add channel to database.

    Args:
        db: Database session
        url: YouTube channel URL

    Returns:
        Dictionary with channel info

    Raises:
        InvalidChannelURLError: If URL is invalid
        DuplicateChannelError: If channel already exists
        MetadataFetchError: If metadata cannot be fetched
    """
    # Validate URL format
    if not is_youtube_url(url, "channel"):
        raise InvalidChannelURLError("Invalid YouTube channel URL")

    # Extract channel information
    channel_info = extract_channel_info(url)

    # Check for duplicates
    existing = channel_repo.get_channel_by_youtube_id(db, channel_info["channel_id"])
    if existing:
        raise DuplicateChannelError(f"Channel '{existing.name}' already exists")

    # Create download directory
    download_path = create_channel_directory(channel_info["channel_id"])

    # Save to database
    channel = channel_repo.create_channel(
        db=db,
        channel_id=channel_info["channel_id"],
        name=channel_info["name"],
        url=channel_info["url"],
        download_path=download_path,
    )

    logger.info(f"Added channel: {channel.name} (ID: {channel.channel_id})")

    return {
        "id": channel.id,
        "channel_id": channel.channel_id,
        "name": channel.name,
        "url": channel.url,
        "download_path": channel.download_path,
        "date_added": channel.date_added,
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
                "name": channel.name,
                "url": channel.url,
                "download_path": channel.download_path,
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
