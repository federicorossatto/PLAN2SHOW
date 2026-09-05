"""Application configuration and workspace paths."""

import json
import os
from constants import APP_NAME

CONFIG_FILENAME = "plan2show_config.json"
WORKSPACE_DIR = None

def get_script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.path.abspath(os.getcwd())

def get_config_path():
    return os.path.join(get_script_dir(), CONFIG_FILENAME)

def load_app_config():
    """
    Load the application configuration.

    Returns an empty dictionary if the configuration file does not exist,
    is not readable, or does not contain a valid JSON object.
    """
    config_path = get_config_path()

    if not os.path.exists(config_path):
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

    if not isinstance(config, dict):
        return {}

    return config

def save_app_config(config):
    """
    Save the complete application configuration.
    """
    with open(get_config_path(), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def update_app_config(**changes):
    """
    Update selected configuration values without deleting existing ones.
    """
    config = load_app_config()
    config.update(changes)
    save_app_config(config)

def load_workspace_config():
    config = load_app_config()

    workspace = config.get("workspace_dir")
    if not workspace:
        return None

    try:
        os.makedirs(workspace, exist_ok=True)
    except OSError:
        return None

    return workspace

def save_workspace_config(workspace_dir):
    update_app_config(workspace_dir=workspace_dir)

def load_active_profile_config():
    """
    Return the last selected stage profile filename.

    The profile path is not stored because stage profiles always live
    inside the current workspace.
    """
    config = load_app_config()
    profile_name = config.get("active_profile")

    if not isinstance(profile_name, str):
        return None

    profile_name = profile_name.strip()

    if not profile_name:
        return None

    return profile_name

def save_active_profile_config(profile_name):
    """
    Save the selected stage profile filename.
    """
    update_app_config(active_profile=profile_name)

def ask_workspace_dir():
    default_dir = get_script_dir()
    print("\n--- Initial Setup ---")
    print(f"{APP_NAME} needs to know where to save Excel tracks, stage profiles, and exported macros.")
    print(f"Default (program folder): {default_dir}")
    raw = input(
        "Press Enter to use default, or type a custom path "
        "(e.g. 'Documents/Plan2Show' or an absolute path): "
    ).strip()

    if not raw:
        chosen = default_dir
    else:
        expanded = os.path.expanduser(raw)
        if not os.path.isabs(expanded):
            expanded = os.path.join(os.path.expanduser("~"), expanded)
        chosen = os.path.abspath(expanded)
        os.makedirs(chosen, exist_ok=True)

    save_workspace_config(chosen)
    print(f"[OK] Workspace set to: {chosen}")
    print(f"     (To change this later, edit or delete '{CONFIG_FILENAME}' next to the script.)")
    return chosen

def get_workspace_dir():
    workspace = load_workspace_config()
    if workspace is None:
        workspace = ask_workspace_dir()
    return workspace

def tracks_dir():
    """Return the directory containing PLAN2SHOW Excel track files."""
    return os.path.join(WORKSPACE_DIR, "tracks")

def export_macros_dir():
    return os.path.join(WORKSPACE_DIR, "export_macros")

def stage_profiles_dir():
    return os.path.join(WORKSPACE_DIR, "stage_profiles")

def set_workspace_dir(workspace_dir):
    """Set the active workspace used by directory helper functions."""
    global WORKSPACE_DIR
    WORKSPACE_DIR = workspace_dir


def setup_workspace(default_profile):
    """Create workspace folders and save the default profile if missing."""
    for folder in [tracks_dir(), export_macros_dir(), stage_profiles_dir()]:
        os.makedirs(folder, exist_ok=True)

    default_profile_path = os.path.join(stage_profiles_dir(), "default_stage.json")
    if not os.path.exists(default_profile_path):
        with open(default_profile_path, "w", encoding="utf-8") as file:
            json.dump(default_profile, file, indent=4)
        print(f"[OK] Default stage profile created at: {default_profile_path}")
