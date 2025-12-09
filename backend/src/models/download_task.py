"""DownloadTask model for tracking download operations."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .database import Base


class DownloadTask(Base):
    """Represents a queued or active download operation."""

    __tablename__ = "download_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True
    )
    channel_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    video_id: Mapped[str] = mapped_column(String(11), nullable=False, index=True)
    video_title: Mapped[str] = mapped_column(String(10000), nullable=False)
    video_url: Mapped[str] = mapped_column(String(10000), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # pending, downloading, completed, failed
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    __table_args__ = (
        Index("ix_task_status_created", "status", "created_at"),
        Index("ix_task_channel_video", "channel_id", "video_id"),
    )

    def __repr__(self):
        return f"<DownloadTask(id={self.id}, task_id={self.task_id}, video_id={self.video_id}, status={self.status})>"
