# Testing Guide

## Overview

This document tracks testing approach, known issues, and test results for the AI Newsletter system.

---

## Test Structure

```
tests/
├── __init__.py
├── test_youtube_sources.csv       # Test data (1 channel)
└── test_youtube_finder.py         # YouTubeVideoFinder tests
```

---

## Running Tests

### Run All Tests
```bash
python -m unittest discover tests
```

### Run Specific Test File
```bash
python -m unittest tests.test_youtube_finder
```

### Run Specific Test Class
```bash
python -m unittest tests.test_youtube_finder.TestYouTubeVideoFinderUnit
```

### Run with Verbose Output
```bash
python -m unittest discover tests -v
```

---

## Test Categories

### 1. Unit Tests
- Test individual components in isolation
- Use mocked data (no network calls)
- Fast execution
- Run in CI/CD

**Example**: `TestYouTubeVideoFinderUnit`

### 2. Integration Tests
- Test component interaction
- CSV → SourceTracker → YouTubeVideoFinder
- Use mocked network calls
- Run in CI/CD

**Example**: `TestYouTubeVideoFinderIntegration`

### 3. Live Tests
- Test with real network requests
- Skipped by default
- Run manually for validation
- Not in CI/CD

**Example**: `TestYouTubeVideoFinderLive`

---

## Test Coverage

### YouTubeVideoFinder

| Test Case | Status | Description |
|-----------|--------|-------------|
| Initialization | ✅ Pass | Verifies object creation |
| RSS URL construction | ✅ Pass | Checks correct URL format |
| Find videos with mock data | ✅ Pass | Tests video discovery |
| Filter old videos | ✅ Pass | Tests 24-hour filtering |
| Network error handling | ✅ Pass | Graceful error handling |
| Output structure validation | ✅ Pass | Checks return format |
| CSV integration | ✅ Pass | CSV → Finder flow |

### Pending Tests

- [ ] TranscriptFetcher
- [ ] TextCleaner
- [ ] GroqNewsWriter
- [ ] JSONBuilder
- [ ] YouTubePipeline (end-to-end)

---

## Known Issues

### Issue 1: RSS Feed Delay
**Module**: YouTubeVideoFinder  
**Description**: YouTube RSS feeds may have 10-15 minute delay after video publication  
**Impact**: Very recent videos might not appear immediately  
**Workaround**: Run pipeline periodically (e.g., every 30 minutes)  
**Status**: Expected behavior

### Issue 2: RSS Feed Limit
**Module**: YouTubeVideoFinder  
**Description**: RSS feeds return maximum 15 most recent videos  
**Impact**: If channel uploads >15 videos in 24h, older ones won't appear  
**Workaround**: Run pipeline more frequently (every 6-8 hours)  
**Status**: Expected behavior

---

## Error Tracking

### Format
```
Date: YYYY-MM-DD
Module: module_name
Error: error_description
Input: test_input
Expected: expected_output
Actual: actual_output
Resolution: how_it_was_fixed
```

### Log

#### 2026-01-22: Initial Setup
**Module**: test_youtube_finder  
**Status**: ✅ All tests passing  
**Notes**: Created test suite with mocked RSS data

---

## Test Data

### Test CSV File
Location: `tests/test_youtube_sources.csv`

```csv
source_id,type,name,url_or_id,category,last_checked
yt_test_001,youtube,Test Tech Channel,UCXuqSBlHAE6Xw-yeJA0Tunw,tech,2026-01-21T00:00:00Z
```

Channel: Linus Tech Tips (active, frequent uploads)

---

## Mocking Strategy

### YouTubeVideoFinder
- Mock `requests.get()` for network calls
- Mock `feedparser.parse()` for RSS parsing
- Return controlled test data
- Test both success and failure paths

### Example Mock Structure
```python
mock_feed = Mock()
mock_feed.feed.title = "Test Channel"
mock_feed.entries = [
    Mock(
        title="Test Video",
        published="2026-01-22T12:00:00Z",
        yt_videoid="test123",
        link="https://www.youtube.com/watch?v=test123"
    )
]
```

---

## CI/CD Integration

### Pre-commit Tests
```bash
# Run fast unit tests only
python -m unittest tests.test_youtube_finder.TestYouTubeVideoFinderUnit
```

### Full Test Suite
```bash
# Run all tests except live
python -m unittest discover tests -v
```

### Live Validation (Manual)
```bash
# Run live tests with real RSS
python -m unittest tests.test_youtube_finder.TestYouTubeVideoFinderLive
```

---

## Testing Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Mock External Calls**: Don't rely on network in unit tests
3. **Test Edge Cases**: Empty feeds, network errors, malformed data
4. **Descriptive Names**: `test_find_new_videos_filters_old_videos`
5. **Assert Clearly**: One assertion per logical check
6. **Clean Up**: Use setUp/tearDown for fixtures

---

## Adding New Tests

### Step 1: Create Test File
```bash
# In tests/ directory
touch test_module_name.py
```

### Step 2: Import Module
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.module_name import ClassName
```

### Step 3: Write Test Class
```python
class TestModuleName(unittest.TestCase):
    def setUp(self):
        # Setup fixtures
        pass
    
    def test_specific_functionality(self):
        # Test code
        self.assertEqual(expected, actual)
```

### Step 4: Run Tests
```bash
python -m unittest tests.test_module_name
```

---

## Test Results Format

### Console Output
```
test_find_new_videos_filters_old_videos (tests.test_youtube_finder.TestYouTubeVideoFinderUnit) ... ok
test_find_new_videos_with_mock_data (tests.test_youtube_finder.TestYouTubeVideoFinderUnit) ... ok
test_handles_network_error (tests.test_youtube_finder.TestYouTubeVideoFinderUnit) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.045s

OK
```

### Failed Test Output
```
FAIL: test_example (tests.test_module.TestClass)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "tests/test_module.py", line 42, in test_example
    self.assertEqual(expected, actual)
AssertionError: 'expected' != 'actual'
```

---

## Dependencies

Tests require:
```
unittest (built-in)
unittest.mock (built-in)
requests
feedparser
```

Install test dependencies:
```bash
pip install -r requirements.txt
```

---

## Next Steps

1. ✅ Create test structure
2. ✅ Implement YouTubeVideoFinder tests
3. ⏳ Add TranscriptFetcher tests
4. ⏳ Add TextCleaner tests
5. ⏳ Add GroqNewsWriter tests
6. ⏳ Add JSONBuilder tests
7. ⏳ Add end-to-end pipeline tests
8. ⏳ Set up CI/CD pipeline

---

**Last Updated**: 2026-01-22  
**Status**: YouTubeVideoFinder tests complete
