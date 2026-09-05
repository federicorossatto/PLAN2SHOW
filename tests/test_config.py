"""Configuration persistence tests."""

import json

import config


def isolate_config(monkeypatch, tmp_path):
    config_path = tmp_path / "plan2show_config.json"
    monkeypatch.setattr(config, "get_config_path", lambda: str(config_path))
    return config_path


def test_missing_config_returns_empty(monkeypatch, tmp_path):
    isolate_config(monkeypatch, tmp_path)
    assert config.load_app_config() == {}


def test_invalid_config_returns_empty(monkeypatch, tmp_path):
    path = isolate_config(monkeypatch, tmp_path)
    path.write_text("not json", encoding="utf-8")
    assert config.load_app_config() == {}


def test_update_preserves_existing_values(monkeypatch, tmp_path):
    path = isolate_config(monkeypatch, tmp_path)
    config.save_app_config({"workspace_dir": "/old"})
    config.update_app_config(active_profile="tour.json")
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved == {"workspace_dir": "/old", "active_profile": "tour.json"}


def test_active_profile_round_trip(monkeypatch, tmp_path):
    isolate_config(monkeypatch, tmp_path)
    config.save_active_profile_config("tour.json")
    assert config.load_active_profile_config() == "tour.json"


def test_workspace_helpers(monkeypatch, tmp_path):
    config.set_workspace_dir(str(tmp_path))
    assert config.tracks_dir() == str(tmp_path / "tracks")
    assert config.export_macros_dir() == str(tmp_path / "export_macros")
    assert config.stage_profiles_dir() == str(tmp_path / "stage_profiles")
