from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class VideoMetadata(BaseModel):
    """Output for YouTubeVideoFinder"""
    video_id: str
    title: str
    published_at: str
    channel: str
    link: str

class TranscriptData(BaseModel):
    """Output for TranscriptFetcher"""
    video_id: str
    title: str
    clean_text: str
    link: Optional[str] = None

class VideoSummary(BaseModel):
    """Output for LLMWriter"""
    title: str
    summary: str

class NewsletterItem(BaseModel):
    """Final Output Item for Pipeline"""
    type: str = "youtube"
    title: str
    summary: str
    link: str

class PipelineResult(BaseModel):
    """Complete Pipeline Result"""
    date: str
    count: int
    items: List[NewsletterItem]
