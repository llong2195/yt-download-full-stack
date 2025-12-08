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


def get_channel_by_youtube_id(db: Session, youtube_channel_id: str) -> Optional[Channel]:
    """Get channel by YouTube channel ID.

    Args:
        db: Database session
        youtube_channel_id: YouTube's channel ID (e.g., "UC...")

    Returns:
        Channel object or None if not found
    """
    return db.query(Channel).filter(Channel.channel_id == youtube_channel_id).first()


def create_channel(
    db: Session,
    channel_id: str,
    name: str,
    url: str,
    download_path: str,
) -> Channel:
    """Create a new channel.

    Args:
        db: Database session
        channel_id: YouTube channel ID
        name: Channel display name
        url: Full YouTube channel URL
        download_path: Local filesystem path for downloads

    Returns:
        Created Channel object
    """
    channel = Channel(
        channel_id=channel_id,
        name=name,
        url=url,
        download_path=download_path,
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


def update_channel_metadata(
    db: Session,
    channel_id: int,
    name: Optional[str] = None,
) -> Optional[Channel]:
    """Update channel metadata.

    Args:
        db: Database session
        channel_id: Internal channel ID
        name: New channel name (optional)

    Returns:
        Updated Channel object or None if not found
    """
    channel = get_channel_by_id(db, channel_id)
    if not channel:
        return None

    if name is not None:
        channel.name = name

    channel.last_updated = datetime.now()

    db.commit()
    db.refresh(channel)
    return channel
