# API Reference

## Models Package

### SourceTracker

**Location**: `src/models/source_tracker.py`

```python
from src.models import SourceTracker

tracker = SourceTracker("youtube_sources.csv")
```

**Methods**:

#### `load_sources()`
Load sources from CSV file.
```python
tracker.load_sources()  # Called automatically in __init__
```

#### `get_active_sources(source_type: str)`
Get all sources of a specific type.
```python
youtube_sources = tracker.get_active_sources("youtube")
# Returns: List[Dict]
```

#### `update_last_checked(source_id: str, timestamp: str = None)`
Update the last_checked timestamp.
```python
tracker.update_last_checked("yt_001")  # Uses current time
tracker.update_last_checked("yt_001", "2026-01-22T12:00:00Z")  # Custom time
```

#### `get_source_by_id(source_id: str)`
Get a single source by ID.
```python
source = tracker.get_source_by_id("yt_001")
# Returns: Dict or None
```

---

### YouTubeVideoFinder

**Location**: `src/models/youtube_finder.py`

```python
from src.models import YouTubeVideoFinder

finder = YouTubeVideoFinder(api_key="YOUR_KEY")
```

**Methods**:

#### `find_new_videos(channel_id, hours=24, last_checked=None)`
Find videos published in last N hours.
```python
videos = finder.find_new_videos(
    channel_id="UCxxxxxxxxxxxxxx",
    hours=24,
    last_checked="2026-01-22T12:00:00Z"
)
# Returns: List[Dict] with video_id, title, link, etc.
```

#### `get_channel_info(channel_id: str)`
Get channel metadata.
```python
info = finder.get_channel_info("UCxxxxxxxxxxxxxx")
# Returns: Dict or None
```

---

### TranscriptFetcher

**Location**: `src/models/transcript_fetcher.py`

```python
from src.models import TranscriptFetcher

fetcher = TranscriptFetcher()
```

**Methods**:

#### `fetch_transcript(video_id, languages=None)`
Get raw transcript.
```python
text = fetcher.fetch_transcript("xxxxx", languages=['en'])
# Returns: str or None
```

#### `clean_transcript(text: str)`
Clean raw transcript.
```python
clean = fetcher.clean_transcript(raw_text)
# Removes: timestamps, brackets, filler words
# Returns: str
```

#### `fetch_and_clean(video_id, title, link, languages=None)`
Fetch and clean in one call.
```python
result = fetcher.fetch_and_clean(
    video_id="xxxxx",
    title="Video Title",
    link="https://youtube.com/watch?v=xxxxx"
)
# Returns: Dict with video_id, title, clean_text, link
```

---

### GroqNewsWriter

**Location**: `src/models/groq_news_writer.py`

```python
from src.models import GroqNewsWriter

writer = GroqNewsWriter(
    model="llama-3.3-70b-versatile",
    api_key="YOUR_GROQ_KEY"
)
```

**Methods**:

#### `summarize(title, text, max_lines=6)`
Generate summary using Groq.
```python
summary = writer.summarize(
    title="Video Title",
    text="Long transcript text...",
    max_lines=6
)
# Returns: str (summary text)
```

#### `process_content(title, text)`
Summarize and return title + summary.
```python
result = writer.process_content(
    title="Video Title",
    text="Long text..."
)
# Returns: Dict with title, summary
```

#### `get_available_models()`
List available Groq models.
```python
models = GroqNewsWriter.get_available_models()
# Returns: Dict[str, str]
```

---

## Utils Package

### TextCleaner

**Location**: `src/utils/text_cleaner.py`

```python
from src.utils import TextCleaner
```

**Methods** (all static):

#### `clean_html(text: str)`
Remove HTML tags and entities.
```python
clean = TextCleaner.clean_html("<p>Hello &nbsp; world</p>")
# Returns: "Hello   world"
```

#### `normalize_spaces(text: str)`
Fix whitespace issues.
```python
clean = TextCleaner.normalize_spaces("Text  with\n\n\nmany spaces")
# Returns: "Text with\n\nmany spaces"
```

#### `remove_repeated_headers(text: str)`
Remove duplicate lines.
```python
clean = TextCleaner.remove_repeated_headers(text_with_duplicates)
# Returns: text with duplicates removed
```

#### `remove_short_lines(text: str, min_length=10)`
Remove short lines (navigation cruft).
```python
clean = TextCleaner.remove_short_lines(text, min_length=15)
# Returns: text with short lines removed
```

#### `clean_full(text: str, remove_short_lines=True, min_line_length=10)`
Apply all cleaning operations.
```python
clean = TextCleaner.clean_full(dirty_text)
# Returns: fully cleaned text
```

---

### JSONBuilder

**Location**: `src/utils/json_builder.py`

```python
from src.utils import JSONBuilder
```

**Methods** (all static):

#### `build_item(item_type, title, summary, link)`
Create single news item.
```python
item = JSONBuilder.build_item(
    item_type="youtube",
    title="Video Title",
    summary="Summary text...",
    link="https://youtube.com/watch?v=xxxxx"
)
# Returns: Dict with type, title, summary, link
```

#### `build_daily_digest(items, date=None)`
Create complete digest JSON.
```python
digest = JSONBuilder.build_daily_digest(items_list)
# date defaults to today
digest = JSONBuilder.build_daily_digest(items_list, date="2026-01-22")
# Returns: Dict with date, count, items
```

#### `save_to_file(data, filepath)`
Write JSON to file.
```python
success = JSONBuilder.save_to_file(digest, "output.json")
# Returns: bool
```

#### `load_from_file(filepath)`
Read JSON from file.
```python
digest = JSONBuilder.load_from_file("output.json")
# Returns: Dict or None
```

---

## Pipelines Package

### YouTubePipeline

**Location**: `src/pipelines/youtube_pipeline.py`

```python
from src.pipelines import YouTubePipeline, main_youtube_pipeline
```

#### Class Usage
```python
pipeline = YouTubePipeline(
    youtube_api_key="YOUR_KEY",
    groq_api_key="YOUR_GROQ_KEY",
    sources_file="youtube_sources.csv",
    groq_model="llama-3.3-70b-versatile"
)
```

**Methods**:

#### `process_all_youtube_sources()`
Process all channels in sources file.
```python
result_json = pipeline.process_all_youtube_sources()
# Returns: Dict with date, count, items
```

#### `process_single_channel(source)`
Process one channel.
```python
items = pipeline.process_single_channel(source_dict)
# Returns: List[Dict] of items
```

#### Function Usage
```python
result = main_youtube_pipeline(
    youtube_api_key="YOUR_KEY",
    groq_api_key="YOUR_GROQ_KEY",
    output_file="daily_digest.json",
    groq_model="llama-3.3-70b-versatile"
)
# Returns: Dict with date, count, items
# Also saves to output_file
```

---

## Examples

### Example 1: Full Pipeline
```python
from src.pipelines import main_youtube_pipeline

result = main_youtube_pipeline(
    youtube_api_key="youtube_key",
    groq_api_key="groq_key"
)

print(f"Generated {result['count']} items")
```

### Example 2: Step-by-Step
```python
from src.models import *
from src.utils import *

# Load sources
tracker = SourceTracker("youtube_sources.csv")
sources = tracker.get_active_sources("youtube")

# Process first channel
source = sources[0]
finder = YouTubeVideoFinder("youtube_key")
videos = finder.find_new_videos(source['url_or_id'])

# Process first video
video = videos[0]
fetcher = TranscriptFetcher()
transcript = fetcher.fetch_and_clean(
    video['video_id'],
    video['title'],
    video['link']
)

# Summarize
from src.models import GroqNewsWriter
writer = GroqNewsWriter(api_key="groq_key")
summary = writer.process_content(
    transcript['title'],
    transcript['clean_text']
)

# Build item
item = JSONBuilder.build_item(
    "youtube",
    summary['title'],
    summary['summary'],
    video['link']
)

print(item)
```

### Example 3: Custom Text Cleaning
```python
from src.utils import TextCleaner

dirty_text = "<p>Hello  &nbsp; <b>world</b>!!</p>"

# Step by step
html_clean = TextCleaner.clean_html(dirty_text)
space_clean = TextCleaner.normalize_spaces(html_clean)

# Or all at once
clean = TextCleaner.clean_full(dirty_text)
```

---

## Error Handling

### Missing API Keys
```python
try:
    writer = GroqNewsWriter()  # No key provided
except ValueError as e:
    print(f"Error: {e}")
    # Handle missing key
```

### Missing Transcripts
```python
result = fetcher.fetch_and_clean(video_id)
if result is None:
    print("No transcript available")
    continue  # Skip this video
```

### API Failures
```python
try:
    videos = finder.find_new_videos(channel_id)
except Exception as e:
    print(f"Error: {e}")
    # Returns empty list on error
    videos = []
```

---

**Ready to integrate! All APIs documented and ready to use. 🚀**
