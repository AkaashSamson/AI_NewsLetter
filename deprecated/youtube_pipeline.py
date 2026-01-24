import yaml
import logging
from typing import Dict, Any, List
from datetime import datetime
from src.models.source_tracker import SourceTracker
from src.models.youtube_finder import YouTubeVideoFinder
from src.models.transcript_fetcher import TranscriptFetcher
from src.models.yt_channel_resolver import YouTubeChannelResolver
from src.models.llm_writer import LLMWriter
from src.schemas.youtube import NewsletterItem, PipelineResult

logger = logging.getLogger(__name__)


class YouTubePipeline:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.source_tracker = SourceTracker(self.config["pipeline"]["sources_file"])
        self.video_finder = YouTubeVideoFinder()
        self.channel_resolver = YouTubeChannelResolver()
        self.transcript_fetcher = TranscriptFetcher()
        self.llm_writer = LLMWriter(config_path=config_path)

    def process_single_channel(self, source: Dict[str, Any]) -> List[NewsletterItem]:
        """Handles the logic for a single source entry."""
        items = []
        channel_url = source.get("url")
        last_checked = source.get("last_checked")

        # Get rate limiting config
        max_videos = self.config.get("rate_limiting", {}).get("max_videos_per_run", 10)

        try:
            channel_id = self.channel_resolver.get_channel_id(channel_url)
            # Use configured lookback hours
            lookback_hours = self.config.get("pipeline", {}).get(
                "video_lookback_hours", 24
            )
            # returns List[VideoMetadata]
            videos = self.video_finder.find_new_videos(channel_id, hours=lookback_hours)

            # Limit number of videos to process
            if len(videos) > max_videos:
                logger.warning(
                    f"  ⚠ Found {len(videos)} videos, but limiting to {max_videos} to avoid rate limits"
                )
                videos = videos[:max_videos]

            for video in videos:
                logger.info(f"Processing video: {video.title}")
                # returns TranscriptData | None
                transcript = self.transcript_fetcher.fetch_and_clean(
                    video_id=video.video_id, title=video.title
                )
                if transcript:
                    logger.info(f"Transcript fetched, generating summary...")
                    # returns VideoSummary
                    res = self.llm_writer.process_content(
                        video.title, transcript.clean_text
                    )
                    
                    item = NewsletterItem(
                        type="youtube",
                        title=res.title,
                        summary=res.summary,
                        link=video.link
                    )
                    items.append(item)
                    logger.info(f"Summary generated for: {video.title}")
                else:
                    logger.warning(f"No transcript available for: {video.title}")

            logger.info(f"Processed {len(items)} items from channel")
            return items
        except Exception as e:
            logger.error(f"Error processing channel {channel_url}: {e}", exc_info=True)
            return []

    def run(self) -> PipelineResult:
        """Main execution loop for all sources."""
        logger.info("\n" + "=" * 80)
        logger.info("YOUTUBE PIPELINE STARTED")
        logger.info("=" * 80)

        all_items: List[NewsletterItem] = []
        sources = self.source_tracker.get_sources()
        logger.info(f"\nTotal sources to process: {len(sources)}")

        for idx, source in enumerate(sources, 1):
            logger.info(f"\n{'#'*80}")
            logger.info(f"SOURCE {idx}/{len(sources)}: {source.get('name', 'Unknown')}")
            logger.info(f"{'#'*80}")
            channel_items = self.process_single_channel(source)
            all_items.extend(channel_items)

        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETE")
        logger.info(f"Total items generated: {len(all_items)}")
        
        if all_items:
            logger.info("\nGenerated items:")
            for idx, item in enumerate(all_items, 1):
                logger.info(f"  {idx}. {item.title}")
        logger.info("=" * 80 + "\n")
        
        return PipelineResult(
            date=datetime.now().strftime("%Y-%m-%d"),
            count=len(all_items),
            items=all_items
        )


if __name__ == "__main__":
    import json
    from src.utils.logger import setup_logging

    # Setup industry-grade logging
    setup_logging(
        log_level="INFO",  # Change to DEBUG for more detailed logs
        log_dir="logs",
        console=True,
    )

    logger.info("Initializing YouTube Pipeline...")

    # Initialize the pipeline with actual config
    pipeline = YouTubePipeline(config_path="src/config/config.yaml")
    print("Starting YouTube Pipeline...")
    print("=" * 60)

    # Run the pipeline with real YouTube sources
    result = pipeline.run()

    # Display results
    print(f"\nDaily Digest Generated: {result.date}")
    print(f"Total Items: {result.count}")
    print("=" * 60)

    for idx, item in enumerate(result.items, 1):
        print(f"\n[{idx}] {item.title}")
        print(f"Type: {item.type}")
        print(f"Link: {item.link}")
        print(f"Summary:\n{item.summary}")
        print("-" * 60)

    # Save to file
    output_file = "daily_digest.json"
    with open(output_file, "w", encoding="utf-8") as f:
        # Convert Pydantic model to JSON string
        f.write(result.model_dump_json(indent=2))

    print(f"\n✓ Results saved to {output_file}")
