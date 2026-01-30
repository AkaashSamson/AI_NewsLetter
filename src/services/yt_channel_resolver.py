import requests
import re
import logging

logger = logging.getLogger(__name__)


class YouTubeChannelResolver:
    # This matches ONLY the owner channel id
    CHANNEL_ID_REGEX = re.compile(r'"externalId":"(UC[a-zA-Z0-9_-]{22})"')
    CHANNEL_TITLE_REGEX = re.compile(r"<title>(.*?)</title>")

    def __init__(self, timeout=10):
        self.timeout = timeout

    def get_channel_info(self, channel_url: str) -> tuple[str, str]:
        """
        Takes any YouTube channel URL and returns (channel_id, channel_name).
        Raises ValueError if ID not found. Name will be "Unknown" if not found.
        """
        logger.info(f"Resolving channel info for: {channel_url}")

        # Normalize URL
        if not channel_url.startswith("http"):
            channel_url = "https://" + channel_url

        headers = {"User-Agent": "Mozilla/5.0"}  # avoid bot blocking

        response = requests.get(channel_url, headers=headers, timeout=self.timeout)
        response.raise_for_status()

        html = response.text

        # 1. Get ID
        id_match = self.CHANNEL_ID_REGEX.search(html)
        if not id_match:
            raise ValueError("Owner channel ID not found in page source")
        channel_id = id_match.group(1)

        # 2. Get Name
        title_match = self.CHANNEL_TITLE_REGEX.search(html)
        channel_name = "Unknown"
        if title_match:
            raw_title = title_match.group(1)
            # Remove " - YouTube" suffix
            channel_name = raw_title.replace(" - YouTube", "").strip()

        return channel_id, channel_name


if __name__ == "__main__":
    resolver = YouTubeChannelResolver()

    test_urls = [
        "https://www.youtube.com/@t3dotgg",
        "https://www.youtube.com/@theothrowaways",
    ]

    for url in test_urls:
        try:
            channel_id, name = resolver.get_channel_info(url)
            print(f"URL: {url} -> ID: {channel_id}, Name: {name}")
        except Exception as e:
            print(f"Failed to resolve {url}: {e}")
