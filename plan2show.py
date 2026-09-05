"""PLAN2SHOW command-line entry point."""

import os
import re

from config import (
    export_macros_dir, get_workspace_dir, load_active_profile_config,
    save_active_profile_config, set_workspace_dir, setup_workspace,
    stage_profiles_dir, tracks_dir,
)
from constants import APP_AUTHOR, APP_NAME, APP_VERSION, SUPPORTED_FRAME_RATES
from engine import generate_show
from excel_io import create_excel_template, read_excel_rows
from profiles import get_default_profile, load_profile


def print_banner():
    print("\n" + "=" * 50)
    print(f" {APP_NAME}  v{APP_VERSION}")
    print(f" by {APP_AUTHOR}")
    print("=" * 50)


def clear_screen():
    """Clear the terminal independently of the operating system."""
    os.system("cls" if os.name == "nt" else "clear")


def resolve_output_path(directory, base_filename):
    """Ask before overwriting and otherwise select a numbered filename."""
    candidate_path = os.path.join(directory, base_filename)
    if not os.path.exists(candidate_path):
        return candidate_path
    overwrite = input(
        f"[WARNING] '{base_filename}' already exists in export_macros. Overwrite? (y/n): "
    ).strip().lower()
    if overwrite == "y":
        return candidate_path
    name, extension = os.path.splitext(base_filename)
    counter = 2
    while True:
        alternative = os.path.join(directory, f"{name}_{counter}{extension}")
        if not os.path.exists(alternative):
            print(f"[OK] Keeping the existing file. Saving as '{os.path.basename(alternative)}'.")
            return alternative
        counter += 1


def load_initial_profile():
    """Load the persisted stage profile with a safe default fallback."""
    profile_name = load_active_profile_config() or "default_stage.json"
    profile_path = os.path.join(stage_profiles_dir(), profile_name)
    if not os.path.exists(profile_path):
        print(f"[WARNING] Saved profile '{profile_name}' was not found. Using default_stage.json.")
        profile_name = "default_stage.json"
        profile_path = os.path.join(stage_profiles_dir(), profile_name)
        save_active_profile_config(profile_name)
    return profile_name, load_profile(profile_path)


def compile_track(active_profile):
    """Collect compile options, compile one workbook, and write the macro."""
    file_name = input("Excel filename (in 'tracks') [e.g. Dancing_Queen.xlsx]: ").strip()
    if not file_name:
        print("[ERROR] Please enter an Excel filename.")
        return
    if not file_name.lower().endswith(".xlsx"):
        file_name += ".xlsx"
    input_path = os.path.join(tracks_dir(), file_name)
    if not os.path.exists(input_path):
        print(f"[ERROR] File '{input_path}' not found.")
        return

    target_exec = input("Target Executor [e.g. 1.2]: ").strip() or "1.2"
    if not re.fullmatch(r"\d+\.\d+", target_exec):
        print("[ERROR] Invalid executor. Use page.executor, for example 1.2.")
        return

    print("\nTrack Start Time")
    print("Format: Hours:Minutes:Seconds:Frames")
    print("Short formats: 1 -> 01:00:00:00 | 1:2 -> 01:02:00:00")
    start_timecode = input("Start [00:00:00:00]: ").strip() or "00:00:00:00"
    frame_rate_raw = input("Frame Rate [24/25/30, default 25]: ").strip() or "25"
    if not frame_rate_raw.isdigit() or int(frame_rate_raw) not in SUPPORTED_FRAME_RATES:
        print("[ERROR] Frame Rate must be 24, 25, or 30.")
        return
    frame_rate = int(frame_rate_raw)

    rows, track_title = read_excel_rows(input_path)
    final_code, song_name, total_cues, normalized_start = generate_show(
        rows, track_title, target_exec, start_timecode, frame_rate, active_profile
    )
    output_name = f"Macro_Exec_{target_exec}_{song_name}.txt"
    output_path = resolve_output_path(export_macros_dir(), output_name)
    header = (
        f"{APP_NAME} GENERATED MACRO\n{APP_NAME} by {APP_AUTHOR}\n"
        f"Track: {song_name}\nExecutor: {target_exec}\n"
        f"Start timecode: {normalized_start}\nFrame rate: {frame_rate} FPS\n\n"
        "INSTRUCTIONS\nCopy the command between the START and END markers, then paste it "
        "into the dot2 command line.\n\nIMPORTANT\n"
        "If cue fades are displayed as '=0' in dot2, disable 'Use Exec Time' "
        "in Setup > Global Settings > Default Executor Settings.\n\n"
        "==================== START COPY ====================\n"
    )
    footer = "\n===================== END COPY =====================\n"
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(header + final_code + footer)
    print(f"[OK] Macro saved to: {output_path} ({total_cues} cues compiled)")


def main():
    workspace = get_workspace_dir()
    set_workspace_dir(workspace)
    setup_workspace(get_default_profile())
    try:
        active_profile_name, active_profile = load_initial_profile()
    except ValueError as error:
        print(f"[ERROR] Unable to load the stage profile:\n  {error}")
        return

    while True:
        clear_screen()
        print_banner()
        print(f" Workspace: {workspace}")
        print(f" Active Stage Profile: [{active_profile_name}]")
        print("-" * 50)
        print("1. Compile Show from Excel")
        print("2. Create Excel Track Template")
        print("3. Change Stage Profile")
        print("4. Exit")
        choice = input("\nSelect an option (1-4): ").strip()
        try:
            if choice == "1":
                compile_track(active_profile)
            elif choice == "2":
                create_excel_template(tracks_dir())
            elif choice == "3":
                profiles = sorted(name for name in os.listdir(stage_profiles_dir()) if name.endswith(".json"))
                print("\nAvailable profiles:")
                for index, profile_name in enumerate(profiles, start=1):
                    marker = " (active)" if profile_name == active_profile_name else ""
                    print(f" {index}. {profile_name}{marker}")
                selection = input("\nSelect profile number: ").strip()
                if selection.isdigit() and 1 <= int(selection) <= len(profiles):
                    candidate_name = profiles[int(selection) - 1]
                    candidate = load_profile(os.path.join(stage_profiles_dir(), candidate_name))
                    active_profile_name, active_profile = candidate_name, candidate
                    save_active_profile_config(active_profile_name)
                    print(f"[OK] Profile changed to {active_profile_name} and saved.")
                else:
                    print("[ERROR] Invalid selection.")
            elif choice == "4":
                clear_screen()
                print("Exiting PLAN2SHOW. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")
        except ValueError as error:
            print(f"[ERROR] {error}")
        except Exception as error:
            print(f"[ERROR] Unexpected error: {error}")
        input("\nPress Enter to return to the main menu...")


if __name__ == "__main__":
    main()
