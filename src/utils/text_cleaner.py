"""
TextCleaner Module
Role: Generic text cleaning utility for web content.
"""

import re
from typing import List


class TextCleaner:
    """Cleans raw web text for processing."""

    @staticmethod
    def clean_html(text: str) -> str:
        """
        Remove HTML tags from text.

        Args:
            text: Text potentially containing HTML

        Returns:
            Text with HTML removed
        """
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Decode HTML entities
        text = text.replace("&nbsp;", " ")
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")

        return text

    @staticmethod
    def normalize_spaces(text: str) -> str:
        """
        Normalize whitespace in text.

        Args:
            text: Text to normalize

        Returns:
            Text with normalized spacing
        """
        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)

        # Replace multiple newlines with double newline
        text = re.sub(r"\n\n+", "\n\n", text)

        # Replace tabs with spaces
        text = text.replace("\t", " ")

        return text.strip()

    @staticmethod
    def remove_repeated_headers(text: str) -> str:
        """
        Remove repeated header lines.

        Args:
            text: Text to process

        Returns:
            Text with repeated headers removed
        """
        lines = text.split("\n")
        unique_lines = []
        prev_line = None

        for line in lines:
            stripped = line.strip()
            # Skip if line is same as previous (ignoring whitespace)
            if stripped and stripped != prev_line:
                unique_lines.append(line)
                prev_line = stripped

        return "\n".join(unique_lines)

    @staticmethod
    def remove_short_lines(text: str, min_length: int = 10) -> str:
        """
        Remove very short lines (typically navigation/UI cruft).

        Args:
            text: Text to process
            min_length: Minimum line length to keep

        Returns:
            Text with short lines removed
        """
        lines = text.split("\n")
        filtered_lines = [
            line
            for line in lines
            if len(line.strip()) >= min_length or line.strip() == ""
        ]

        return "\n".join(filtered_lines)

    @staticmethod
    def clean_full(
        text: str, remove_short_lines: bool = True, min_line_length: int = 10
    ) -> str:
        """
        Apply all cleaning operations in sequence.

        Args:
            text: Raw text to clean
            remove_short_lines: Whether to filter out short lines
            min_line_length: Minimum line length if filtering

        Returns:
            Cleaned text
        """
        # Clean HTML
        text = TextCleaner.clean_html(text)

        # Normalize spaces
        text = TextCleaner.normalize_spaces(text)

        # Remove repeated headers
        text = TextCleaner.remove_repeated_headers(text)

        # Remove short lines if requested
        if remove_short_lines:
            text = TextCleaner.remove_short_lines(text, min_length=min_line_length)

        # Final normalization
        text = TextCleaner.normalize_spaces(text)

        return text
