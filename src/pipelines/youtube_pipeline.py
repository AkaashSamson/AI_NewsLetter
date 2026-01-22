"""
YouTubePipeline Module
Role: Orchestrates the complete YouTube content processing pipeline using LLMWriter for summarization.
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
from models.llm_writer import LLMWriter
from models.yt_channel_resolver import YouTubeChannelResolver
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
            youtube_api_key: (Unused now but kept for compatibility)
            groq_api_key: Groq API key for LLM
            sources_file: Path to sources CSV file
            groq_model: Groq model to use
        """
        self.source_tracker = SourceTracker(sources_file)
        self.video_finder = YouTubeVideoFinder()  # RSS based, no API key needed
        self.channel_resolver = YouTubeChannelResolver()
        self.transcript_fetcher = TranscriptFetcher()
        # Initialize LLMWriter with Groq provider
        self.llm_writer = LLMWriter(
            provider="groq", model=groq_model, api_key=groq_api_key
        )

    def process_all_youtube_sources(self) -> Dict[str, Any]:
        """
        Process all YouTube sources and return final JSON.

        Returns:
            JSON structure with processed items
        """
        all_items = []

        # Get all sources (simple list)
        youtube_sources = self.source_tracker.get_sources()

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
        source_id = source.get("id")
        name = source.get("name")
        channel_url = source.get("url")
        last_checked = source.get("last_checked")

        items = []

        # Step 1: Resolve Channel ID from URL
        print(f"  Resolving ID for {channel_url}...")
        try:
            channel_id = self.channel_resolver.get_channel_id(channel_url)
        except Exception as e:
            print(f"  Error resolving channel for {name}: {e}")
            return items

        # Step 2: Find new videos (filtering by last_checked happens inside finder)
        print(f"  Finding new videos since {last_checked}...")
        videos = self.video_finder.find_new_videos(
            channel_id=channel_id, last_checked=last_checked
        )

        if not videos:
            print(f"  No new videos found")
            return items

        print(f"  Found {len(videos)} new video(s)")

        # Track latest video timestamp found
        max_published_at = last_checked

        # Step 3: Process each video
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

            # Summarize with LLMWriter
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

            # Update max date if this video is newer
            if video["published_at"] > max_published_at:
                max_published_at = video["published_at"]

        # Update last_checked in CSV if we found a later date
        if max_published_at > last_checked:
            self.source_tracker.update_last_checked(source_id, max_published_at)
            print(f"  Updated last_checked to {max_published_at}")

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
        youtube_api_key: YouTube API key (unused but kept for param compatibility)
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
