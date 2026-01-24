# Architecture Reference

This document provides a formal technical reference for the AI NewsLetter service-oriented architecture.

## 1. Database Layer (`src/database/`)

The database layer handles all direct data persistence and retrieval. It is built on **SQLAlchemy ORM** and backed by **PostgreSQL**.

### 1.1 Core (`src/database/core.py`)
- **Engine**: created via `create_engine` using settings from env.
- **SessionLocal**: Factory for creating new database sessions.
- **get_db()**: Generator function used for dependency injection (yielding a `Session`).

### 1.2 Models (`src/database/models.py`)
All models inherit from `TimeStampedModel` (adds `created_at`).

**Channel**
| Field | Type | Description |
| :--- | :--- | :--- |
| `channel_id` | String (PK) | The YouTube Channel ID (e.g., `UC...`). |
| `name` | String | Human-readable name. |
| `url` | String (Unique) | Original Channel URL. |
| `last_checked` | DateTime | Timestamp of the newest video processed for this channel. |

**VideoSummary**
| Field | Type | Description |
| :--- | :--- | :--- |
| `video_id` | String (PK) | The YouTube Video ID. |
| `channel_id` | String (FK) | Foreign key to `channels.channel_id`. |
| `title` | String | Video Title. |
| `summary` | Text | AI-generated summary. |
| `published_at` | DateTime | When the video was uploaded to YouTube. |

### 1.3 CRUD Operations (`src/database/crud.py`)
Pure data access functions. No business logic (e.g., no external API calls).

- **`create_channel(db, channel_id, url, name)`**: Inserts a new channel.
- **`get_channel_by_id(db, channel_id)`**: Fetches a channel by its PK.
- **`get_channel_by_url(db, url)`**: Helper to check for existing URLs.
- **`create_summary(...)`**: Inserts a new AI summary.
- **`get_summary_by_video_id(db, video_id)`**: Used for deduplication checks.

## 2. Service Layer (`src/services/`)

The service layer implements the business logic, orchestrating calls between the database and the external API modules (`src/models/`).

### 2.1 ChannelManager (`src/services/channel_manager.py`)
Responsible for onboarding new sources.

- **`add_new_channel(url)`**: 
    - **Validates** unique URL.
    - **Resolves** the immutable YouTube Channel ID using `models.yt_channel_resolver`.
    - **Prevents** duplicate Channel IDs (e.g., if user adds `youtube.com/@Verge` and `youtube.com/channel/UC...` which map to same ID).
    - **Persists** via `crud`.

### 2.2 FeedManager (`src/services/feed_manager.py`)
The core engine that runs practically the entire pipeline loop.

- **`run_polling_cycle()`**:
    - **Polling**: Iterates all DB channels.
    - **Discovery**: Uses `models.youtube_finder` to get recent videos.
    - **Deduplication**: Checks `crud.get_summary_by_video_id` to ensure we never process a video twice.
    - **Rate Limit**: Enforces a strict Global Limit (default: 5 videos/run) regardless of how many new videos exist.
    - **Jitter**: Sleeps for a random interval (3-7s) between processing videos to avoid Bot Detection.
    - **Pipeline**:
        1. `TranscriptFetcher`: Gets text.
        2. `LLMWriter`: Summarizes text.
        3. `crud.create_summary`: Saves result.

## 3. Frontend Layer (`src/app/`)

The frontend is built with **Streamlit** and interacts only with the Service Layer.

#### `src/app/main.py`
Entry point for the Dashboard.

- **Sidebar**:
    - **Add Channel**: Input form for YouTube URLs. Calls `ChannelManager.add_new_channel()`.
    - **Run Update**: Parameterized button to trigger `FeedManager.run_polling_cycle()`. 
      *(Note: In production, polling runs as a background daemon, but manual trigger is provided for control.)*

- **Main View**:
    - **Stats**: Total channels, Total summaries, Last run time.
    - **Latest News**: A feed of the most recent AI summaries from the database, ordered by creation time.

## 4. Cleanup & Legacy Code

Old modules that were file-based have been deprecated and moved to the `deprecated/` directory.

- `src/pipelines/youtube_pipeline.py` -> `deprecated/youtube_pipeline.py`
- `src/models/source_tracker.py` -> `deprecated/source_tracker.py`

These files are preserved for reference but are no longer used in the active `src/app/main.py` flow.
