"""
JSONBuilder Module
Role: Build final structured JSON output with title, summary, and real link.
"""

from typing import List, Dict, Any
from datetime import datetime
import json


class JSONBuilder:
    """Builds the final structured JSON output."""

    @staticmethod
    def build_item(
        item_type: str, title: str, summary: str, link: str
    ) -> Dict[str, Any]:
        """
        Build a single news item.

        Args:
            item_type: Type of item ('youtube', 'blog', etc.)
            title: Item title
            summary: Item summary
            link: Original source link (MUST be from original source, never LLM)

        Returns:
            Dict representing a news item
        """
        return {"type": item_type, "title": title, "summary": summary, "link": link}

    @staticmethod
    def build_daily_digest(
        items: List[Dict[str, Any]], date: str = None
    ) -> Dict[str, Any]:
        """
        Build the complete daily digest JSON.

        Args:
            items: List of news items
            date: ISO date string (default: today)

        Returns:
            Complete digest structure
        """
        if date is None:
            date = datetime.utcnow().strftime("%Y-%m-%d")

        return {"date": date, "count": len(items), "items": items}

    @staticmethod
    def save_to_file(data: Dict[str, Any], filepath: str) -> bool:
        """
        Save JSON to file.

        Args:
            data: JSON data to save
            filepath: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving JSON to {filepath}: {e}")
            return False

    @staticmethod
    def load_from_file(filepath: str) -> Dict[str, Any] | None:
        """
        Load JSON from file.

        Args:
            filepath: Input file path

        Returns:
            Loaded JSON data or None if error
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {filepath}: {e}")
            return None
