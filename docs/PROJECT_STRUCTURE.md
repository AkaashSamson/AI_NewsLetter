# Project Structure Guide

## Folder Organization

```
AI_NewsLetter/
│
├── src/                               # All source code (Python package)
│   ├── __init__.py                   # Makes src a package
│   │
│   ├── models/                       # Domain models & API clients
│   │   ├── __init__.py
│   │   ├── source_tracker.py         # CSV source management (YouTube channels)
│   │   ├── youtube_finder.py         # YouTube API v3 integration
│   │   ├── transcript_fetcher.py     # YouTube transcript API client
│   │   └── groq_news_writer.py       # Groq LLM (OpenAI client)
│   │
│   ├── utils/                        # Utility functions (generic, reusable)
│   │   ├── __init__.py
│   │   ├── text_cleaner.py           # Text preprocessing
│   │   └── json_builder.py           # JSON serialization
│   │
│   ├── pipelines/                    # Orchestration & workflows
│   │   ├── __init__.py
│   │   └── youtube_pipeline.py       # Main YouTube processing pipeline
│   │
│   └── config/                       # Configuration (reserved for Phase 2+)
│       └── __init__.py
│
├── docs/                             # All documentation
│   ├── SETUP_GUIDE.md               # Quick start & installation
│   ├── ARCHITECTURE.md              # System design & data flow
│   ├── API_REFERENCE.md             # Complete API documentation
│   ├── TROUBLESHOOTING.md           # Common issues & solutions
│   ├── PROJECT_STRUCTURE.md         # This file - folder organization
│   └── README.md                    # Documentation index
│
├── .env                             # Environment variables (secrets)
│   └── Never commit this file!
│
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project metadata
├── .gitignore                       # Git exclusions
├── youtube_sources.csv              # Channel configuration
├── README.md                        # Project README
│
└── ai_news/                         # Virtual environment (Python venv)
    ├── Scripts/                     # Executables (activate, pip, python)
    └── Lib/                         # Installed packages

```

---

## Folder Purposes

### `src/` - Main Application Code
- **Purpose**: Python package containing all application logic
- **Why**: Keeps code organized and allows `from src.models import ...` imports
- **When to add**: Create new subfolders for new phases (src/blog_models/, src/email_models/)

### `src/models/`
- **Purpose**: Domain models and external API clients
- **Contents**:
  - Data fetchers (YouTube, transcripts, etc.)
  - LLM integrations (Groq, OpenAI, etc.)
  - Domain objects
- **When to add**: Add new fetchers (BlogFetcher, TwitterFetcher, etc.)
- **Why separate**: API clients have external dependencies and lifecycle

### `src/utils/`
- **Purpose**: Generic, reusable utility functions
- **Contents**:
  - Text processing
  - Data formatting
  - Common algorithms
- **Characteristics**: No external API calls, no complex state
- **When to add**: Add formatters (EmailFormatter, HTMLFormatter, etc.)
- **Why separate**: These utilities should be usable by any model or pipeline

### `src/pipelines/`
- **Purpose**: Orchestration and workflow logic
- **Contents**:
  - Main processing workflows
  - Integration logic (connects models and utils)
  - Business logic
- **When to add**: Add new pipelines for Phase 2 (blog_pipeline) and Phase 3 (email_pipeline)
- **Why separate**: Pipelines coordinate multiple components

### `src/config/` (Reserved)
- **Purpose**: Configuration management (currently unused)
- **Planned use**: Environment-specific configs, logging setup, etc.
- **When to add**: Phase 2+, when app grows

### `docs/` - Documentation
- **Purpose**: User-facing and developer documentation
- **Contents**:
  - Setup guides
  - API reference
  - Architecture diagrams
  - Troubleshooting guides
- **Why separate**: Documentation shouldn't live with code

---

## Import Patterns

### Standard Imports
```python
# From src/ - use relative imports (within src)
from src.models import YouTubeVideoFinder
from src.utils import TextCleaner
from src.pipelines import main_youtube_pipeline

# From Python packages
from openai import OpenAI
from datetime import datetime
```

### Inside src/ (submodule to submodule)
```python
# In src/pipelines/youtube_pipeline.py
from src.models import YouTubeVideoFinder, SourceTracker
from src.utils import JSONBuilder
```

### In main.py
```python
import sys
sys.path.insert(0, 'src')  # Adds src to import path

from pipelines import main_youtube_pipeline
```

---

## File Naming Conventions

### Python Modules
- **Files**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions**: `lowercase_with_underscores()`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`

### Examples
```python
# youtube_finder.py
class YouTubeVideoFinder:
    def find_new_videos(self, channel_id):
        MAX_RESULTS = 50
        results = []
        # ...
```

### Documentation Files
- **Index**: `README.md`
- **Guides**: `NOUN_GUIDE.md` (e.g., SETUP_GUIDE.md)
- **Technical**: `TOPIC.md` (e.g., ARCHITECTURE.md)
- **Reference**: `REFERENCE.md` or `TOPIC_REFERENCE.md`

---

## Phase-Based Expansion

### Phase 1 (Complete) - YouTube
```
src/
├── models/
│   └── [YouTube APIs]
├── utils/
│   └── [Text, JSON utilities]
└── pipelines/
    └── youtube_pipeline.py
```

### Phase 2 (Planned) - Blog/RSS
```
src/
├── models/
│   ├── [YouTube APIs]
│   └── blog_fetcher.py      ← NEW
├── utils/
│   ├── [Text, JSON utilities]
│   └── rss_parser.py        ← NEW
└── pipelines/
    ├── youtube_pipeline.py
    └── blog_pipeline.py     ← NEW
```

### Phase 3 (Planned) - Email Delivery
```
src/
├── models/
│   └── [All above + email_sender.py] ← NEW
├── utils/
│   └── [All above + email_formatter.py] ← NEW
└── pipelines/
    └── [All above + email_pipeline.py] ← NEW
```

---

## Adding New Features

### Adding a New Source Type (e.g., RSS Feeds)

1. **Create fetcher in models/**
   ```python
   # src/models/rss_fetcher.py
   class RSSFetcher:
       def fetch_feeds(self, feed_url):
           # ...
   ```

2. **Add to imports**
   ```python
   # src/models/__init__.py
   from .rss_fetcher import RSSFetcher
   ```

3. **Create pipeline (or update existing)**
   ```python
   # src/pipelines/blog_pipeline.py
   from src.models import RSSFetcher, GroqNewsWriter
   class BlogPipeline:
       # ...
   ```

4. **Update main.py**
   ```python
   from pipelines import main_youtube_pipeline, main_blog_pipeline
   ```

---

## Dependencies Between Modules

```
┌─────────────┐
│  main.py    │  <- Entry point
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Pipelines      │  <- Orchestration layer
└────┬────────────┘
     │
     ├──────────────┬──────────────┐
     │              │              │
     ▼              ▼              ▼
┌─────────┐   ┌─────────┐   ┌──────────┐
│ Models  │   │ Models  │   │  Utils   │
│ (APIs)  │   │ (LLM)   │   │(Utility) │
└─────────┘   └─────────┘   └──────────┘
```

**Key Rule**: 
- Models don't depend on Pipelines
- Pipelines depend on Models and Utils
- Utils don't depend on Models or Pipelines

---

## File Locations Quick Reference

| Purpose | Location |
|---------|----------|
| YouTube API integration | `src/models/youtube_finder.py` |
| Transcript fetching | `src/models/transcript_fetcher.py` |
| LLM summarization | `src/models/groq_news_writer.py` |
| Source CSV management | `src/models/source_tracker.py` |
| Text cleaning | `src/utils/text_cleaner.py` |
| JSON building | `src/utils/json_builder.py` |
| Main workflow | `src/pipelines/youtube_pipeline.py` |
| Application entry | `main.py` |
| Configuration | `.env` |
| Setup guide | `docs/SETUP_GUIDE.md` |
| API docs | `docs/API_REFERENCE.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Troubleshooting | `docs/TROUBLESHOOTING.md` |

---

## Best Practices

### 1. Keep Models Focused
- One model = one external API or concept
- Don't mix YouTube and Groq logic in same file

### 2. Utilities are Generic
- `TextCleaner` works on any text
- `JSONBuilder` works with any data structure
- No hardcoded logic for specific APIs

### 3. Pipelines Orchestrate
- Connect models and utilities
- Implement business logic
- Handle error recovery

### 4. Test in Isolation
```python
# Test YouTubeVideoFinder without pipeline
from src.models import YouTubeVideoFinder
finder = YouTubeVideoFinder("key")
videos = finder.find_new_videos("channel")

# Test TextCleaner without pipeline
from src.utils import TextCleaner
clean = TextCleaner.clean_full(dirty_text)
```

### 5. Configuration via Environment
- Never hardcode API keys
- Use `.env` for all secrets
- Use environment variables for settings

---

## Migration Checklist

If you're coming from the old flat structure:

- ✅ Code moved to `src/models/` and `src/utils/`
- ✅ Documentation moved to `docs/`
- ✅ API key moved to `.env`
- ✅ Imports updated in `main.py`
- ✅ `requirements.txt` updated with new dependencies
- ✅ `.gitignore` updated to exclude `.env`

---

**Structure is clean, extensible, and ready for growth! 🚀**
