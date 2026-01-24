# YouTube Content Pipeline Documentation

This document outlines the architecture and data flow of the YouTube Content Pipeline. This pipeline monitors YouTube channels, detects new videos, fetches transcripts, and generates AI-powered summaries.

## Pipeline Overview

The **YouTube Pipeline** is an automated system that orchestrates several specialized modules to transform raw YouTube channel URLs into concise, summarized insights. This process is managed by the main controller script.

**Main Controller:**
- **File:** [src/pipelines/youtube_pipeline.py](../src/pipelines/youtube_pipeline.py)
- **Role:** Orchestrates the entire flow, manages configuration, and handles error logging.

---

## Module Breakdown

### 1. Source Tracker
- **File:** [src/models/source_tracker.py](../src/models/source_tracker.py)
- **Role:** Manages the list of YouTube channels to monitor. It reads from a CSV file and updates "last checked" timestamps.
- **Input:** `youtube_sources.csv` (File path).
- **Output:** A list of source dictionaries (e.g., `{'url': '...', 'last_checked': '...'}`).

### 2. Channel Resolver
- **File:** [src/models/yt_channel_resolver.py](../src/models/yt_channel_resolver.py)
- **Role:** Converts user-friendly Channel URLs (handles) into the permanent Channel IDs required by RSS feeds.
- **Input:** Channel URL (e.g., `https://youtube.com/@channelname`).
- **Output:** Channel ID string (e.g., `UCxxxxxxxxxxxx`).

### 3. Video Finder
- **File:** [src/models/youtube_finder.py](../src/models/youtube_finder.py)
- **Role:** Detects new videos published within a specific time window (e.g., last 24 hours). It uses public RSS feeds to avoid API quota limits.
- **Input:** Channel ID and lookback duration (hours).
- **Output:** A list of video dictionaries containing:
  - `video_id`
  - `title`
  - `published_at`
  - `link`

### 4. Transcript Fetcher
- **File:** [src/models/transcript_fetcher.py](../src/models/transcript_fetcher.py)
- **Role:** Retrieves the closed captions/subtitles for a specific video and cleans the text (removes timestamps, filler words).
- **Input:** `video_id`.
- **Output:** A dictionary containing the cleaned transcript text (`clean_text`) or `None` if unavailable.

### 5. LLM Writer (Summarizer)
- **File:** [src/models/llm_writer.py](../src/models/llm_writer.py)
- **Role:** Uses an LLM (Groq or Gemini) to generate a concise summary of the video based on its transcript.
- **Input:** Video Title and Transcript Text.
- **Output:** A dictionary with the generated `summary` and `title`.

---

## Data Flow Diagram

The data moves through the pipeline in the following sequence:

1.  **Start:** `YouTubePipeline` initializes and reads config.
2.  **Load Sources:** `SourceTracker` provides a list of target channel URLs.
3.  **Resolve ID:** `YouTubeChannelResolver` converts **URL** $\rightarrow$ **Channel ID**.
4.  **Find Videos:** `YouTubeVideoFinder` takes **Channel ID** $\rightarrow$ returns **List of New Videos**.
5.  **Fetch Content:** For each new video, `TranscriptFetcher` takes **Video ID** $\rightarrow$ returns **Clean Transcript**.
6.  **Generate Insight:** `LLMWriter` takes **Transcript** $\rightarrow$ returns **Summary**.
7.  **Finalize:** The result is formatted into a final JSON item and collected.

---

## Key Configuration

The pipeline behavior is controlled by `config.yaml`:
- **lookback_hours**: How far back to check for new videos.
- **max_videos_per_run**: Rate limiting to prevent overwhelming the APIs.
- **llm_provider**: Choice between `groq` or `gemini` for summarization.
