"""Shared fixtures for the PLAN2SHOW test suite."""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from profiles import get_default_profile


@pytest.fixture
def default_profile():
    """Return a fresh profile for every test."""
    return get_default_profile()


@pytest.fixture
def basic_rows():
    """Return two valid compiler rows without file I/O."""
    return [
        {
            "Cue Number": "1",
            "Name": "Intro",
            "Minutes": "0",
            "Seconds": "0",
            "Fade": "0",
            "BPM": "120",
            "Actions": "Smoke: 25%",
            "Director Notes": "",
            "_source_row": "6",
        },
        {
            "Cue Number": "2",
            "Name": "Verse",
            "Minutes": "0",
            "Seconds": "5",
            "Fade": "2",
            "BPM": "",
            "Actions": "Sides: Blue, 30%",
            "Director Notes": "",
            "_source_row": "7",
        },
    ]
