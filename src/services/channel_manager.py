import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database import crud
from src.services.yt_channel_resolver import YouTubeChannelResolver

logger = logging.getLogger(__name__)


class ChannelManager:
    """
    Service for managing YouTube Channels.
    Orchestrates validation, ID resolution, and persistence.
    """

    def __init__(self, db: Session):
        self.db = db
        self.resolver = YouTubeChannelResolver()

    def add_new_channel(self, url: str) -> str:
        """
        Adds a new channel to the database.

        Steps:
        1. Checks if URL already exists.
        2. Resolves Channel ID (external API).
        3. Checks if Channel ID already exists.
        4. Saves to DB.

        Args:
            url: The full YouTube channel URL.

        Returns:
            str: Message indicating result (Success/Exists).

        Raises:
            ValueError: If channel ID cannot be resolved.
        """
        # 1. Check URL existence
        existing_by_url = crud.get_channel_by_url(self.db, url)
        if existing_by_url:
            return f"Channel URL already exists: {existing_by_url.name or existing_by_url.channel_id}"

        # 2. Resolve ID & Name
        try:
            channel_id, channel_name = self.resolver.get_channel_info(url)
            logger.info(f"Resolved {url} -> {channel_id} ({channel_name})")
        except Exception as e:
            logger.error(f"Failed to resolve channel info for {url}: {e}")
            raise ValueError(f"Could not resolve channel info: {e}")

        # 3. Check ID existence (to prevent duplicates via different URLs)
        existing_by_id = crud.get_channel_by_id(self.db, channel_id)
        if existing_by_id:
            return f"Channel ID {channel_id} already monitored."

        # 4. Save
        crud.create_channel(self.db, channel_id=channel_id, url=url, name=channel_name)
        return f"Successfully added channel: {channel_name} ({channel_id})"

    def list_channels(self):
        """Returns all monitored channels."""
        return crud.get_all_channels(self.db)
