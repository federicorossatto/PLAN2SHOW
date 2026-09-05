"""Shared PLAN2SHOW constants."""

APP_NAME = "PLAN2SHOW"
APP_AUTHOR = "Federico Rossatto"
APP_VERSION = "1.3"

REQUIRED_PROFILE_KEYS = ["FIXTURE_PATCH", "MACRO_GROUPS", "COMMANDS_PRESETS"]
REQUIRED_COLUMNS = [
    "Cue Number", "Name", "Minutes", "Seconds",
    "Fade", "BPM", "Actions", "Director Notes"
]
SUPPORTED_FRAME_RATES = (24, 25, 30)
