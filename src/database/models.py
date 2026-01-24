from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class TimeStampedModel(Base):
    """Abstract base model with timestamp."""
    __abstract__ = True
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Channel(TimeStampedModel):
    """
    YouTube Channel Model.
    PK: channel_id (Natural Key, e.g. "UC...")
    """
    __tablename__ = "channels"

    channel_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    url = Column(String, unique=True, nullable=False)
    last_checked = Column(DateTime, nullable=True)

class VideoSummary(TimeStampedModel):
    """
    Video Summary Model.
    PK: video_id (Natural Key, e.g. "dQw4...")
    """
    __tablename__ = "video_summaries"

    video_id = Column(String, primary_key=True, index=True)
    channel_id = Column(String, ForeignKey("channels.channel_id"), nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    link = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
