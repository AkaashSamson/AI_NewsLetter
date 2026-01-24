from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from typing import List, Optional, Type
from datetime import datetime, timezone

from src.database.models import Channel, VideoSummary

# --- Channel Operations ---
def create_channel(db: Session, channel_id: str, url: str, name: str = None) -> Channel:
    """Create a new channel entry."""
    db_channel = Channel(channel_id=channel_id, url=url, name=name)
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel

def get_channel_by_id(db: Session, channel_id: str) -> Optional[Channel]:
    return db.query(Channel).filter(Channel.channel_id == channel_id).first()

def get_channel_by_url(db: Session, url: str) -> Optional[Channel]:
    return db.query(Channel).filter(Channel.url == url).first()

def get_all_channels(db: Session) -> List[Channel]:
    return db.query(Channel).all()

def update_channel_last_checked(db: Session, channel_id: str, timestamp: datetime) -> None:
    channel = get_channel_by_id(db, channel_id)
    if channel:
        channel.last_checked = timestamp
        db.commit()

# --- Summary Operations ---
def create_summary(
    db: Session, 
    video_id: str, 
    channel_id: str, 
    title: str, 
    summary: str, 
    link: str, 
    published_at: datetime
) -> VideoSummary:
    """Create a new video summary."""
    db_summary = VideoSummary(
        video_id=video_id,
        channel_id=channel_id,
        title=title,
        summary=summary,
        link=link,
        published_at=published_at
    )
    db.add(db_summary)
    db.commit()
    return db_summary

def get_summary_by_video_id(db: Session, video_id: str) -> Optional[VideoSummary]:
    return db.query(VideoSummary).filter(VideoSummary.video_id == video_id).first()

def get_latest_summaries(db: Session, limit: int = 20) -> List[VideoSummary]:
    """Get latest summaries ordered by processing time (created_at)."""
    return db.query(VideoSummary).order_by(desc(VideoSummary.created_at)).limit(limit).all()
