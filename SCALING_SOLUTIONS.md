# Scaling Solutions for Production

## Current Problem
YouTube blocks IPs that make too many transcript requests via web scraping. This is a **real limitation** for production systems.

## Immediate Solutions (Implemented)

### ✅ Rate Limiting
- **What**: Wait 2 seconds between each transcript request
- **Why**: Prevents triggering YouTube's anti-bot detection
- **Config**: `rate_limiting.delay_between_requests` in config.yaml
- **Status**: Implemented with `@rate_limit` decorator

### ✅ Request Limits
- **What**: Cap at 10 videos per run by default
- **Why**: Safety limit to prevent mass requests
- **Config**: `rate_limiting.max_videos_per_run` in config.yaml
- **Status**: Implemented in pipeline

## Production Solutions

### 1. **Proxy Rotation** (Recommended for Medium Scale)
**Cost**: $50-200/month  
**Effort**: Medium  

```python
# Use rotating residential proxies
from rotating_proxies import ProxyRotator

proxies = ProxyRotator([
    'http://proxy1.com:8080',
    'http://proxy2.com:8080',
    # ... more proxies
])

# In transcript_fetcher.py
session = requests.Session()
session.proxies = proxies.get_next()
```

**Providers:**
- Bright Data (formerly Luminati)
- Oxylabs
- SmartProxy

### 2. **YouTube Data API v3** (Official but Limited)
**Cost**: Free tier (10,000 quota/day) then pay  
**Effort**: Medium  

**Limitations:**
- No direct transcript API
- Need to use Captions API (requires video owner permission OR public captions)
- Many videos don't have accessible captions via API

```python
# Example using YouTube Data API
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey=API_KEY)
request = youtube.captions().list(part='snippet', videoId=video_id)
# Then download specific caption track
```

### 3. **Whisper AI Transcription** (Most Reliable)
**Cost**: $0.006/minute (OpenAI Whisper API)  
**Effort**: High  

**Process:**
1. Download video audio using `yt-dlp`
2. Send to OpenAI Whisper API or run local Whisper
3. Get transcript with timestamps

```python
import yt_dlp
import openai

# Download audio
ydl_opts = {'format': 'bestaudio'}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(video_url)
    audio_file = ydl.prepare_filename(info)

# Transcribe
with open(audio_file, 'rb') as f:
    transcript = openai.Audio.transcribe('whisper-1', f)
```

**Pros:**
- Works for ALL videos (even without captions)
- No YouTube blocking issues
- High accuracy

**Cons:**
- Costs money per video
- Slower (transcription takes time)
- Need to handle audio downloads

### 4. **Caching Layer** (Essential for All Solutions)
**Cost**: $0 (free with Redis/SQLite)  
**Effort**: Low  

Store transcripts in a database to avoid re-fetching:

```python
# cache_manager.py
import sqlite3

class TranscriptCache:
    def get(self, video_id):
        # Check if transcript exists
        pass
    
    def set(self, video_id, transcript):
        # Store transcript
        pass
```

### 5. **Distributed System** (Enterprise Scale)
**Cost**: $500+/month  
**Effort**: High  

- Multiple workers with different IPs
- Queue system (Celery + Redis)
- Load balancer
- Kubernetes deployment

## Recommended Architecture for Production

```
┌─────────────────┐
│   Scheduler     │ ← Run daily/hourly
│   (Cron/Cloud)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Pipeline Queue │ ← Rate-limited task queue
│  (Celery/SQS)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│ Worker Pool (3) │────▶│ Proxy Pool   │
│ Different IPs   │     │ (Rotating)   │
└────────┬────────┘     └──────────────┘
         │
         ▼
┌─────────────────┐
│ Transcript DB   │ ← Cache layer
│ (PostgreSQL)    │
└─────────────────┘
```

## Cost Comparison (100 videos/day)

| Solution | Monthly Cost | Reliability | Effort |
|----------|-------------|-------------|---------|
| Current (scraping) | $0 | Low | Done |
| + Rate Limiting | $0 | Medium | Done |
| + Proxies | $100 | High | Medium |
| Whisper API | $180 | Very High | High |
| YouTube API | $0-50 | Medium | Medium |
| Full Production | $500+ | Very High | High |

## Immediate Actions

1. **Today**: Use rate limiting (implemented)
2. **This Week**: Add caching layer
3. **Next Month**: Evaluate proxy service or Whisper API
4. **Growth Phase**: Build distributed system

## Current Status

✅ Rate limiting: 2 seconds between requests  
✅ Request cap: Max 10 videos per run  
✅ Configurable via config.yaml  
⏳ Caching: Not implemented  
⏳ Proxies: Not implemented  

## Notes

- YouTube blocking is usually temporary (1-24 hours)
- Running from residential IP is better than cloud IPs
- Consider running pipeline less frequently (2-3 times/day instead of every hour)
- Monitor logs for `RequestBlocked` errors
