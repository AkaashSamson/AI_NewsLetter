import sys
import os
from pathlib import Path

# Add project root to path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from src.database.core import get_db
from src.database.models import Channel
from src.services.yt_channel_resolver import YouTubeChannelResolver


def backfill_names():
    db = next(get_db())
    resolver = YouTubeChannelResolver()

    # Get channels with no name (empty string or None)
    channels = (
        db.query(Channel).filter((Channel.name == None) | (Channel.name == "")).all()
    )

    print(f"Found {len(channels)} channels to update.")

    for channel in channels:
        try:
            print(f"Resolving: {channel.url}")
            _, name = resolver.get_channel_info(channel.url)
            channel.name = name
            db.commit()
            print(f"  -> Updated to: {name}")
        except Exception as e:
            print(f"  -> Failed: {e}")


if __name__ == "__main__":
    backfill_names()
