"""
YouTubeVideoFinder Module
Role: Detect new YouTube videos within last 24 hours from monitored channels.
Uses RSS feeds - no API key required.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import json
import logging
import requests
import feedparser
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)


class YouTubeVideoFinder:
    """
    Finds new videos from YouTube channels using RSS feeds.

    No API key required - uses public YouTube RSS feeds.
    """

    def __init__(self):
        """Initialize YouTubeVideoFinder."""
        self.base_rss_url = (
            "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        )

    def find_new_videos(
        self, channel_id: str, hours: int = 24, last_checked: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find new videos from a channel published in the last N hours.

        Args:
            channel_id: YouTube channel ID (format: UCxxxxxxxxxxxxx)
            hours: Number of hours to look back (default: 24)
            last_checked: ISO format timestamp to filter from (overrides hours)

        Returns:
            List of video dicts with fields:
            - video_id: YouTube video ID
            - title: Video title
            - published_at: ISO format timestamp
            - channel: Channel name
            - link: Full YouTube URL
        """
        # Determine cutoff time
        if last_checked:
            cutoff_time = datetime.fromisoformat(last_checked.replace("Z", "+00:00"))
            logger.info(f"Using last_checked time: {cutoff_time}")
        else:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            logger.info(f"Using relative time: {hours} hours ago = {cutoff_time}")

        rss_url = self.base_rss_url.format(channel_id=channel_id)
        logger.info(f"Fetching RSS feed from: {rss_url}")

        videos = []

        try:
            # Construct RSS feed URL
            rss_url = self.base_rss_url.format(channel_id=channel_id)

            # Fetch RSS feed
            response = requests.get(rss_url, timeout=10)
            response.raise_for_status()

            # Parse feed
            feed = feedparser.parse(response.content)

            # Extract channel name from feed
            channel_name = feed.feed.get("title", "Unknown Channel")
            logger.info(f"Channel: {channel_name}")
            logger.info(f"Total entries in RSS feed: {len(feed.entries)}")

            # Process entries
            for entry in feed.entries:
                # Parse published date
                # YouTube RSS uses 'published' field in format: 2026-01-22T12:34:56+00:00
                published_str = entry.get("published", "")

                if not published_str:
                    continue

                try:
                    # Parse the published timestamp
                    published_at = datetime.fromisoformat(
                        published_str.replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    # Fallback to parsedate if ISO format fails
                    try:
                        published_at = parsedate_to_datetime(published_str)
                    except:
                        continue

                video_title = entry.get("title", "Untitled")
                is_new = published_at > cutoff_time

                if is_new:
                    logger.info(f"  ✓ New video found: '{video_title}'")
                    logger.info(f"    Published: {published_at}")
                else:
                    logger.debug(
                        f"  ✗ Old video (before cutoff): '{video_title}' | {published_at}"
                    )

                # Filter by cutoff time
                if published_at > cutoff_time:
                    # Extract video ID from link
                    video_id = entry.get("yt_videoid", "")
                    if not video_id:
                        # Fallback: extract from link
                        link = entry.get("link", "")
                        if "watch?v=" in link:
                            video_id = link.split("watch?v=")[1].split("&")[0]

                    video_data = {
                        "video_id": video_id,
                        "title": entry.get("title", "Untitled"),
                        "published_at": published_str,
                        "channel": channel_name,
                        "link": entry.get(
                            "link", f"https://www.youtube.com/watch?v={video_id}"
                        ),
                    }
                    videos.append(video_data)
                    logger.info(f"    Video ID: {video_id}")

            logger.info(f"\\n{'─'*60}")
            logger.info(f"SUMMARY: Found {len(videos)} new video(s) after cutoff time")
            logger.info(f"{'─'*60}")

        except requests.RequestException as e:
            logger.error(f"Error fetching RSS feed for channel {channel_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing RSS feed for channel {channel_id}: {e}")
            return []

        return videos


if __name__ == "__main__":
    """Quick manual test for the module."""
    channel_id = "UCbRP3c757lWg9M-U7TyEkXA"  # Sample channel
    finder = YouTubeVideoFinder()
    videos = finder.find_new_videos(channel_id, hours=24)
    print(json.dumps(videos, indent=2))
