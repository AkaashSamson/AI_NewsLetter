# AI Newsletter with Groq - Complete Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify .env File
The `.env` file is already created with your Groq API key:
```
GROQ_API_KEY=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
YOUTUBE_API_KEY=your_youtube_key
GROQ_MODEL=llama-3.3-70b-versatile
```

**Get YouTube API Key**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable YouTube Data API v3
3. Create API key credential
4. Add to `.env`: `YOUTUBE_API_KEY=your_key`

### 3. Add YouTube Channels
Edit `youtube_sources.csv`:
```csv
source_id,type,name,url_or_id,category,last_checked
yt_001,youtube,My Channel,UCxxxxxxxxxxxxxx,tech,2026-01-01T00:00:00Z
```

### 4. Run Pipeline
```bash
python main.py
```

**Output**: `daily_digest.json` with summaries from Groq

---

## Project Structure

```
AI_NewsLetter/
├── src/                           # Main source code
│   ├── __init__.py
│   ├── models/                    # Data and API models
│   │   ├── source_tracker.py      # CSV management
│   │   ├── youtube_finder.py      # YouTube API
│   │   ├── transcript_fetcher.py  # Captions
│   │   └── groq_news_writer.py    # Groq LLM
│   ├── utils/                     # Utility functions
│   │   ├── text_cleaner.py        # Text processing
│   │   └── json_builder.py        # JSON output
│   └── pipelines/                 # Orchestration
│       └── youtube_pipeline.py    # Main pipeline
├── docs/                          # Documentation
├── .env                           # Environment (secrets)
├── main.py                        # Entry point
├── requirements.txt               # Dependencies
└── youtube_sources.csv            # Channel config
```

---

## Available Groq Models

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `mixtral-8x7b-32768` | ⚡ Very Fast | Good | Quick summaries |
| `llama-3.1-70b-versatile` | ⚡ Fast | Excellent | Balanced |
| `llama-3.3-70b-versatile` | 🚀 **Recommended** | Excellent | Best quality |

Change model in `.env`:
```
GROQ_MODEL=mixtral-8x7b-32768
```

---

## API Integration

### Groq with OpenAI Client
Uses OpenAI Python client with Groq endpoint:

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_groq_api_key",
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "..."}]
)
```

---

## Data Flow

```
YouTube Channels (CSV)
    ↓
YouTubeVideoFinder (YouTube API)
    ↓ [Find videos from last 24h]
TranscriptFetcher (Caption API)
    ↓ [Get clean transcripts]
TextCleaner (Utilities)
    ↓ [Remove noise]
GroqNewsWriter (Groq API)
    ↓ [Summarize with LLM]
JSONBuilder (Utilities)
    ↓ [Format output]
daily_digest.json (Output)
```

---

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "GROQ_API_KEY not found"
Ensure `.env` file exists with:
```
GROQ_API_KEY=gsk_...
```

### "No transcripts found"
- Video might not have captions enabled
- Try different language in TranscriptFetcher
- Pipeline skips automatically

### "YouTube API error"
- Get API key from Google Cloud Console
- Enable YouTube Data API v3
- Add to `.env`

---

## Environment Variables

| Variable | Required | Example |
|----------|----------|---------|
| `GROQ_API_KEY` | Yes | `gsk_0TC6eUhwixsBYY3...` |
| `YOUTUBE_API_KEY` | Yes | Your YouTube API key |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` |
| `OUTPUT_JSON_PATH` | No | `daily_digest.json` |
| `SOURCES_CSV_PATH` | No | `youtube_sources.csv` |

---

## Performance

- **Groq Speed**: ~100-500ms per summary
- **YouTube API**: ~1-2s per channel
- **Typical run**: 10-30 seconds for 1 channel with 3 new videos

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Set up Groq API key  
3. ✅ Add YouTube channels to CSV
4. ✅ Get YouTube API key
5. ✅ Run `python main.py`
6. 🔄 Phase 2: Add blog/RSS support
7. 🔄 Phase 3: Email delivery

---

**Ready to process YouTube content with AI! 🚀**
