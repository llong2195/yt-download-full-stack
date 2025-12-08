"""Channel model representing YouTube channels."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from .database import Base


class Channel(Base):
    """YouTube channel tracked by the user."""

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    download_path: Mapped[str] = mapped_column(String(2000), nullable=False)
    date_added: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Channel(id={self.id}, name={self.name}, channel_id={self.channel_id})>"
