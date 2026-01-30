import logging
import random
import time
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database import crud, models
from src.services.youtube_finder import YouTubeVideoFinder
from src.services.transcript_fetcher import TranscriptFetcher
from src.services.llm_writer import LLMWriter
from src.config.settings import settings
from src.schemas.youtube import VideoMetadata

logger = logging.getLogger(__name__)


class FeedManager:
    """
    Service for polling feeds and processing new videos.
    Enforces global rate limits and deduplication.
    """

    def __init__(self, db: Session):
        self.db = db
        self.finder = YouTubeVideoFinder()
        self.fetcher = TranscriptFetcher()
        self.writer = LLMWriter(
            config_path="src/config/config.yaml"
        )  # TODO: Refactor config path

    def run_polling_cycle(self):
        """
        Main execution loop.
        1. Scan all channels for new videos.
        2. Filter out already processed videos (Deduplication).
        3. Apply Global Rate Limit (Max N videos).
        4. Process remaining candidates.
        """
        logger.info("Starting Polling Cycle...")
        channels = crud.get_all_channels(self.db)
        if not channels:
            logger.info("No channels to monitor.")
            return

        # 1. Gather Candidates
        candidates: List[dict] = []  # stores (channel_obj, video_metadata)

        for channel in channels:
            # Look back 24h by default, or verify against DB last_checked
            # Note: finder returns schema objects now
            videos = self.finder.find_new_videos(channel.channel_id, hours=24)

            for video in videos:
                # 2. Deduplication check against DB
                if not crud.get_summary_by_video_id(self.db, video.video_id):
                    # Also check timestamp > channel.last_checked if desired,
                    # but DB existence is the ultimate truth.
                    candidates.append({"channel": channel, "video": video})

        logger.info(
            f"Found {len(candidates)} new candidates across {len(channels)} channels."
        )

        # 3. Apply Global Rate Limit
        limit = settings.MAX_VIDEOS_PER_RUN
        if len(candidates) > limit:
            logger.warning(
                f"Rate Limiting: Processing only {limit} of {len(candidates)} videos."
            )
            candidates = candidates[:limit]

        # 4. Process
        for item in candidates:
            video: VideoMetadata = item["video"]
            channel: models.Channel = item["channel"]

            self._process_single_video(channel, video)

            # Randomized Jitter between videos (Protection against YT Bot detection)
            jitter = random.uniform(3.0, 7.0)
            logger.info(f"Sleeping {jitter:.1f}s...")
            time.sleep(jitter)

    def _process_single_video(self, channel: models.Channel, video: VideoMetadata):
        """Fetch transcript, Summarize, and Save."""
        logger.info(f"Processing: {video.title}")

        transcript_data = self.fetcher.fetch_and_clean(video.video_id, video.title)

        if not transcript_data:
            logger.warning(f"Skipping {video.video_id} (No transcript)")
            # Might want to mark as 'failed' in DB to avoid infinite retries?
            # For now, we skip. It will be picked up again next run if we don't save it.
            # To prevent loops, maybe we should save a 'failed' record.
            # User requirement: Simple tables. We just skip for now.
            return

        # LLM Summary
        # Note: LLMWriter currently takes config_path.
        # Ideally it should take settings or just the key.
        summary_result = self.writer.process_content(
            video.title, transcript_data.clean_text
        )

        # Save to DB
        crud.create_summary(
            self.db,
            video_id=video.video_id,
            channel_id=channel.channel_id,
            title=summary_result.title,
            summary=summary_result.summary,
            link=video.link,
            published_at=datetime.fromisoformat(
                video.published_at.replace("Z", "+00:00")
            ),  # Basic parsing fallback
        )

        # Update Channel Timestamp
        # We update strictly to the published_at of the processed video.
        # Since we process chronological or filtered, this moves the cursor forward.
        published_dt = datetime.fromisoformat(video.published_at.replace("Z", "+00:00"))
        crud.update_channel_last_checked(self.db, channel.channel_id, published_dt)
        logger.info(f"Display: Saved summary for {video.title}")
