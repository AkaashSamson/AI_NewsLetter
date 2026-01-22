# Troubleshooting Guide

## Common Issues and Solutions

### 1. "ModuleNotFoundError: No module named 'src'"

**Problem**: Python can't find the src package.

**Solutions**:

a) **Install dependencies first**
```bash
pip install -r requirements.txt
```

b) **Make sure you're in project root**
```bash
cd c:\Users\Akaash\Desktop\D_Drive\Project\AI_NewsLetter
python main.py
```

c) **Check Python path**
```bash
python -c "import sys; print(sys.path)"
# Should include your project directory
```

---

### 2. "GROQ_API_KEY not found"

**Problem**: Environment variable not loaded.

**Solutions**:

a) **Check .env file exists**
```bash
dir .env  # Windows
ls .env   # Mac/Linux
```

b) **Verify .env content**
```
GROQ_API_KEY=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
YOUTUBE_API_KEY=your_key
```

c) **Check .env is not ignored globally**
```bash
# Windows
git config --global core.excludesfile
# If set, check that file doesn't exclude .env
```

d) **Verify python-dotenv installed**
```bash
pip install python-dotenv
```

---

### 3. "No such file or directory: 'youtube_sources.csv'"

**Problem**: Source file not found.

**Solutions**:

a) **Create the file**
```bash
# Copy provided template
# Or create manually:
```
```csv
source_id,type,name,url_or_id,category,last_checked
yt_001,youtube,My Channel,UCxxxxxxxxxxxxxx,tech,2026-01-01T00:00:00Z
```

b) **Check path in .env**
```
SOURCES_CSV_PATH=youtube_sources.csv
```

c) **Run from project root**
```bash
cd c:\Users\Akaash\Desktop\D_Drive\Project\AI_NewsLetter
python main.py
```

---

### 4. "YouTube API error: 403 Forbidden"

**Problem**: Invalid or missing YouTube API key.

**Solutions**:

a) **Get valid API key**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Select your project
- Go to APIs & Services → Credentials
- Click on your API key
- Under "API restrictions", enable YouTube Data API v3

b) **Check quota**
- YouTube Data API has quota of 10,000 units/day
- Each video search uses ~100 units
- Limit to ~100 searches/day

c) **Add to .env**
```
YOUTUBE_API_KEY=AIzaSy...
```

d) **Test the key**
```python
python -c "
from src.models import YouTubeVideoFinder
import os
finder = YouTubeVideoFinder(os.getenv('YOUTUBE_API_KEY'))
print('API key works!')
"
```

---

### 5. "No transcripts found"

**Problem**: Video has no captions or transcripts unavailable.

**Solutions**:

a) **Check if video has captions**
- Go to video on YouTube
- Click "More" → "Show transcript"
- If not available, video won't work

b) **Try different language**
- Edit `transcript_fetcher.py`
- Change `languages=['en']` to `['en', 'es', 'fr']`

c) **Skip unavailable videos**
- Pipeline automatically skips (won't error)
- Just moves to next video

d) **Use videos with guaranteed captions**
- Technical presentations usually have auto-captions
- News channels have captions

---

### 6. "Groq API error: rate_limit_exceeded"

**Problem**: Hit Groq rate limits.

**Solutions**:

a) **Check rate limits**
- Free tier: ~5 requests/minute
- Pro tier: higher limits
- See [Groq pricing](https://console.groq.com/keys)

b) **Reduce batch size**
- Process fewer videos per run
- Add delay between calls

c) **Use faster model (optional)**
```
GROQ_MODEL=mixtral-8x7b-32768
```

d) **Upgrade plan**
- Free tier has limits
- Pay for higher throughput

---

### 7. "Connection error: Failed to connect to Groq API"

**Problem**: Network or API endpoint issue.

**Solutions**:

a) **Check internet connection**
```bash
ping google.com
```

b) **Verify Groq API status**
- Go to [Groq status page](https://status.groq.com/)
- Check if API is down

c) **Verify endpoint URL**
```python
# Should be:
base_url="https://api.groq.com/openai/v1"
```

d) **Check firewall/proxy**
- Corporate networks sometimes block API calls
- Try different network

---

### 8. "JSON decode error in output"

**Problem**: Invalid JSON in daily_digest.json.

**Solutions**:

a) **Check file isn't corrupted**
```bash
python -c "
import json
with open('daily_digest.json') as f:
    json.load(f)
print('JSON is valid!')
"
```

b) **Delete and regenerate**
```bash
del daily_digest.json
python main.py  # Regenerate
```

c) **Check file permissions**
```bash
# Make sure file is writable
chmod 644 daily_digest.json  # Mac/Linux
```

---

### 9. "AttributeError: 'NoneType' object has no attribute 'get'"

**Problem**: YouTube channel ID is invalid or URL format wrong.

**Solutions**:

a) **Verify channel ID format**
- Should start with `UC` followed by 22 characters
- Example: `UCxxxxxxxxxxxxxxxxxxxxxx`

b) **Get correct channel ID**
- Go to channel on YouTube
- Right-click → Inspect
- Search for `"channelId"`

c) **Fix in youtube_sources.csv**
```csv
source_id,type,name,url_or_id,category,last_checked
yt_001,youtube,Tech,UCxxxxxxxxxxxxxxxxxxxxxx,tech,2026-01-01T00:00:00Z
```

d) **Test channel**
```python
from src.models import YouTubeVideoFinder
finder = YouTubeVideoFinder("youtube_key")
info = finder.get_channel_info("UCxxxxxxxxxxxxxxxxxxxxxx")
print(info)
```

---

### 10. "Empty output - no items generated"

**Problem**: No new videos found or all failed processing.

**Solutions**:

a) **Check if videos exist**
- Go to channel on YouTube
- Are there recent videos?
- Videos older than 24 hours won't be included

b) **Increase look-back window**
- Edit `youtube_pipeline.py`
- Change `hours=24` to `hours=48` or `hours=72`

c) **Check channel has active sources**
```bash
python -c "
from src.models import SourceTracker
tracker = SourceTracker('youtube_sources.csv')
sources = tracker.get_active_sources('youtube')
print(f'Found {len(sources)} sources')
for s in sources:
    print(f'  - {s[\"name\"]}: {s[\"url_or_id\"]}')
"
```

d) **Run with debugging**
```python
from src.pipelines import YouTubePipeline
import os

pipeline = YouTubePipeline(
    youtube_api_key=os.getenv('YOUTUBE_API_KEY'),
    groq_api_key=os.getenv('GROQ_API_KEY'),
)

# Check each step
sources = pipeline.source_tracker.get_active_sources('youtube')
print(f"1. Found {len(sources)} sources")

for source in sources:
    videos = pipeline.video_finder.find_new_videos(source['url_or_id'])
    print(f"2. Found {len(videos)} videos in {source['name']}")
```

---

### 11. "Summary is incomplete or cut off"

**Problem**: LLM output is truncated.

**Solutions**:

a) **Increase max_tokens**
```python
# In groq_news_writer.py
response = client.chat.completions.create(
    model=self.model,
    messages=messages,
    max_tokens=1024,  # Increase from 512
)
```

b) **Use more capable model**
```
GROQ_MODEL=llama-3.3-70b-versatile
```

c) **Reduce transcript length**
- Process videos with shorter transcripts first
- Or split long transcripts

---

### 12. "Progress seems stuck"

**Problem**: Application running but no output for a long time.

**Solutions**:

a) **Check what's happening**
- Most likely: YouTube API call or Groq API call
- Groq average response: 0.5-1 second
- YouTube API average response: 1-2 seconds

b) **Add debugging output**
```python
# In youtube_pipeline.py
print(f"Processing {source['name']}...")
```

c) **Run with timeout**
```bash
# Linux/Mac
timeout 60 python main.py

# Windows - use Ctrl+C to stop
python main.py  # Wait max 2 minutes per channel
```

d) **Check API quotas**
- YouTube: 10,000 units/day
- Groq: depends on plan (usually unlimited for free)

---

## Performance Tips

### Speed Up Processing

1. **Use faster model** (less accurate but 2x faster)
```
GROQ_MODEL=mixtral-8x7b-32768
```

2. **Process fewer channels**
- Only add active channels to CSV
- Disable old channels (comment out)

3. **Reduce look-back window**
```python
# In youtube_pipeline.py
videos = self.video_finder.find_new_videos(
    channel_id=channel_id,
    hours=12  # Check only last 12 hours instead of 24
)
```

4. **Batch processing**
- Run once daily automatically
- Don't re-process same videos

---

## Debug Mode

### Enable Verbose Logging

```python
# Add to main.py
import logging
logging.basicConfig(level=logging.DEBUG)

from src.pipelines import main_youtube_pipeline
result = main_youtube_pipeline(...)
```

### Test Individual Components

```python
# Test YouTube API
from src.models import YouTubeVideoFinder
finder = YouTubeVideoFinder("your_key")
videos = finder.find_new_videos("UCxxxxxx")
print(f"Found {len(videos)} videos")

# Test Groq API
from src.models import GroqNewsWriter
writer = GroqNewsWriter("your_key")
summary = writer.summarize("Title", "Long text...", 6)
print(summary)

# Test CSV
from src.models import SourceTracker
tracker = SourceTracker("youtube_sources.csv")
sources = tracker.get_active_sources("youtube")
print(f"Loaded {len(sources)} sources")
```

---

## Need More Help?

1. **Check the logs** - Look for error messages
2. **Read API docs** - [Groq](https://groq.com/), [YouTube](https://developers.google.com/youtube)
3. **Test API keys** - Verify they work independently
4. **Check file paths** - Make sure all files exist and are readable
5. **Review .env** - Ensure all required vars are set

---

**Stuck? Try these solutions in order - usually fixes the problem! 🔧**
