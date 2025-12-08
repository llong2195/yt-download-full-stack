"""YouTube service for video metadata extraction."""

from datetime import datetime
from typing import Dict, Optional

import yt_dlp
import yt_dlp.utils
from src.utils.logger import get_logger
from src.utils.validators import extract_video_id

logger = get_logger(__name__)


class YouTubeServiceError(Exception):
    """Base exception for YouTube service errors."""

    pass


class VideoUnavailableError(YouTubeServiceError):
    """Raised when video is unavailable."""

    pass


class MetadataFetchError(YouTubeServiceError):
    """Raised when metadata cannot be fetched."""

    pass


def extract_video_id_from_url(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL.

    Args:
        url: YouTube video URL

    Returns:
        Video ID or None if not found
    """
    return extract_video_id(url)


def extract_video_metadata(video_url: str) -> Dict:
    """Extract video metadata using yt-dlp without downloading.

    Args:
        video_url: YouTube video URL

    Returns:
        Dictionary with video metadata

    Raises:
        VideoUnavailableError: If video is unavailable
        MetadataFetchError: If metadata extraction fails
    """
    try:
        ydl_opts: yt_dlp._Params = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": "True",
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            if not info:
                raise MetadataFetchError("Could not extract video information")

            # Extract required fields
            video_id = info.get("id")
            if not video_id:
                raise MetadataFetchError("Could not extract video ID")

            # Get channel information
            channel_id = info.get("channel_id")
            channel_name = info.get("channel") or info.get("uploader")
            channel_url = (
                info.get("channel_url")
                or f"https://www.youtube.com/channel/{channel_id}"
            )

            # Get video information
            title = info.get("title", "Unknown Title")
            duration = info.get("duration")  # in seconds
            upload_date = info.get("upload_date")  # YYYYMMDD format

            # Parse upload_date to datetime string
            upload_date_str = None
            if upload_date:
                try:
                    dt = datetime.strptime(upload_date, "%Y%m%d")
                    upload_date_str = dt.isoformat()
                except Exception:
                    pass

            return {
                "video_id": video_id,
                "video_title": title,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "channel_id": channel_id,
                "channel_name": channel_name,
                "channel_url": channel_url,
                "duration": duration,
                "upload_date": upload_date_str,
            }

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Video unavailable" in error_msg or "not available" in error_msg:
            raise VideoUnavailableError(f"Video unavailable: {error_msg}")
        logger.error(f"yt-dlp error extracting video metadata: {e}")
        raise MetadataFetchError(f"Failed to fetch video metadata: {error_msg}")

    except Exception as e:
        logger.error(f"Unexpected error extracting video metadata: {e}")
        raise MetadataFetchError(f"Unexpected error: {str(e)}")


def extract_channel_id_from_video_url(video_url: str) -> Optional[str]:
    """Extract channel ID from a video URL.

    Args:
        video_url: YouTube video URL

    Returns:
        Channel ID or None if extraction fails
    """
    try:
        metadata = extract_video_metadata(video_url)
        return metadata.get("channel_id")
    except Exception as e:
        logger.warning(f"Could not extract channel ID from video URL: {e}")
        return None
