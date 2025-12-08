"""DownloadHistory model for audit logging with video metadata."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, BigInteger, Index
from sqlalchemy.sql import func
from .database import Base


class DownloadHistory(Base):
    """Persistent record of all download attempts with complete video information."""

    __tablename__ = "download_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(String(11), nullable=False, index=True)
    video_title = Column(String(500), nullable=False)
    video_url = Column(String(1000), nullable=False)
    task_id = Column(String(36), nullable=True, index=True)
    download_date = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    upload_date = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)
    file_path = Column(String(2000), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    video_metadata = Column(String, nullable=True)  # JSON stored as string (renamed from 'metadata')
    download_duration_seconds = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False, index=True)
    error_code = Column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_history_channel_video", "channel_id", "video_id"),
        Index("ix_history_video_date", "video_id", "download_date"),
    )

    def __repr__(self):
        return f"<DownloadHistory(id={self.id}, video_id={self.video_id}, success={self.success})>"
