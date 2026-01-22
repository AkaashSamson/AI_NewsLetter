# Verification & Testing Guide

Verify your project is set up correctly by running these checks.

---

## ✅ Pre-Flight Checklist

### 1. Python Environment

```bash
# Check Python version (3.8+)
python --version
# Expected: Python 3.x.x

# Check virtual environment is active
# Windows: should see (ai_news) in command prompt
# Mac/Linux: should see (ai_news) in terminal
```

### 2. Dependencies Installed

```bash
# Check dependencies
pip list

# Look for:
# openai >= 1.40.0
# groq >= 0.4.0
# python-dotenv >= 1.0.0
# google-api-python-client
# youtube-transcript-api
```

If missing, run:
```bash
pip install -r requirements.txt
```

### 3. .env File Exists

```bash
# Windows
type .env

# Mac/Linux
cat .env

# Should show:
# GROQ_API_KEY=gsk_0TC6eUhwixsBYY3...
# YOUTUBE_API_KEY=(should be empty or have key)
```

### 4. Project Structure

```bash
# Check src/ folder exists
ls src/                 # or dir src/ on Windows

# Should show:
# models/  utils/  pipelines/  config/  __init__.py
```

---

## 🧪 Test Individual Components

### Test 1: Groq API Connection

```bash
python -c "
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(
    api_key=os.getenv('GROQ_API_KEY'),
    base_url='https://api.groq.com/openai/v1'
)

response = client.chat.completions.create(
    model='llama-3.3-70b-versatile',
    messages=[{'role': 'user', 'content': 'Say hello!'}]
)

print('✓ Groq API works!')
print(f'Response: {response.choices[0].message.content}')
"
```

**Expected**: Should print success message and hello

### Test 2: Module Imports

```bash
python -c "
from src.models import (
    SourceTracker,
    YouTubeVideoFinder,
    TranscriptFetcher,
    GroqNewsWriter
)
from src.utils import TextCleaner, JSONBuilder
from src.pipelines import YouTubePipeline

print('✓ All imports successful!')
"
```

**Expected**: Should print success message with no errors

### Test 3: Environment Variables

```bash
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

print('Environment Variables:')
print(f'  GROQ_API_KEY: {os.getenv(\"GROQ_API_KEY\")[:10]}...')
print(f'  YOUTUBE_API_KEY: {os.getenv(\"YOUTUBE_API_KEY\", \"[NOT SET]\")[:10]}...')
print(f'  GROQ_MODEL: {os.getenv(\"GROQ_MODEL\", \"DEFAULT\")}')
print('✓ Environment variables loaded!')
"
```

**Expected**: Should show API key prefix and settings

### Test 4: YouTube Sources CSV

```bash
python -c "
from src.models import SourceTracker

tracker = SourceTracker('youtube_sources.csv')
sources = tracker.get_active_sources('youtube')

print(f'✓ CSV loaded successfully!')
print(f'  Found {len(sources)} YouTube sources')
for s in sources[:3]:
    print(f'    - {s[\"name\"]}: {s[\"url_or_id\"]}')
"
```

**Expected**: Should load CSV and list channels

### Test 5: Text Cleaning

```bash
python -c "
from src.utils import TextCleaner

dirty = '<p>Hello  &nbsp; <b>world</b>!!</p>'
clean = TextCleaner.clean_full(dirty)

print(f'Original: {dirty}')
print(f'Cleaned: {clean}')
print('✓ Text cleaning works!')
"
```

**Expected**: HTML removed and spaces normalized

### Test 6: JSON Building

```bash
python -c "
from src.utils import JSONBuilder

item = JSONBuilder.build_item(
    'youtube',
    'Test Title',
    'This is a test summary.',
    'https://youtube.com/watch?v=test'
)

print('✓ JSON building works!')
print(f'Item: {item}')
"
```

**Expected**: Should create valid JSON item structure

---

## 🔌 End-to-End Test

### Full Pipeline Test (requires YouTube API key)

If you have YouTube API key configured:

```bash
python -c "
import os
from dotenv import load_dotenv
from src.pipelines import main_youtube_pipeline

load_dotenv()

try:
    result = main_youtube_pipeline(
        youtube_api_key=os.getenv('YOUTUBE_API_KEY'),
        groq_api_key=os.getenv('GROQ_API_KEY'),
        groq_model='llama-3.3-70b-versatile'
    )
    
    print('✓ Pipeline executed successfully!')
    print(f'Generated {result[\"count\"]} items')
    print(f'Date: {result[\"date\"]}')
    
except Exception as e:
    print(f'Pipeline error: {e}')
    print('This is expected if YouTube API key is not configured')
"
```

**Expected**: Should either run successfully or fail gracefully

---

## 📊 Quick Test Summary

Run this script to test everything at once:

```bash
python -c "
import sys
from dotenv import load_dotenv
import os

load_dotenv()

tests_passed = 0
tests_total = 0

def test(name, func):
    global tests_passed, tests_total
    tests_total += 1
    try:
        func()
        print(f'✓ {name}')
        tests_passed += 1
        return True
    except Exception as e:
        print(f'✗ {name}: {str(e)[:50]}')
        return False

# Run tests
test('Imports', lambda: (
    __import__('src.models'),
    __import__('src.utils'),
    __import__('src.pipelines')
))

test('Environment', lambda: (
    os.getenv('GROQ_API_KEY') or (_ for _ in ()).throw(Exception('GROQ_API_KEY not set'))
))

test('Groq Connection', lambda: (
    __import__('openai').OpenAI(
        api_key=os.getenv('GROQ_API_KEY'),
        base_url='https://api.groq.com/openai/v1'
    )
))

test('CSV Loading', lambda: (
    __import__('src.models', fromlist=['SourceTracker']).SourceTracker('youtube_sources.csv').get_active_sources('youtube')
))

test('Text Cleaning', lambda: (
    __import__('src.utils', fromlist=['TextCleaner']).TextCleaner.clean_full('<p>Test</p>')
))

test('JSON Building', lambda: (
    __import__('src.utils', fromlist=['JSONBuilder']).JSONBuilder.build_item('youtube', 'Title', 'Summary', 'Link')
))

print(f'\n{tests_passed}/{tests_total} tests passed')
sys.exit(0 if tests_passed == tests_total else 1)
"
```

---

## 🐛 Common Test Issues

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution**: Make sure you're in project root directory
```bash
cd c:\Users\Akaash\Desktop\D_Drive\Project\AI_NewsLetter
python -c "from src.models import SourceTracker"
```

### Issue: "GROQ_API_KEY not set"

**Solution**: Check .env file exists and contains key
```bash
# Windows
type .env

# Mac/Linux
cat .env
```

### Issue: "No transcripts found"

**Solution**: This is normal - videos must have captions enabled

### Issue: "YouTube API error"

**Solution**: 
1. Get YouTube API key from Google Cloud Console
2. Add to .env: `YOUTUBE_API_KEY=AIzaSy...`
3. Make sure API is enabled in Google Cloud

---

## ✅ Success Criteria

Project is properly set up when:

- [ ] All imports work without errors
- [ ] Groq API connection successful
- [ ] .env file loaded correctly
- [ ] YouTube sources CSV loaded
- [ ] Text cleaning produces output
- [ ] JSON building creates valid structure
- [ ] `python main.py` runs without ModuleNotFoundError
- [ ] Output file created (daily_digest.json)
- [ ] Documentation is readable

---

## 🚀 Ready to Run

Once all tests pass:

```bash
# Run the full pipeline
python main.py

# Should output:
# ======================================================================
# AI Newsletter - Daily Intelligence Agent with Groq LLM
# ======================================================================
# 
# [PHASE 1] YouTube Pipeline with Groq
# ...
# ✓ Generated daily digest:
#   Date: 2026-01-22
#   Items: 3
#   Output: daily_digest.json
```

---

## 📋 Troubleshooting Checklist

If tests fail:

- [ ] Python 3.8+ installed? → `python --version`
- [ ] Dependencies installed? → `pip install -r requirements.txt`
- [ ] Virtual environment active? → Check command prompt
- [ ] .env file exists? → `ls .env` or `type .env`
- [ ] In project root? → `pwd` or `cd` to project
- [ ] API keys in .env? → Check GROQ_API_KEY exists
- [ ] src/ folder exists? → `ls src/`
- [ ] Models exist? → `ls src/models/`

See `docs/TROUBLESHOOTING.md` for detailed solutions.

---

**All tests passing? You're ready to go! 🚀**
