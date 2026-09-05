"""Stage profile creation, validation, loading, and saving."""

import json
import os
import re

from constants import REQUIRED_PROFILE_KEYS


def normalize_key(text):
    """Normalize user-facing profile keys for comparison."""
    return str(text).lower().replace(" ", "").replace("_", "")

def get_default_profile():
    return {
        "FIXTURE_PATCH": {
            "Smoke": "Fixture 21", "Followspot": "Fixture 22", 
            "White 1": "Fixture 1", "White 2": "Fixture 2",
            "White 3": "Fixture 3", "White 4": "Fixture 4",
            "Blinder 1": "Fixture 5", "Blinder 2": "Fixture 6",
            "Par 1": "Fixture 9", "Par 2": "Fixture 10",
            "Par 3": "Fixture 11", "Par 4": "Fixture 12",
            "Side 1": "Fixture 13", "Side 2": "Fixture 14",
            "Side 3": "Fixture 15", "Side 4": "Fixture 16",
            "Side 5": "Fixture 17", "Side 6": "Fixture 18",
            "Side 7": "Fixture 19", "Side 8": "Fixture 20"
        },
        "MACRO_GROUPS": {
            "Pars": "Fixture 9 Thru 12", "Sides": "Fixture 13 Thru 20",
            "Whites": "Fixture 1 Thru 4", "Blinders": "Fixture 5 + 6",
            "Sides Front": "Fixture 13 + 14 + 17 + 18",
            "Sides Back": "Fixture 15 + 16 + 19 + 20",
            "Sides L": "Fixture 13 + 15 + 17 + 19",
            "Sides R": "Fixture 14 + 16 + 18 + 20",
            "Stand L": "Fixture 1 + 2 + 5 + 9 + 10",
            "Stand R": "Fixture 3 + 4 + 6 + 11 + 12",
            "Full Rig": "Fixture 1 Thru 6 + 9 Thru 20",
            "BPM Show": "SpecialMaster 3.1"
        },
        "COMMANDS_PRESETS": {
            "Full": "At 100", "Max": "At 100", 
            "Out": "At 0", "Blackout": "At 0",
            "Red": "At Preset 4.1", "Yellow": "At Preset 4.2",
            "Green": "At Preset 4.3", "Cyan": "At Preset 4.4",
            "Blue": "At Preset 4.5", "Magenta": "At Preset 4.6",
            "White": "At Preset 4.7", "Orange": "At Preset 4.8",
            "Light Blue": "At Preset 4.9", "Purple": "At Preset 4.10",
            "Soft Dimmer": "At Effect 1", "Hard Dimmer": "At Effect 2",
            "Ramp Up": "At Effect 3", "Ramp Down": "At Effect 4",
            "Ballyhoo": "At Effect 5", "Strobe": "At Effect 6",
            "StopFX": "Stomp"
        }
    }

def validate_profile(data, source_name="profile"):
    if not isinstance(data, dict):
        raise ValueError(f"[{source_name}] JSON must contain an object {{...}} at its root.")

    missing = [k for k in REQUIRED_PROFILE_KEYS if k not in data]
    if missing:
        raise ValueError(f"[{source_name}] Missing keys in profile: {', '.join(missing)}")

    warnings = []
    for key in REQUIRED_PROFILE_KEYS:
        section = data[key]
        if not isinstance(section, dict):
            raise ValueError(f"[{source_name}] '{key}' must be an object {{name: value}}, found: {type(section).__name__}")
        if len(section) == 0:
            warnings.append(f"'{key}' is empty")

        seen_norm = {}
        for k, v in section.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise ValueError(f"[{source_name}] In '{key}', key/value are not strings: {k!r} -> {v!r}")
            if not v.strip():
                raise ValueError(f"[{source_name}] In '{key}', the value for '{k}' is empty.")
            nk = normalize_key(k)
            if nk in seen_norm:
                warnings.append(f"in '{key}' entries '{seen_norm[nk]}' and '{k}' normalize to the same name ('{nk}'): the latter overwrites the former.")
            seen_norm[nk] = k

    for w in warnings:
        print(f"[WARNING] Profile '{source_name}': {w}")

def load_profile(filepath):
    source_name = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"[{source_name}] Invalid JSON (syntax error): {e}") from e
    validate_profile(data, source_name=source_name)
    return data

def save_profile(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

