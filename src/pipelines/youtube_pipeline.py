import yaml
import logging
from typing import Dict, Any, List
from src.models.source_tracker import SourceTracker
from src.models.youtube_finder import YouTubeVideoFinder
from src.models.transcript_fetcher import TranscriptFetcher
from src.models.yt_channel_resolver import YouTubeChannelResolver
from src.models.llm_writer import LLMWriter
from src.utils.json_builder import JSONBuilder

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

    def process_single_channel(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handles the logic for a single source entry."""
        items = []
        channel_url = source.get("url")
        last_checked = source.get("last_checked")

        try:
            channel_id = self.channel_resolver.get_channel_id(channel_url)
            # Use 24-hour window instead of last_checked to avoid stale dates from CSV
            videos = self.video_finder.find_new_videos(channel_id, hours=24)

            for video in videos:
                logger.info(f"Processing video: {video['title']}")
                transcript = self.transcript_fetcher.fetch_and_clean(
                    video_id=video["video_id"], title=video["title"]
                )
                if transcript:
                    logger.info(f"Transcript fetched, generating summary...")
                    res = self.llm_writer.process_content(
                        video["title"], transcript["clean_text"]
                    )
                    items.append(
                        JSONBuilder.build_item(
                            item_type="youtube",
                            title=res["title"],
                            summary=res["summary"],
                            link=video["link"],
                        )
                    )
                    logger.info(f"Summary generated for: {video['title']}")
                else:
                    logger.warning(f"No transcript available for: {video['title']}")

            logger.info(f"Processed {len(items)} items from channel")
            return items
        except Exception as e:
            logger.error(f"Error processing channel {channel_url}: {e}", exc_info=True)
            return []

    def run(self) -> Dict[str, Any]:
        """Main execution loop for all sources."""
        logger.info("\n" + "=" * 80)
        logger.info("YOUTUBE PIPELINE STARTED")
        logger.info("=" * 80)

        all_items = []
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
                logger.info(f"  {idx}. {item['title']}")
        logger.info("=" * 80 + "\n")


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
    print(f"\nDaily Digest Generated: {result['date']}")
    print(f"Total Items: {len(result['items'])}")
    print("=" * 60)

    for idx, item in enumerate(result["items"], 1):
        print(f"\n[{idx}] {item['title']}")
        print(f"Type: {item['type']}")
        print(f"Link: {item['link']}")
        print(f"Summary:\n{item['summary']}")
        print("-" * 60)

    # Save to file
    output_file = "daily_digest.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Results saved to {output_file}")
