# Quick Reference Card

**Print this or pin it for quick lookup! ⚡**

---

## Installation

```bash
# Windows
python -m venv ai_news
ai_news\Scripts\activate
pip install -r requirements.txt

# Mac/Linux
python3 -m venv ai_news
source ai_news/bin/activate
pip install -r requirements.txt
```

---

## Environment Setup

1. **Groq API Key**: Get from https://console.groq.com/keys
2. **YouTube API Key**: Get from Google Cloud Console
3. **Create `.env`**: Should already exist
4. **Add keys to `.env`**:
```
GROQ_API_KEY=gsk_0TC6eUhwixsBYY3...
YOUTUBE_API_KEY=AIzaSy...
```

---

## Running the App

```bash
python main.py
```

**Output**: `daily_digest.json`

---

## Folder Structure

```
AI_NewsLetter/
├── src/models/          ← API clients & domain objects
├── src/utils/           ← Utility functions
├── src/pipelines/       ← Main workflows
├── docs/                ← This documentation
├── .env                 ← API keys (secret!)
├── main.py              ← Entry point
└── youtube_sources.csv  ← Channel list
```

---

## Add YouTube Channels

Edit `youtube_sources.csv`:

```csv
source_id,type,name,url_or_id,category,last_checked
yt_001,youtube,Tech Channel,UCxxxxxxxxxxxxxxxxxxxxxx,tech,2026-01-01T00:00:00Z
yt_002,youtube,News Channel,UCyyyyyyyyyyyyyyyyyyyyyyyy,news,2026-01-01T00:00:00Z
```

Get channel ID:
- Go to channel → Click About
- Copy channel ID (looks like: `UCxxxxxxxxxxxxxxxxxxxxxx`)

---

## API Reference Cheat Sheet

### YouTubeVideoFinder
```python
from src.models import YouTubeVideoFinder

finder = YouTubeVideoFinder("api_key")
videos = finder.find_new_videos("UCxxxxxx", hours=24)
```

### TranscriptFetcher
```python
from src.models import TranscriptFetcher

fetcher = TranscriptFetcher()
result = fetcher.fetch_and_clean("video_id", "title", "link")
```

### GroqNewsWriter
```python
from src.models import GroqNewsWriter

writer = GroqNewsWriter(api_key="groq_key")
summary = writer.summarize("title", "long text", max_lines=6)
```

### TextCleaner
```python
from src.utils import TextCleaner

clean = TextCleaner.clean_full(dirty_html_text)
```

### JSONBuilder
```python
from src.utils import JSONBuilder

item = JSONBuilder.build_item("youtube", "title", "summary", "link")
digest = JSONBuilder.build_daily_digest([items])
JSONBuilder.save_to_file(digest, "output.json")
```

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `GROQ_API_KEY not found` | Check `.env` file exists |
| `YouTube API error` | Verify API key in `.env` |
| `No transcripts found` | Video must have captions enabled |
| `Rate limit exceeded` | Free Groq tier has 5 req/min limit |

---

## Groq Models (Speed vs Quality)

| Model | Speed | Quality |
|-------|-------|---------|
| `mixtral-8x7b-32768` | ⚡ Fastest | Good |
| `llama-3.1-70b-versatile` | 🚀 Fast | Excellent |
| `llama-3.3-70b-versatile` | 🚀 Best | Excellent |

Change in `.env`:
```
GROQ_MODEL=mixtral-8x7b-32768
```

---

## Environment Variables

| Variable | Required | Example |
|----------|----------|---------|
| `GROQ_API_KEY` | ✅ Yes | `gsk_0TC6eUhw...` |
| `YOUTUBE_API_KEY` | ✅ Yes | `AIzaSy...` |
| `GROQ_MODEL` | ⏱️ Optional | `llama-3.3-70b-versatile` |
| `OUTPUT_JSON_PATH` | ⏱️ Optional | `daily_digest.json` |
| `SOURCES_CSV_PATH` | ⏱️ Optional | `youtube_sources.csv` |

---

## Performance

| Operation | Time | Cost |
|-----------|------|------|
| Find videos (1 channel) | 1-2s | ~100 units |
| Fetch transcript | 1-2s | Free |
| Summarize (Groq) | 0.5-1s | Free |
| Process 1 video | 2-5s | ~100 units |
| Process 1 channel (3 videos) | 6-15s | ~300 units |

**YouTube quota**: 10,000 units/day = ~33 channels/day

---

## File Paths (from project root)

| File | Purpose |
|------|---------|
| `main.py` | Run this |
| `.env` | API keys here |
| `youtube_sources.csv` | Add channels here |
| `daily_digest.json` | Output file |
| `src/models/` | API clients |
| `src/utils/` | Utilities |
| `src/pipelines/` | Main logic |
| `docs/` | Full documentation |

---

## Debug Commands

```python
# Test Groq API
python -c "
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
c = OpenAI(api_key=os.getenv('GROQ_API_KEY'), base_url='https://api.groq.com/openai/v1')
msg = c.chat.completions.create(model='llama-3.3-70b-versatile', messages=[{'role': 'user', 'content': 'hi'}])
print('Groq works!')
"

# Test YouTube API
python -c "
from src.models import YouTubeVideoFinder
import os
from dotenv import load_dotenv
load_dotenv()
f = YouTubeVideoFinder(os.getenv('YOUTUBE_API_KEY'))
print('YouTube API works!')
"

# Test imports
python -c "
from src.models import YouTubeVideoFinder, GroqNewsWriter
from src.utils import TextCleaner, JSONBuilder
from src.pipelines import main_youtube_pipeline
print('All imports work!')
"
```

---

## Getting Help

- **Installation issues** → See docs/SETUP_GUIDE.md
- **How does it work?** → See docs/ARCHITECTURE.md  
- **API methods** → See docs/API_REFERENCE.md
- **Where's the code?** → See docs/PROJECT_STRUCTURE.md
- **Something broken** → See docs/TROUBLESHOOTING.md

---

## Phase Roadmap

- **Phase 1** ✅ YouTube pipeline (complete)
- **Phase 2** 🔄 Blog/RSS feeds (coming)
- **Phase 3** 🔄 Email delivery (coming)

---

## Links

- [Groq API](https://groq.com/)
- [YouTube API](https://developers.google.com/youtube)
- [OpenAI Python](https://github.com/openai/openai-python)
- [Project Repo](.) 

---

**Bookmark this page! 🔖**
