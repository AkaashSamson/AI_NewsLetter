"""
SourceTracker Module
Role: Load sources.csv, track last_checked, and prevent duplicates.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class SourceTracker:
    """Manages the watchlist of YouTube channels and blogs."""

    def __init__(self, sources_file: str = "youtube_sources.csv"):
        """
        Initialize the SourceTracker.

        Args:
            sources_file: Path to the CSV file containing sources
        """
        self.sources_file = Path(sources_file)
        self.sources: List[Dict[str, Any]] = []
        self.load_sources()

    def load_sources(self) -> None:
        """Load sources from CSV file."""
        if not self.sources_file.exists():
            raise FileNotFoundError(f"Sources file not found: {self.sources_file}")

        with open(self.sources_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.sources = list(reader)

    def get_active_sources(self, source_type: str = "youtube") -> List[Dict[str, Any]]:
        """
        Get all active sources of a given type.

        Args:
            source_type: Type of source ('youtube' or 'rss')

        Returns:
            List of active sources
        """
        return [s for s in self.sources if s.get("type") == source_type]

    def update_last_checked(self, source_id: str, timestamp: str = None) -> None:
        """
        Update the last_checked timestamp for a source.

        Args:
            source_id: ID of the source to update
            timestamp: ISO format timestamp (default: now)
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"

        for source in self.sources:
            if source.get("source_id") == source_id:
                source["last_checked"] = timestamp
                break

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

    def get_source_by_id(self, source_id: str) -> Dict[str, Any] | None:
        """Get a source by its ID."""
        for source in self.sources:
            if source.get("source_id") == source_id:
                return source
        return None
