"""
SourceTracker Module
Role: Minimal CSV handler to load sources and update timestamps.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any


class SourceTracker:
    """Manages the watchlist of YouTube channels."""

    def __init__(self, sources_file: str = "youtube_sources.csv"):
        self.sources_file = Path(sources_file)
        self.sources: List[Dict[str, Any]] = []
        self.load_sources()

    def load_sources(self) -> None:
        """Load sources from CSV file."""
        if not self.sources_file.exists():
            return

        with open(self.sources_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.sources = list(reader)

    def get_sources(self) -> List[Dict[str, Any]]:
        """Return all loaded sources."""
        return self.sources

    def update_last_checked(self, source_id: str, timestamp: str) -> None:
        """
        Update the last_checked timestamp for a source and save to file.
        """
        updated = False
        for source in self.sources:
            if source.get("id") == source_id:
                source["last_checked"] = timestamp
                updated = True
                break

        if updated:
            self._save_sources()

    def _save_sources(self) -> None:
        """Save sources back to CSV file."""
        if not self.sources:
            return

        fieldnames = self.sources[0].keys()
        with open(self.sources_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.sources)
