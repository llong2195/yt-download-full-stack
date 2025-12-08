"""Download repository for download tasks and history."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.models.download_history import DownloadHistory
from src.models.download_task import DownloadTask

# ============================================================================
# DownloadTask Repository
# ============================================================================


def get_task_by_id(db: Session, task_id: int) -> Optional[DownloadTask]:
    """Get download task by internal ID."""
    return db.query(DownloadTask).filter(DownloadTask.id == task_id).first()


def get_task_by_task_id(db: Session, task_id: str) -> Optional[DownloadTask]:
    """Get download task by Huey task ID."""
    return db.query(DownloadTask).filter(DownloadTask.task_id == task_id).first()


def get_active_task_for_video(db: Session, video_id: str) -> Optional[DownloadTask]:
    """Check if there's an active download task for this video.

    Args:
        db: Database session
        video_id: YouTube video ID

    Returns:
        Active DownloadTask or None
    """
    return (
        db.query(DownloadTask)
        .filter(
            and_(
                DownloadTask.video_id == video_id,
                DownloadTask.status.in_(["pending", "downloading"]),
            )
        )
        .first()
    )


def create_download_task(
    db: Session,
    task_id: str,
    channel_id: int,
    video_id: str,
    video_url: str,
) -> DownloadTask:
    """Create a new download task."""
    task = DownloadTask(
        task_id=task_id,
        channel_id=channel_id,
        video_id=video_id,
        video_url=video_url,
        status="pending",
        progress_percent=0,
        retry_count=0,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task_status(
    db: Session,
    task_id: str,
    status: str,
    progress_percent: Optional[int] = None,
    error_message: Optional[str] = None,
) -> Optional[DownloadTask]:
    """Update task status and progress."""
    task = get_task_by_task_id(db, task_id)
    if not task:
        return None

    task.status = status
    if progress_percent is not None:
        task.progress_percent = progress_percent
    if error_message is not None:
        task.error_message = error_message

    if status == "downloading" and not task.started_at:
        task.started_at = datetime.now()
    elif status in ["completed", "failed"]:
        task.completed_at = datetime.now()

    db.commit()
    db.refresh(task)
    return task


def get_tasks_by_status(db: Session, status: str) -> List[DownloadTask]:
    """Get all tasks with given status."""
    return (
        db.query(DownloadTask)
        .filter(DownloadTask.status == status)
        .order_by(DownloadTask.created_at.desc())
        .all()
    )


def get_all_active_tasks(db: Session) -> List[DownloadTask]:
    """Get all pending and downloading tasks."""
    return (
        db.query(DownloadTask)
        .filter(DownloadTask.status.in_(["pending", "downloading"]))
        .order_by(DownloadTask.created_at.desc())
        .all()
    )


def get_task_with_channel_info(db: Session, task_id: str) -> Optional[dict]:
    """Get task with channel information via JOIN."""
    from src.models.channel import Channel
    
    result = (
        db.query(DownloadTask, Channel)
        .join(Channel, DownloadTask.channel_id == Channel.id)
        .filter(DownloadTask.task_id == task_id)
        .first()
    )
    
    if not result:
        return None
    
    task, channel = result
    return {
        "task": task,
        "channel": channel,
    }


# ============================================================================
# DownloadHistory Repository
# ============================================================================


def create_history_record(
    db: Session,
    channel_id: int,
    video_id: str,
    video_title: str,
    video_url: str,
    task_id: str,
    download_duration_seconds: int,
    success: bool,
    upload_date: Optional[str] = None,
    duration: Optional[int] = None,
    file_path: Optional[str] = None,
    file_size: Optional[int] = None,
    video_metadata: Optional[str] = None,
    error_code: Optional[str] = None,
) -> DownloadHistory:
    """Create a new history record."""
    history = DownloadHistory(
        channel_id=channel_id,
        video_id=video_id,
        video_title=video_title,
        video_url=video_url,
        task_id=task_id,
        download_duration_seconds=download_duration_seconds,
        success=success,
        upload_date=upload_date,
        duration=duration,
        file_path=file_path,
        file_size=file_size,
        video_metadata=video_metadata,
        error_code=error_code,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_successful_download_for_video(
    db: Session, video_id: str
) -> Optional[DownloadHistory]:
    """Check if video was already successfully downloaded."""
    return (
        db.query(DownloadHistory)
        .filter(
            and_(
                DownloadHistory.video_id == video_id,
                DownloadHistory.success,
            )
        )
        .order_by(DownloadHistory.download_date.desc())
        .first()
    )


def get_history_by_channel(
    db: Session, channel_id: int, limit: int = 100
) -> List[DownloadHistory]:
    """Get download history for a channel."""
    return (
        db.query(DownloadHistory)
        .filter(DownloadHistory.channel_id == channel_id)
        .order_by(DownloadHistory.download_date.desc())
        .limit(limit)
        .all()
    )


def get_all_history(
    db: Session, skip: int = 0, limit: int = 100
) -> List[DownloadHistory]:
    """Get all download history with pagination."""
    return (
        db.query(DownloadHistory)
        .order_by(DownloadHistory.download_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_history_with_filters(
    db: Session,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    success: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[List[DownloadHistory], int]:
    """Get download history with search and filters.

    Args:
        db: Database session
        search: Search in video_title (case-insensitive)
        date_from: Filter by download_date >= date_from
        date_to: Filter by download_date <= date_to
        success: Filter by success status
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        Tuple of (history records, total count)
    """
    from src.models.channel import Channel

    # Build query with JOIN to Channel to get channel name
    query = db.query(DownloadHistory).join(
        Channel, DownloadHistory.channel_id == Channel.id
    )

    # Apply filters
    if search:
        query = query.filter(
            DownloadHistory.video_title.ilike(f"%{search}%")
        )
    
    if date_from:
        query = query.filter(DownloadHistory.download_date >= date_from)
    
    if date_to:
        query = query.filter(DownloadHistory.download_date <= date_to)
    
    if success is not None:
        query = query.filter(DownloadHistory.success == success)

    # Get total count before pagination
    total_count = query.count()

    # Apply pagination and ordering
    results = (
        query.order_by(DownloadHistory.download_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return results, total_count


def get_history_stats(db: Session, period: str = "all") -> dict:
    """Get download history statistics.

    Args:
        db: Database session
        period: Time period for stats (7d, 30d, 90d, all)

    Returns:
        Dictionary with stats: total, success_rate, total_size, avg_time, most_downloaded_channel
    """
    from src.models.channel import Channel
    from sqlalchemy import func

    # Calculate date filter based on period
    date_filter = None
    if period == "7d":
        date_filter = datetime.now() - datetime.timedelta(days=7)
    elif period == "30d":
        date_filter = datetime.now() - datetime.timedelta(days=30)
    elif period == "90d":
        date_filter = datetime.now() - datetime.timedelta(days=90)

    # Base query
    query = db.query(DownloadHistory)
    if date_filter:
        query = query.filter(DownloadHistory.download_date >= date_filter)

    # Get all stats
    total = query.count()
    successful = query.filter(DownloadHistory.success == True).count()
    success_rate = (successful / total * 100) if total > 0 else 0.0

    # Total size (sum of file_size where not null)
    total_size = (
        query.filter(DownloadHistory.file_size.isnot(None))
        .with_entities(func.sum(DownloadHistory.file_size))
        .scalar()
        or 0
    )

    # Average download time
    avg_time = (
        query.filter(DownloadHistory.download_duration_seconds.isnot(None))
        .with_entities(func.avg(DownloadHistory.download_duration_seconds))
        .scalar()
        or 0.0
    )

    # Most downloaded channel
    most_downloaded = (
        query.join(Channel, DownloadHistory.channel_id == Channel.id)
        .filter(DownloadHistory.success == True)
        .with_entities(
            Channel.name,
            func.count(DownloadHistory.id).label("download_count"),
        )
        .group_by(Channel.name)
        .order_by(func.count(DownloadHistory.id).desc())
        .first()
    )

    most_downloaded_channel = most_downloaded[0] if most_downloaded else None

    return {
        "total": total,
        "successful": successful,
        "success_rate": round(success_rate, 2),
        "total_size": total_size,
        "avg_download_time": round(float(avg_time), 2),
        "most_downloaded_channel": most_downloaded_channel,
    }
