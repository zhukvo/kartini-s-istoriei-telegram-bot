# Run tests in a module
# pytest tests.py
import pytest
import main

def test_download_stories():
    result = loadStories()

    assert len(result) > 0
    assert len(result[0]) == 4
    