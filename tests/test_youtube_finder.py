"""
Unit tests for YouTubeVideoFinder module.

Tests the RSS-based YouTube video finder with real and mocked data.
"""

import unittest
import sys
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.models.youtube_finder import YouTubeVideoFinder
from src.models.source_tracker import SourceTracker


class TestYouTubeVideoFinderUnit(unittest.TestCase):
    """Unit tests for YouTubeVideoFinder class."""

    def setUp(self):
        """Set up test fixtures."""
        self.finder = YouTubeVideoFinder()
        self.test_channel_id = "UCXuqSBlHAE6Xw-yeJA0Tunw"  # Linus Tech Tips

    def test_initialization(self):
        """Test that YouTubeVideoFinder initializes correctly."""
        self.assertIsNotNone(self.finder)
        self.assertEqual(
            self.finder.base_rss_url,
            "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}",
        )

    def test_rss_url_construction(self):
        """Test that RSS URL is constructed correctly."""
        expected_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={self.test_channel_id}"
        constructed_url = self.finder.base_rss_url.format(
            channel_id=self.test_channel_id
        )
        self.assertEqual(constructed_url, expected_url)

    @patch("models.youtube_finder.requests.get")
    @patch("models.youtube_finder.feedparser.parse")
    def test_find_new_videos_with_mock_data(self, mock_parse, mock_get):
        """Test finding videos with mocked RSS feed data."""
        # Mock RSS response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<feed>...</feed>"
        mock_get.return_value = mock_response

        # Mock parsed feed with recent video
        now = datetime.now(timezone.utc)
        recent_time = now - timedelta(hours=12)

        mock_feed = Mock()
        mock_feed.feed.title = "Test Channel"
        mock_feed.entries = [
            Mock(
                title="Test Video",
                published=recent_time.isoformat(),
                yt_videoid="test123",
                link="https://www.youtube.com/watch?v=test123",
            )
        ]
        mock_parse.return_value = mock_feed

        # Execute
        videos = self.finder.find_new_videos(self.test_channel_id, hours=24)

        # Assert
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]["video_id"], "test123")
        self.assertEqual(videos[0]["title"], "Test Video")
        self.assertEqual(videos[0]["channel"], "Test Channel")
        mock_get.assert_called_once()

    @patch("models.youtube_finder.requests.get")
    @patch("models.youtube_finder.feedparser.parse")
    def test_find_new_videos_filters_old_videos(self, mock_parse, mock_get):
        """Test that old videos are filtered out."""
        # Mock RSS response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<feed>...</feed>"
        mock_get.return_value = mock_response

        # Mock feed with old video (25 hours ago)
        now = datetime.now(timezone.utc)
        old_time = now - timedelta(hours=25)

        mock_feed = Mock()
        mock_feed.feed.title = "Test Channel"
        mock_feed.entries = [
            Mock(
                title="Old Video",
                published=old_time.isoformat(),
                yt_videoid="old123",
                link="https://www.youtube.com/watch?v=old123",
            )
        ]
        mock_parse.return_value = mock_feed

        # Execute - should return empty list
        videos = self.finder.find_new_videos(self.test_channel_id, hours=24)

        # Assert
        self.assertEqual(len(videos), 0)

    @patch("models.youtube_finder.requests.get")
    def test_handles_network_error(self, mock_get):
        """Test that network errors are handled gracefully."""
        # Mock network error
        mock_get.side_effect = Exception("Network error")

        # Execute
        videos = self.finder.find_new_videos(self.test_channel_id)

        # Assert - should return empty list, not crash
        self.assertEqual(videos, [])

    def test_output_structure(self):
        """Test that output has correct structure."""
        with (
            patch("models.youtube_finder.requests.get") as mock_get,
            patch("models.youtube_finder.feedparser.parse") as mock_parse,
        ):

            # Mock data
            mock_response = Mock()
            mock_response.content = b"<feed>...</feed>"
            mock_get.return_value = mock_response

            now = datetime.now(timezone.utc)
            recent_time = now - timedelta(hours=1)

            mock_feed = Mock()
            mock_feed.feed.title = "Test Channel"
            mock_feed.entries = [
                Mock(
                    title="Test Video",
                    published=recent_time.isoformat(),
                    yt_videoid="abc123",
                    link="https://www.youtube.com/watch?v=abc123",
                )
            ]
            mock_parse.return_value = mock_feed

            # Execute
            videos = self.finder.find_new_videos(self.test_channel_id)

            # Assert structure
            self.assertIsInstance(videos, list)
            if videos:
                video = videos[0]
                self.assertIn("video_id", video)
                self.assertIn("title", video)
                self.assertIn("published_at", video)
                self.assertIn("channel", video)
                self.assertIn("link", video)


class TestYouTubeVideoFinderIntegration(unittest.TestCase):
    """Integration tests with CSV file."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_csv_path = os.path.join(
            os.path.dirname(__file__), "test_youtube_sources.csv"
        )
        self.tracker = SourceTracker(self.test_csv_path)
        self.finder = YouTubeVideoFinder()

    def test_load_source_from_csv(self):
        """Test loading source from CSV file."""
        sources = self.tracker.get_active_sources("youtube")

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["source_id"], "yt_test_001")
        self.assertEqual(sources[0]["type"], "youtube")
        self.assertIn("UC", sources[0]["url_or_id"])

    def test_csv_to_finder_flow(self):
        """Test complete flow: CSV → SourceTracker → YouTubeVideoFinder."""
        # Load sources from CSV
        sources = self.tracker.get_active_sources("youtube")
        self.assertGreater(len(sources), 0)

        # Get first source
        source = sources[0]
        channel_id = source["url_or_id"]
        last_checked = source["last_checked"]

        # Mock the finder to avoid real API calls in tests
        with (
            patch("models.youtube_finder.requests.get") as mock_get,
            patch("models.youtube_finder.feedparser.parse") as mock_parse,
        ):

            mock_response = Mock()
            mock_response.content = b"<feed>...</feed>"
            mock_get.return_value = mock_response

            now = datetime.now(timezone.utc)
            recent_time = now - timedelta(hours=2)

            mock_feed = Mock()
            mock_feed.feed.title = source["name"]
            mock_feed.entries = [
                Mock(
                    title="Recent Test Video",
                    published=recent_time.isoformat(),
                    yt_videoid="test456",
                    link="https://www.youtube.com/watch?v=test456",
                )
            ]
            mock_parse.return_value = mock_feed

            # Find videos
            videos = self.finder.find_new_videos(channel_id, hours=24)

            # Assert
            self.assertIsInstance(videos, list)
            print(f"\nFound {len(videos)} video(s) from channel: {source['name']}")
            for video in videos:
                print(f"  - {video['title']} (ID: {video['video_id']})")


class TestYouTubeVideoFinderLive(unittest.TestCase):
    """
    Live tests with real RSS feeds.

    These tests make real network requests and should be run separately.
    Use: python -m unittest tests.test_youtube_finder.TestYouTubeVideoFinderLive
    """

    @unittest.skip("Live test - enable manually for real RSS feed testing")
    def test_real_rss_feed(self):
        """Test with real YouTube RSS feed (Linus Tech Tips)."""
        finder = YouTubeVideoFinder()
        channel_id = "UCXuqSBlHAE6Xw-yeJA0Tunw"  # Linus Tech Tips

        videos = finder.find_new_videos(channel_id, hours=168)  # Last week

        print(f"\nReal RSS Feed Test Results:")
        print(f"Channel ID: {channel_id}")
        print(f"Videos found: {len(videos)}")

        for video in videos[:3]:  # Print first 3
            print(f"\n  Title: {video['title']}")
            print(f"  Video ID: {video['video_id']}")
            print(f"  Published: {video['published_at']}")
            print(f"  Link: {video['link']}")

        # Assert we got some results
        self.assertIsInstance(videos, list)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
