"""Global settings model for application-wide defaults."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .database import Base


class GlobalSettings(Base):
    """System-wide default configuration (singleton pattern)."""

    __tablename__ = "global_settings"
    __table_args__ = (CheckConstraint("id = 1", name="singleton_check"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    default_download_path: Mapped[str] = mapped_column(
        String(2000), nullable=False, server_default="./download"
    )
    default_subtitle_language: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    default_video_quality: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self):
        return f"<GlobalSettings(id={self.id}, path={self.default_download_path})>"
