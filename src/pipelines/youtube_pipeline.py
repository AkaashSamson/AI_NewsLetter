"""
YouTubePipeline Module
Role: Orchestrates the complete YouTube content processing pipeline using Groq for summarization.
"""

from typing import List, Dict, Any
from datetime import datetime

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.source_tracker import SourceTracker
from models.youtube_finder import YouTubeVideoFinder
from models.transcript_fetcher import TranscriptFetcher
from models.groq_news_writer import GroqNewsWriter
from utils.text_cleaner import TextCleaner
from utils.json_builder import JSONBuilder


class YouTubePipeline:
    """Orchestrates the complete YouTube processing pipeline."""

    def __init__(
        self,
        youtube_api_key: str = None,
        groq_api_key: str = None,
        sources_file: str = "youtube_sources.csv",
        groq_model: str = "llama-3.3-70b-versatile",
    ):
        """
        Initialize the YouTube pipeline.

        Args:
            youtube_api_key: YouTube API key
            groq_api_key: Groq API key for LLM
            sources_file: Path to sources CSV file
            groq_model: Groq model to use
        """
        self.source_tracker = SourceTracker(sources_file)
        self.video_finder = YouTubeVideoFinder(api_key=youtube_api_key)
        self.transcript_fetcher = TranscriptFetcher()
        self.llm_writer = GroqNewsWriter(model=groq_model, api_key=groq_api_key)

    def process_all_youtube_sources(self) -> Dict[str, Any]:
        """
        Process all YouTube sources and return final JSON.

        Returns:
            JSON structure with processed items
        """
        all_items = []

        youtube_sources = self.source_tracker.get_active_sources("youtube")

        for source in youtube_sources:
            print(f"\nProcessing: {source.get('name')}")
            items = self.process_single_channel(source)
            all_items.extend(items)

        # Build final JSON
        final_json = JSONBuilder.build_daily_digest(all_items)

        return final_json

    def process_single_channel(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a single YouTube channel.

        Args:
            source: Source dict from CSV

        Returns:
            List of processed news items
        """
        channel_id = source.get("url_or_id")
        source_id = source.get("source_id")
        last_checked = source.get("last_checked")

        items = []

        # Step 1: Find new videos
        print(f"  Finding new videos...")
        videos = self.video_finder.find_new_videos(
            channel_id=channel_id, last_checked=last_checked
        )

        if not videos:
            print(f"  No new videos found")
            return items

        print(f"  Found {len(videos)} new video(s)")

        # Step 2-4: Process each video
        for video in videos:
            print(f"  Processing: {video['title'][:50]}...")

            # Fetch and clean transcript
            transcript_data = self.transcript_fetcher.fetch_and_clean(
                video_id=video["video_id"], title=video["title"], link=video["link"]
            )

            if not transcript_data:
                print(f"    Skipped (no transcript)")
                continue

            # Clean the text further
            clean_text = TextCleaner.clean_full(transcript_data["clean_text"])

            # Summarize with Groq LLM
            print(f"    Summarizing with Groq...")
            summary_result = self.llm_writer.process_content(
                title=video["title"], text=clean_text
            )

            # Build final item
            item = JSONBuilder.build_item(
                item_type="youtube",
                title=summary_result["title"],
                summary=summary_result["summary"],
                link=video["link"],  # REAL link from original source
            )

            items.append(item)

        # Update last_checked
        self.source_tracker.update_last_checked(source_id)
        print(f"  Updated last_checked for {source_id}")

        return items


def main_youtube_pipeline(
    youtube_api_key: str = None,
    groq_api_key: str = None,
    output_file: str = "daily_digest.json",
    groq_model: str = "llama-3.3-70b-versatile",
):
    """
    Run the complete YouTube pipeline.

    Args:
        youtube_api_key: YouTube API key
        groq_api_key: Groq API key
        output_file: Output JSON file path
        groq_model: Groq model to use

    Returns:
        The generated JSON data
    """
    print("Starting YouTube Pipeline with Groq...")

    pipeline = YouTubePipeline(
        youtube_api_key=youtube_api_key,
        groq_api_key=groq_api_key,
        groq_model=groq_model,
    )

    result_json = pipeline.process_all_youtube_sources()

    # Save to file
    print(f"\nSaving results to {output_file}...")
    JSONBuilder.save_to_file(result_json, output_file)

    print(f"✓ Pipeline complete. Generated {result_json['count']} items")

    return result_json
