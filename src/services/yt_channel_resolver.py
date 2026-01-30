import requests
import re
import logging

logger = logging.getLogger(__name__)


class YouTubeChannelResolver:
    # This matches ONLY the owner channel id
    CHANNEL_ID_REGEX = re.compile(r'"externalId":"(UC[a-zA-Z0-9_-]{22})"')

    def __init__(self, timeout=10):
        self.timeout = timeout

    def get_channel_id(self, channel_url: str) -> str:
        """
        Takes any YouTube channel URL and returns permanent owner channel_id (UC...).
        Raises ValueError if not found.
        """
        logger.info(f"Resolving channel ID for: {channel_url}")

        # Normalize URL
        if not channel_url.startswith("http"):
            channel_url = "https://" + channel_url

        headers = {"User-Agent": "Mozilla/5.0"}  # avoid bot blocking

        response = requests.get(channel_url, headers=headers, timeout=self.timeout)
        response.raise_for_status()

        html = response.text

        match = self.CHANNEL_ID_REGEX.search(html)
        if not match:
            raise ValueError("Owner channel ID not found in page source")

        return match.group(1)


if __name__ == "__main__":
    resolver = YouTubeChannelResolver()

    test_urls = [
        "https://www.youtube.com/@t3dotgg",
        "https://www.youtube.com/@theothrowaways",
    ]

    for url in test_urls:
        try:
            channel_id = resolver.get_channel_id(url)
            print(f"URL: {url} -> Channel ID: {channel_id}")
        except Exception as e:
            print(f"Failed to resolve {url}: {e}")
