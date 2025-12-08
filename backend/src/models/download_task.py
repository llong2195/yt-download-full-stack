"""DownloadTask model for tracking download operations."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from .database import Base


class DownloadTask(Base):
    """Represents a queued or active download operation."""

    __tablename__ = "download_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), unique=True, nullable=False, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(String(11), nullable=False, index=True)
    video_url = Column(String(1000), nullable=False)
    status = Column(String(20), nullable=False, index=True)  # pending, downloading, completed, failed
    progress_percent = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_task_status_created", "status", "created_at"),
        Index("ix_task_channel_video", "channel_id", "video_id"),
    )

    def __repr__(self):
        return f"<DownloadTask(id={self.id}, task_id={self.task_id}, video_id={self.video_id}, status={self.status})>"
