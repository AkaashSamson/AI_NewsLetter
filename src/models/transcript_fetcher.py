"""
TranscriptFetcher Module
Role: Fetch YouTube transcripts and clean them.
"""

from typing import Dict, Any, Optional
from src.schemas.youtube import TranscriptData
import re
import json
import sys
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMIT_DELAY = 2  # seconds between requests
RATE_LIMIT_ENABLED = True


def rate_limit(func):
    """Decorator to add rate limiting to transcript fetches"""
    last_call = {"time": 0}

    @wraps(func)
    def wrapper(*args, **kwargs):
        if RATE_LIMIT_ENABLED:
            elapsed = time.time() - last_call["time"]
            if elapsed < RATE_LIMIT_DELAY:
                sleep_time = RATE_LIMIT_DELAY - elapsed
                logger.info(
                    f"  Rate limiting: waiting {sleep_time:.1f}s before next request..."
                )
                time.sleep(sleep_time)
            last_call["time"] = time.time()
        return func(*args, **kwargs)

    return wrapper


try:
    from youtube_transcript_api import YouTubeTranscriptApi

    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False


class TranscriptFetcher:
    """Fetches and cleans YouTube video transcripts."""

    # Common filler words/sounds to remove
    FILLER_WORDS = {
        "um",
        "uh",
        "like",
        "you know",
        "basically",
        "literally",
        "actually",
        "honestly",
        "right",
        "so",
        "yeah",
        "okay",
        "alright",
        "well",
    }

    def __init__(self):
        """Initialize TranscriptFetcher."""
        if not TRANSCRIPT_API_AVAILABLE:
            raise RuntimeError(
                "youtube-transcript-api not installed. Install with: pip install youtube-transcript-api"
            )

    @rate_limit
    def fetch_transcript(self, video_id: str, languages: list = None) -> str | None:
        """
        Fetch transcript for a YouTube video.

        Args:
            video_id: YouTube video ID
            languages: List of language codes to try (e.g., ['en', 'es'])

        Returns:
            Transcript text or None if not available
        """
        if not TRANSCRIPT_API_AVAILABLE:
            raise RuntimeError("youtube-transcript-api not installed")

        if languages is None:
            languages = ["en"]

        logger.info(
            f"Fetching transcript for video: {video_id} (languages: {languages})"
        )

        try:

            # transcript = YouTubeTranscriptApi.fetch(video_id, languages=languages)
            ytt_api = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(video_id, languages=languages)
            # Merge transcript entries into continuous text
            text = " ".join([entry.text for entry in transcript])
            logger.info(f"Transcript fetched successfully ({len(text)} characters)")
            return text

        except Exception as e:
            logger.error(f"Could not fetch transcript for video {video_id}: {e}")
            return None

    def clean_transcript(self, text: str) -> str:
        """
        Clean raw transcript text.

        Operations:
        - Remove timestamps and brackets
        - Normalize spaces
        - Remove filler words at start of sentences
        - Remove repeated punctuation

        Args:
            text: Raw transcript text

        Returns:
            Cleaned text
        """
        # if not text:
        #     return ""

        # # Remove bracketed content (like [Music], [Applause])
        # text = re.sub(r"\[.*?\]", "", text)

        # # Remove multiple spaces
        # text = re.sub(r"\s+", " ", text)

        # # Remove repeated punctuation
        # text = re.sub(r"\.{2,}", ".", text)
        # text = re.sub(r"!{2,}", "!", text)
        # text = re.sub(r"\?{2,}", "?", text)

        # # Clean up filler words at the beginning of sentences
        # text = self._remove_filler_words(text)

        # # Normalize spacing around punctuation
        # text = re.sub(r"\s+([.,!?;:])", r"\1", text)
        # text = re.sub(r"([.,!?;:])\s*([a-zA-Z])", r"\1 \2", text)

        return text.strip()

    def _remove_filler_words(self, text: str) -> str:
        """Remove filler words at the beginning of sentences."""
        sentences = text.split(". ")
        cleaned_sentences = []

        for sentence in sentences:
            words = sentence.split()
            # Remove leading filler words
            while words and words[0].lower().rstrip(",") in self.FILLER_WORDS:
                words.pop(0)

            if words:
                cleaned_sentences.append(" ".join(words))

        return ". ".join(cleaned_sentences)



    def fetch_and_clean(
        self, video_id: str, title: str, link: str = None, languages: list = None
    ) -> Optional[TranscriptData]:
        """
        Fetch and clean transcript in one call.

        Args:
            video_id: YouTube video ID
            title: Video title
            link: Video link (optional)
            languages: Language preferences

        Returns:
            TranscriptData object or None
        """
        logger.info(f"  Fetching transcript for video ID: {video_id}")
        raw_text = self.fetch_transcript(video_id, languages)

        if raw_text is None:
            logger.warning(f"  ✗ No transcript available")
            return None

        logger.info(f"  Raw transcript: {len(raw_text)} characters")
        clean_text = self.clean_transcript(raw_text)
        logger.info(f"  ✓ Cleaned transcript: {len(clean_text)} characters")
        logger.debug(f"  Transcript preview: {clean_text[:200]}...")

        return TranscriptData(
            video_id=video_id,
            title=title,
            clean_text=clean_text,
            link=link,
        )


if __name__ == "__main__":
    """Quick manual test for fetching a transcript."""
    video_id = "sPU6wVz2iE8"  # sample video id
    fetcher = TranscriptFetcher()
    transcript = fetcher.fetch_transcript(video_id)
    if transcript:
        print(json.dumps({"video_id": video_id, "excerpt": transcript[:500]}, indent=2))
    else:
        sys.exit(1)

    # from youtube_transcript_api import YouTubeTranscriptApi

    # ytt_api = YouTubeTranscriptApi()
    # fetched_transcript = ytt_api.fetch(video_id, languages = ["en"])
    # print(fetched_transcript[0])
