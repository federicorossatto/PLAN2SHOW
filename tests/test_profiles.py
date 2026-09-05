"""Stage profile tests."""

import json

import pytest

from profiles import get_default_profile, load_profile, save_profile, validate_profile


def test_default_profile_is_valid():
    validate_profile(get_default_profile(), "default")


def test_default_profile_has_required_sections(default_profile):
    assert set(default_profile) == {"FIXTURE_PATCH", "MACRO_GROUPS", "COMMANDS_PRESETS"}


@pytest.mark.parametrize("missing", ["FIXTURE_PATCH", "MACRO_GROUPS", "COMMANDS_PRESETS"])
def test_missing_section_is_rejected(default_profile, missing):
    del default_profile[missing]
    with pytest.raises(ValueError, match="Missing keys"):
        validate_profile(default_profile, "test")


def test_non_mapping_section_is_rejected(default_profile):
    default_profile["FIXTURE_PATCH"] = []
    with pytest.raises(ValueError):
        validate_profile(default_profile, "test")


def test_empty_value_is_rejected(default_profile):
    default_profile["FIXTURE_PATCH"]["Bad"] = ""
    with pytest.raises(ValueError):
        validate_profile(default_profile, "test")


def test_profile_round_trip(tmp_path, default_profile):
    path = tmp_path / "stage.json"
    save_profile(path, default_profile)
    assert load_profile(path) == default_profile


def test_invalid_json_is_rejected(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_profile(path)
