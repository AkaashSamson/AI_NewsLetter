# Architecture Overview

## System Design

### Modular Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                   (Entry Point)                              │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                  youtube_pipeline.py                         │
│              (Orchestrator/Main Logic)                       │
└────┬──────────────────────────────────────────────────────┬─┘
     │                                                        │
     ├──────────────────────┬──────────────────────┬─────────┘
     │                      │                      │
     ▼                      ▼                      ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│Models Package│  │Utils Package │  │YouTube Finder    │
├──────────────┤  ├──────────────┤  ├──────────────────┤
│SourceTracker│  │TextCleaner   │  │VideoDiscovery    │
│YouTubeFinder│  │JSONBuilder   │  │API Integration   │
│TransFetcher │  │              │  │                  │
│GroqWriter   │  │              │  │                  │
└──────────────┘  └──────────────┘  └──────────────────┘
```

### Processing Flow

```
Input: youtube_sources.csv
         │
         ▼
    ┌─────────────────────────────────┐
    │ SourceTracker                   │
    │ - Load CSV                      │
    │ - Check last_checked            │
    │ - List active sources           │
    └────────────┬────────────────────┘
                 │
                 ▼
         For each channel:
                 │
                 ├──▶ YouTubeVideoFinder
                 │    - YouTube API call
                 │    - Filter by date
                 │    - Get metadata
                 │
                 ├──▶ TranscriptFetcher
                 │    - Download captions
                 │    - Clean timestamps
                 │
                 ├──▶ TextCleaner
                 │    - Remove HTML
                 │    - Normalize spaces
                 │
                 ├──▶ GroqNewsWriter
                 │    - Summarize
                 │    - 5-6 line summary
                 │    - NO URLs
                 │
                 └──▶ JSONBuilder
                      - Combine with link
                      - Format output
                      
Output: daily_digest.json
```

---

## File Organization

### Models (`src/models/`)
Domain objects and API clients:
- `source_tracker.py` - CSV-based source management
- `youtube_finder.py` - YouTube Data API v3 integration
- `transcript_fetcher.py` - YouTube transcript API
- `groq_news_writer.py` - Groq LLM integration (OpenAI client)

### Utils (`src/utils/`)
Reusable utilities:
- `text_cleaner.py` - Generic text processing
- `json_builder.py` - JSON serialization

### Pipelines (`src/pipelines/`)
Orchestration and workflows:
- `youtube_pipeline.py` - Main YouTube processing pipeline

---

## Data Structures

### Source (CSV)
```python
{
    "source_id": "yt_001",
    "type": "youtube",
    "name": "Tech Channel",
    "url_or_id": "UCxxxxxxxxxxxxxx",
    "category": "tech",
    "last_checked": "2026-01-22T12:00:00Z"
}
```

### Video (YouTube API)
```python
{
    "video_id": "xxxxx",
    "title": "Video Title",
    "published_at": "2026-01-22T...",
    "channel_name": "Tech Channel",
    "link": "https://youtube.com/watch?v=xxxxx"
}
```

### Transcript (Cleaned)
```python
{
    "video_id": "xxxxx",
    "title": "Video Title",
    "clean_text": "Paragraph of clean text...",
    "link": "https://youtube.com/watch?v=xxxxx"
}
```

### Summary (LLM Output)
```python
{
    "title": "Video Title",
    "summary": "5-6 line summary from Groq..."
}
```

### Final Item (JSON)
```python
{
    "type": "youtube",
    "title": "Video Title",
    "summary": "5-6 line summary...",
    "link": "https://youtube.com/watch?v=xxxxx"
}
```

### Daily Digest (JSON)
```json
{
    "date": "2026-01-22",
    "count": 2,
    "items": [...]
}
```

---

## API Integrations

### YouTube Data API v3
- **Purpose**: Discover new videos
- **Method**: Rest API via `google-api-python-client`
- **Key Operation**: Search channel uploads by date

### YouTube Transcript API
- **Purpose**: Fetch video captions
- **Method**: Unofficial Python wrapper
- **Key Operation**: Get transcript for video ID

### Groq API (via OpenAI Client)
- **Purpose**: Summarize transcripts
- **Method**: OpenAI Python client pointing to Groq endpoint
- **Model**: `llama-3.3-70b-versatile`
- **Endpoint**: `https://api.groq.com/openai/v1`

---

## Key Design Decisions

### 1. OpenAI Client for Groq
- Reduces dependencies (no separate Groq SDK needed)
- Familiar OpenAI API
- Easy to swap LLM providers
- Simple configuration change

### 2. Modular Imports
- Each package has clear responsibility
- Easy to test independently
- Easy to extend (add Blog fetcher, Email sender)
- No circular dependencies

### 3. Environment Variables
- Secrets in `.env`, not in code
- Easy configuration per environment
- `.env` in gitignore (won't commit secrets)

### 4. CSV-Based Source Tracking
- Simple, human-readable
- Easy to edit manually
- `last_checked` prevents duplicates
- No database needed

### 5. Real Links Only
- LLM never creates URLs
- System attaches original YouTube links
- Ensures traceability

---

## Extension Points

### Adding Blog Support (Phase 2)
```
New files:
- src/models/blog_fetcher.py
- Update youtube_sources.csv to include RSS entries
- Update youtube_pipeline.py to handle both types
```

### Adding Email Delivery (Phase 3)
```
New files:
- src/utils/email_formatter.py
- src/models/email_sender.py
- Add to pipeline: JSONBuilder → EmailFormatter → EmailSender
```

### Adding Different LLM
```
Replace in main.py:
from src.models import GroqNewsWriter
with:
from src.models import OpenAINewsWriter  # or AnthropicNewsWriter
```

---

## Performance Characteristics

| Operation | Time | API Calls |
|-----------|------|-----------|
| Find 1 channel videos | 1-2s | 2 |
| Fetch 1 transcript | 1-2s | 1 |
| Summarize 1 video | 0.5-1s | 1 |
| Clean text | < 0.1s | 0 |
| Process 1 video | 2-5s | 4 |
| Process 1 channel (3 videos) | 6-15s | 12 |

---

## Configuration & Customization

### Change LLM Model
In `.env`:
```
GROQ_MODEL=mixtral-8x7b-32768
```

### Change Look-Back Window
In `youtube_pipeline.py`:
```python
videos = self.video_finder.find_new_videos(
    channel_id=channel_id,
    hours=48  # Change from 24 to 48
)
```

### Change Summary Length
In `groq_news_writer.py`:
```python
summary = self.summarize(
    title, 
    text, 
    max_lines=10  # Change from 6 to 10
)
```

---

**Architecture Summary**: Clean, modular, extensible, production-ready! 🚀
