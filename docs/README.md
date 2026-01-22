# Documentation Index

Welcome to the AI Newsletter project! Here's where to find everything.

## 📚 Getting Started

### New to the Project?
Start here → [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Installation steps
- How to run the pipeline
- API key setup

### Want to Understand the Architecture?
Read → [ARCHITECTURE.md](ARCHITECTURE.md)
- System design overview
- Data flow diagrams
- Module responsibilities
- Design decisions

## 🔧 Implementation Details

### API Reference
See → [API_REFERENCE.md](API_REFERENCE.md)
- Complete method documentation
- Function signatures and parameters
- Usage examples
- Error handling

### Project Structure
Learn → [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- Folder organization
- Import patterns
- File naming conventions
- Phase-based expansion plan

## ❓ Help & Troubleshooting

### Common Issues?
Check → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- API key errors
- Missing files
- Network issues
- Performance tips
- Debug mode

---

## Quick Links

| Question | Answer |
|----------|--------|
| How do I install? | [SETUP_GUIDE.md](SETUP_GUIDE.md#quick-start) |
| How does it work? | [ARCHITECTURE.md](ARCHITECTURE.md#system-design) |
| What APIs are available? | [API_REFERENCE.md](API_REFERENCE.md) |
| Where are the files? | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) |
| Something's broken! | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| How do I extend it? | [ARCHITECTURE.md](ARCHITECTURE.md#extension-points) |

---

## 🚀 Common Tasks

### Running the Pipeline
```bash
python main.py
```
See: [SETUP_GUIDE.md](SETUP_GUIDE.md#4-run-pipeline)

### Adding a YouTube Channel
1. Edit `youtube_sources.csv`
2. Add channel ID (format: `UCxxxxxxxxxxxxxx`)
3. Run pipeline

See: [SETUP_GUIDE.md](SETUP_GUIDE.md#3-add-youtube-channels)

### Using Different LLM Model
Edit `.env`:
```
GROQ_MODEL=mixtral-8x7b-32768
```
See: [SETUP_GUIDE.md](SETUP_GUIDE.md#available-groq-models)

### Testing Individual Components
```python
from src.models import YouTubeVideoFinder
finder = YouTubeVideoFinder("your_key")
videos = finder.find_new_videos("channel_id")
```
See: [TROUBLESHOOTING.md](TROUBLESHOOTING.md#debug-mode)

### Adding Blog Support (Phase 2)
See: [ARCHITECTURE.md](ARCHITECTURE.md#adding-blog-support-phase-2)

### Adding Email Delivery (Phase 3)
See: [ARCHITECTURE.md](ARCHITECTURE.md#adding-email-delivery-phase-3)

---

## 📖 Document Overview

### SETUP_GUIDE.md (3 min read)
Quick start guide with:
- Installation instructions
- Running the pipeline
- API key setup
- Troubleshooting quicklinks

**Read this if**: You want to get it running quickly

### ARCHITECTURE.md (8 min read)
System design document with:
- Modular architecture overview
- Processing flow diagrams
- Data structures
- API integrations
- Design decisions
- Extension points

**Read this if**: You want to understand how it works

### API_REFERENCE.md (10 min read)
Complete API documentation with:
- All classes and methods
- Parameters and return types
- Usage examples
- Error handling
- Code samples

**Read this if**: You're building on top of the system

### PROJECT_STRUCTURE.md (5 min read)
Project organization guide with:
- Folder hierarchy
- File purposes
- Import patterns
- Naming conventions
- Phase-based expansion plan

**Read this if**: You want to add new features

### TROUBLESHOOTING.md (15 min read)
Problem-solving guide with:
- 12 common issues
- Step-by-step solutions
- Performance tips
- Debug mode
- API quota information

**Read this if**: Something isn't working

---

## 🔑 Key Concepts

### Groq API
- Fast LLM service with free tier
- Supports OpenAI-compatible interface
- Models: `llama-3.3-70b-versatile` (recommended)
- See: [SETUP_GUIDE.md](SETUP_GUIDE.md#available-groq-models)

### YouTube Data API v3
- Discovers videos from channels
- Requires API key from Google Cloud
- Limited to 10,000 units/day on free tier
- See: [SETUP_GUIDE.md](SETUP_GUIDE.md#get-youtube-api-key)

### YouTube Transcript API
- Fetches video captions
- Unofficial Python wrapper
- Works on videos with transcripts enabled

### Environment Variables (.env)
- Stores API keys securely
- Never committed to git
- Loaded automatically by app
- See: [SETUP_GUIDE.md](SETUP_GUIDE.md#environment-variables)

---

## 🗂️ File Locations

```
docs/
├── README.md                 ← This file
├── SETUP_GUIDE.md           ← Quick start
├── ARCHITECTURE.md          ← System design
├── API_REFERENCE.md         ← Method docs
├── PROJECT_STRUCTURE.md     ← Folder organization
└── TROUBLESHOOTING.md       ← Problem solving
```

---

## 📞 Still Have Questions?

1. **Check the appropriate doc** - Start with the question table above
2. **Search within docs** - Use Ctrl+F to search
3. **Review code examples** - See API_REFERENCE for working examples
4. **Check debug mode** - See TROUBLESHOOTING for detailed debugging

---

## 🎯 Next Steps

- [ ] Read [SETUP_GUIDE.md](SETUP_GUIDE.md)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Set up `.env` with API keys
- [ ] Add channels to `youtube_sources.csv`
- [ ] Run: `python main.py`
- [ ] Check output: `daily_digest.json`
- [ ] Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand what happened
- [ ] Explore [API_REFERENCE.md](API_REFERENCE.md) to extend the system

---

**Everything you need is documented. Happy building! 🚀**
