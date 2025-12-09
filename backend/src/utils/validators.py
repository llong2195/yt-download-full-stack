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


# ============================================================================
# Video Quality and Subtitle Language Validation
# ============================================================================

VALID_QUALITY_KEYWORDS = ["best", "worst", "bestaudio", "bestvideo"]
VALID_RESOLUTIONS = [
    "2160p",
    "1440p",
    "1080p",
    "720p",
    "480p",
    "360p",
    "240p",
    "144p",
]
VALID_LANGUAGES = [
    "en",
    "ja",
    "ko",
    "zh",
    "vi",
    "es",
    "fr",
    "de",
    "ru",
    "ar",
    "pt",
    "it",
    "th",
    "pl",
    "nl",
    "tr",
    "sv",
    "id",
    "hi",
    "cs",
]


def validate_video_quality(quality: str | None) -> bool:
    """Validate video quality setting.

    Args:
        quality: Video quality string (e.g., '1080p', 'best')

    Returns:
        True if valid quality, False otherwise
    """
    if quality is None:
        return True
    return quality in VALID_QUALITY_KEYWORDS or quality in VALID_RESOLUTIONS


def validate_subtitle_language(language: str | None) -> bool:
    """Validate subtitle language code.

    Args:
        language: ISO 639-1 language code (e.g., 'en', 'ja')

    Returns:
        True if valid language code, False otherwise
    """
    if language is None:
        return True
    return len(language) == 2 and language.lower() in VALID_LANGUAGES


def validate_download_path(path: str) -> tuple[bool, str | None]:
    """Validate download path.

    Args:
        path: Download path string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path or not path.strip():
        return False, "Download path cannot be empty"

    # Check for invalid filesystem characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        if char in path:
            return (
                False,
                f"Path contains invalid character: {char}",
            )

    # Check path length (leave room for filenames)
    if len(path) > 250:
        return False, "Path too long (max 250 characters)"

    # Check for Windows reserved names
    reserved_names = [
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    ]
    path_obj = Path(path)
    for part in path_obj.parts:
        if part.upper() in reserved_names:
            return False, f"Path contains reserved name: {part}"

    return True, None
