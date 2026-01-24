# Mitigation Strategies & Best Practices

To prevent IP blocking (YouTube) and API Rate Limiting (Groq/LLM), implement the following strategies in your pipeline.

## 1. Randomized Delays (Jitter)
**Problem:** Static delays (e.g., exactly 2.0 seconds) are easy for anti-scraping systems to detect.
**Solution:** Use random intervals.

**Code Snippet:**
```python
import time
import random

def random_sleep(min_seconds=3, max_seconds=7):
    sleep_time = random.uniform(min_seconds, max_seconds)
    logger.info(f"Sleeping for {sleep_time:.2f}s...")
    time.sleep(sleep_time)

# Usage in Pipeline Loop
for video in videos:
    process_video(video)
    random_sleep(5, 12)  # Sleep 5-12 seconds BETWEEN videos
```

## 2. Exponential Backoff
**Problem:** When you hit a limit (HTTP 429), retrying immediately makes it worse and extends the ban.
**Solution:** Wait longer after each failure.

**Code Snippet:**
```python
import time

def call_api_with_backoff(func, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait_time = (2 ** retries) * 5  # 5s, 10s, 20s...
                logger.warning(f"Rate limit hit. Waiting {wait_time}s...")
                time.sleep(wait_time)
                retries += 1
            else:
                raise e
    return None
```

## 3. Strict Batch Limits
**Problem:** Processing 15 videos in one run is risky for a daily pipeline.
**Solution:** Enforce a hard cap regardless of date.

**Recommendation:**
In your `config.yaml`, set `max_videos_per_run` to a safe number (e.g., 3 or 5).
```yaml
rate_limiting:
  max_videos_per_run: 5  # Processing more than 5 exposes you to bans
```

## 4. Robust Date Parsing (Feedparser)
**Problem:** Manual string parsing fails on edge cases.
**Solution:** Use `feedparser`'s native time struct.

**Code Snippet (Refactored `youtube_finder.py`):**
```python
from time import mktime
from datetime import datetime, timezone

# Inside your loop:
if hasattr(entry, 'published_parsed'):
    # Convert struct_time to aware datetime
    dt = datetime.fromtimestamp(mktime(entry.published_parsed))
    published_at = dt.replace(tzinfo=timezone.utc)
```

## 5. Session Management & User Agents
**Problem:** Default `requests` headers look like bots.
**Solution:** Rotate User-Agents and use Sessions.

**Code Snippet:**
```python
import requests

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "Accept-Language": "en-US,en;q=0.9",
})

response = session.get(url)
```

## 6. Architecture Update Recommendation
Currently, your `process_single_channel` function runs synchronously.

**Recommended Flow:**
1.  **Search Phase:** Find *all* new videos for all channels first. Store them in a list.
2.  **Filter Phase:** stricter date check + limit to top 5 newest across *all* channels (not just per channel).
3.  **Process Phase:**
    ```python
    for video in final_list:
        fetch_transcript()
        random_sleep(3, 6) # Wait for YouTube
        generate_summary()
        random_sleep(2, 4) # Wait for Groq
    ```

This breaks the intense burst of activity into a smoother, slower stream.
