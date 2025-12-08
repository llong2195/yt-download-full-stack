"""Channel model representing YouTube channels."""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base


class Channel(Base):
    """YouTube channel tracked by the user."""

    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    download_path = Column(String(2000), nullable=False)
    date_added = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Channel(id={self.id}, name={self.name}, channel_id={self.channel_id})>"
