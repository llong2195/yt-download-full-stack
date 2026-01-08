"""Channel repository for database operations."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from src.models.channel import Channel


def get_all_channels(db: Session) -> List[Channel]:
    """Get all channels ordered by date added (newest first).

    Args:
        db: Database session

    Returns:
        List of all Channel objects
    """
    return db.query(Channel).order_by(Channel.date_added.desc()).all()


def get_channel_by_id(db: Session, channel_id: int) -> Optional[Channel]:
    """Get channel by internal ID.

    Args:
        db: Database session
        channel_id: Internal channel ID

    Returns:
        Channel object or None if not found
    """
    return db.query(Channel).filter(Channel.id == channel_id).first()


def get_channel_by_youtube_id(
    db: Session, youtube_channel_id: str
) -> Optional[Channel]:
    """Get channel by YouTube channel ID.

    Args:
        db: Database session
        youtube_channel_id: YouTube's channel ID (e.g., "UC...")

    Returns:
        Channel object or None if not found
    """
    return db.query(Channel).filter(Channel.channel_id == youtube_channel_id).first()


def get_channel_by_name(db: Session, name: str) -> Optional[Channel]:
    """Get channel by custom name.

    Args:
        db: Database session
        name: Custom user-defined channel name

    Returns:
        Channel object or None if not found
    """
    return db.query(Channel).filter(Channel.name == name).first()


def create_channel(
    db: Session,
    channel_id: str,
    title: str,
    name: str,
    url: str,
    download_path: str,
    subtitle_language: Optional[str] = None,
    video_quality: Optional[str] = None,
) -> Channel:
    """Create a new channel.

    Args:
        db: Database session
        channel_id: YouTube channel ID
        title: YouTube channel title
        name: Custom user-defined channel name
        url: Full YouTube channel URL
        download_path: Local filesystem path for downloads
        subtitle_language: Preferred subtitle language (optional)
        video_quality: Preferred video quality (optional)

    Returns:
        Created Channel object
    """
    channel = Channel(
        channel_id=channel_id,
        title=title,
        name=name,
        url=url,
        download_path=download_path,
        subtitle_language=subtitle_language,
        video_quality=video_quality,
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


def delete_channel(db: Session, channel_id: int) -> bool:
    """Delete channel by internal ID.

    Args:
        db: Database session
        channel_id: Internal channel ID

    Returns:
        True if deleted, False if not found
    """
    channel = get_channel_by_id(db, channel_id)
    if not channel:
        return False

    db.delete(channel)
    db.commit()
    return True


def update_channel(
    db: Session,
    channel_id: int,
    name: Optional[str] = None,
    download_path: Optional[str] = None,
    subtitle_language: Optional[str] = None,
    video_quality: Optional[str] = None,
) -> Optional[Channel]:
    """Update channel settings.

    Args:
        db: Database session
        channel_id: Internal channel ID
        name: New custom channel name (optional)
        download_path: New download path (optional)
        subtitle_language: New subtitle language (optional)
        video_quality: New video quality (optional)

    Returns:
        Updated Channel object or None if not found
    """
    channel = get_channel_by_id(db, channel_id)
    if not channel:
        return None

    if name is not None:
        channel.name = name
    if download_path is not None:
        channel.download_path = download_path
    if subtitle_language is not None:
        channel.subtitle_language = subtitle_language
    if video_quality is not None:
        channel.video_quality = video_quality

    channel.last_updated = datetime.now()

    db.commit()
    db.refresh(channel)
    return channel
