"""
AI Newsletter - Pipelines Package
Orchestration layer for processing workflows
"""

from .youtube_pipeline import YouTubePipeline, main_youtube_pipeline

__all__ = [
    "YouTubePipeline",
    "main_youtube_pipeline",
]
