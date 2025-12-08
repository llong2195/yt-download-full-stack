"""DownloadHistory model for audit logging with video metadata."""

from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .database import Base


class DownloadHistory(Base):
    """Persistent record of all download attempts with complete video information."""

    __tablename__ = "download_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id: Mapped[str] = mapped_column(String(11), nullable=False, index=True)
    video_title: Mapped[str] = mapped_column(String(500), nullable=False)
    video_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    task_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    download_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)
    upload_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    file_path: Mapped[str] = mapped_column(String(2000), nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=True)
    video_metadata: Mapped[str] = mapped_column(String, nullable=True)  # JSON stored as string (renamed from 'metadata')
    download_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    error_code: Mapped[str] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_history_channel_video", "channel_id", "video_id"),
        Index("ix_history_video_date", "video_id", "download_date"),
    )

    def __repr__(self):
        return f"<DownloadHistory(id={self.id}, video_id={self.video_id}, success={self.success})>"
