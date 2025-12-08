"""Download repository for download tasks and history."""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models.download_task import DownloadTask
from models.download_history import DownloadHistory
from typing import List, Optional
from datetime import datetime


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
        task.started_at = datetime.utcnow()
    elif status in ["completed", "failed"]:
        task.completed_at = datetime.utcnow()

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
                DownloadHistory.success == True,
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
