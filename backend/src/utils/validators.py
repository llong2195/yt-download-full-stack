"""Validation utilities for URLs and paths."""

import re
from pathlib import Path
from urllib.parse import urlparse

# YouTube URL patterns
YOUTUBE_PATTERNS = {
    "channel": [
        r"youtube\.com/channel/([a-zA-Z0-9_-]+)",
        r"youtube\.com/c/([a-zA-Z0-9_-]+)",
        r"youtube\.com/@([a-zA-Z0-9_-]+)",
        r"youtube\.com/user/([a-zA-Z0-9_-]+)",
    ],
    "video": [
        r"youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/v/([a-zA-Z0-9_-]{11})",
    ],
}


def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_youtube_url(url: str, url_type: str | None = None) -> bool:
    """Check if URL is a valid YouTube URL.

    Args:
        url: URL string to validate
        url_type: Optional type to check ('channel' or 'video')

    Returns:
        True if valid YouTube URL, False otherwise
    """
    if not is_valid_url(url):
        return False

    patterns = []
    if url_type:
        patterns = YOUTUBE_PATTERNS.get(url_type, [])
    else:
        patterns = YOUTUBE_PATTERNS["channel"] + YOUTUBE_PATTERNS["video"]

    for pattern in patterns:
        if re.search(pattern, url):
            return True

    return False


def extract_video_id(url: str) -> str | None:
    """Extract video ID from YouTube URL.

    Args:
        url: YouTube video URL

    Returns:
        Video ID string or None if not found
    """
    for pattern in YOUTUBE_PATTERNS["video"]:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_channel_id(url: str) -> str | None:
    """Extract channel identifier from YouTube URL.

    Args:
        url: YouTube channel URL

    Returns:
        Channel identifier or None if not found
    """
    for pattern in YOUTUBE_PATTERNS["channel"]:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[: 200 - len(ext) - 1] + "." + ext if ext else name[:200]

    return filename.strip()


def sanitize_path(path: str) -> str:
    """Sanitize path components.

    Args:
        path: Original path

    Returns:
        Sanitized path
    """
    parts = Path(path).parts
    sanitized_parts = [sanitize_filename(part) for part in parts]
    return str(Path(*sanitized_parts))
