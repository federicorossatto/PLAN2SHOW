# PLAN2SHOW

**PLAN2SHOW** is an AI-assisted Python command-line tool created and directed by **Federico Rossatto**. It converts lighting timelines programmed in Excel into ready-to-paste command macros for **MA Lighting dot2 / dot2 onPC** workflows.

Each Excel row represents a cue. PLAN2SHOW reads the workbook, resolves human-friendly fixture names, groups, presets, effects and BPM changes through a reusable stage profile, applies an absolute timecode start offset, and exports a macro that can be pasted into the dot2 command line.

> **Project status:** pre-release development version. Always inspect and test generated commands in dot2/onPC before using them during rehearsals or live performances.

---

## Features

- Formatted `.xlsx` track editor with `TIMELINE` and `HELP` sheets
- One Excel row per lighting cue
- Relative cue timing with an absolute show start time
- Flexible start-time input such as `1`, `1:2`, `1:2:30` and `1:2:30:12`
- Support for 24, 25 and 30 FPS
- Frame-based timecode calculations and automatic rollovers
- Human-friendly fixture and group aliases through JSON stage profiles
- Custom Actions syntax for intensities, colors, presets, effects and Stomp
- Fixture ranges with `..`
- Fixture combinations with `+`
- BPM changes synchronized with cue timecode
- Cue Fade assignment
- Persistent workspace and active stage profile
- Duplicate cue detection and workbook validation
- Warning messages containing Cue Number and Excel row
- Protection against accidental output-file overwrites
- Modular project structure
- Automated test suite covering critical compiler behavior

---

## Requirements

- Python 3.10 or newer recommended
- `openpyxl`
- `pytest` to run the automated tests
- Microsoft Excel or LibreOffice Calc to edit track workbooks
- MA Lighting dot2 or dot2 onPC to test and use generated macros

Install dependencies with:

```bash
python3 -m pip install -r requirements.txt
```

On Linux distributions that manage Python packages through the operating system:

```bash
sudo apt update
sudo apt install python3-openpyxl python3-pytest
```

---

## Installation

Clone or download the repository, then open a terminal in the project directory:

```bash
git clone <REPOSITORY_URL>
cd PLAN2SHOW
```

Install the dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Start PLAN2SHOW:

```bash
python3 plan2show.py
```

---

## Project structure

```text
PLAN2SHOW/
├── plan2show.py
├── constants.py
├── config.py
├── profiles.py
├── excel_io.py
├── engine.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── PLAN2SHOW_User_Manual.tex
│   └── PLAN2SHOW_User_Manual.pdf
└── tests/
    ├── conftest.py
    ├── test_actions.py
    ├── test_config.py
    ├── test_excel_io.py
    ├── test_generate_show.py
    ├── test_imports.py
    ├── test_profiles.py
    ├── test_timecode.py
    └── test_validation.py
```

### Modules

- `plan2show.py`: command-line entry point and interactive menu
- `constants.py`: shared application constants
- `config.py`: persistent configuration and workspace paths
- `profiles.py`: stage-profile creation, validation, loading and saving
- `excel_io.py`: Excel template creation and workbook reading
- `engine.py`: Actions translation, validation, timecode calculation and macro generation
- `tests/`: automated tests for critical functionality

---

## Quick start

Run:

```bash
python3 plan2show.py
```

The main menu provides:

```text
1. Compile Show from Excel
2. Create Excel Track Template
3. Change Stage Profile
4. Exit
```

### First workflow

1. Start PLAN2SHOW.
2. Select a workspace directory.
3. Choose `2. Create Excel Track Template`.
4. Enter the track name.
5. Open the generated workbook from `tracks/`.
6. Program one cue per row in the `TIMELINE` sheet.
7. Save and close the workbook.
8. Choose `1. Compile Show from Excel`.
9. Enter the workbook name, target executor, track start time and frame rate.
10. Open the generated text file in `export_macros/`.
11. Copy only the command between the `START COPY` and `END COPY` markers.
12. Paste the command into the dot2 command line.
13. Test the complete cue list before live use.

---

## Workspace

At first launch, PLAN2SHOW asks where the workspace should be stored. The selected location is saved in `plan2show_config.json` next to `plan2show.py`.

```text
workspace/
├── tracks/
├── export_macros/
└── stage_profiles/
```

- `tracks/`: Excel lighting timelines
- `export_macros/`: generated macro text files
- `stage_profiles/`: reusable stage configuration profiles

The selected stage profile is also saved and restored at the next launch.

Example configuration:

```json
{
    "workspace_dir": "/home/user/PLAN2SHOW_WORKSPACE",
    "active_profile": "default_stage.json"
}
```

To select a different workspace, edit or delete `plan2show_config.json`, then restart PLAN2SHOW.

---

## Excel track workbook

Option `2` creates an `.xlsx` workbook containing two sheets.

### `TIMELINE`

The operational lighting timeline read by PLAN2SHOW.

### `HELP`

A quick guide to the Actions syntax, separators, fixture ranges and combinations.

The track title is stored in cell `B2` of `TIMELINE` and is used when naming the exported macro.

### Timeline columns

| Column | Required | Description |
|---|---:|---|
| `Cue Number` | Yes | Cue number stored on the selected executor |
| `Name` | No | Cue name; a blank value becomes `Cue N` |
| `Minutes` | Yes | Minutes relative to the beginning of the track |
| `Seconds` | Yes | Seconds relative to the track, from 0 to 59 |
| `Fade` | Yes | Cue Fade in seconds, zero or greater |
| `BPM` | No | Whole-number BPM change synchronized with the cue |
| `Actions` | Usually | Lighting and runtime commands written with PLAN2SHOW syntax |
| `Director Notes` | No | Production notes ignored by the compiler |

Rows containing neither `Actions` nor `BPM` are skipped because they contain nothing to execute.

Do not rename the `TIMELINE` sheet or its required columns.

---

## Actions syntax

The basic structure is:

```text
Subject: Action
```

Multiple actions for the same subject are separated by commas:

```text
Sides: Blue, 30%
```

Independent action blocks are separated by semicolons:

```text
Smoke: 25% ; Full Rig: Blackout ; Sides: Blue, 30%
```

### Separators

| Symbol | Meaning | Example |
|---|---|---|
| `:` | Separates a subject from its actions | `Sides: Blue` |
| `,` | Separates multiple actions | `Sides: Blue, 30%` |
| `;` | Separates independent blocks | `Sides: Blue ; Smoke: 25%` |
| `..` | Defines a fixture range | `White 1..White 4: Full` |
| `+` | Combines fixtures or subjects | `Blinder 1+Blinder 2: Strobe` |

### Complete examples

```text
Smoke: 25%
Full Rig: Blackout
Sides: Blue, 30%
White 1..White 4: Full
Blinder 1+Blinder 2: Strobe
Pars: StopFX
BPM Show: 120 BPM
```

### Example output

This action:

```text
Sides: Blue, 30%
```

can compile to:

```text
Fixture 13 Thru 20 At Preset 4.5 ; Fixture 13 Thru 20 At 30
```

This action:

```text
Pars: StopFX
```

compiles to:

```text
Stomp Fixture 9 Thru 12
```

BPM commands are placed in the timecode-triggered cue command so they run with the cue instead of running immediately when the macro is pasted.

---

## Stage profiles

Stage profiles are JSON files stored in:

```text
stage_profiles/
```

Each profile requires three sections:

```json
{
    "FIXTURE_PATCH": {},
    "MACRO_GROUPS": {},
    "COMMANDS_PRESETS": {}
}
```

### Fixture patch

```json
{
    "Smoke": "Fixture 21",
    "White 1": "Fixture 1",
    "White 2": "Fixture 2"
}
```

### Macro groups

```json
{
    "Sides": "Fixture 13 Thru 20",
    "Full Rig": "Fixture 1 Thru 6 + 9 Thru 20",
    "BPM Show": "SpecialMaster 3.1"
}
```

### Commands and presets

```json
{
    "Full": "At 100",
    "Blackout": "At 0",
    "Blue": "At Preset 4.5",
    "Strobe": "At Effect 6",
    "StopFX": "Stomp"
}
```

Profile names are compared without case, spaces and underscores. PLAN2SHOW validates the required sections, key and value types, empty values and normalized-name collisions.

Use menu option `3` to change the active profile. The selection is saved for future sessions.

---

## Start timecode and frame rate

Times in the workbook are relative to the beginning of the track. During compilation, PLAN2SHOW asks for the absolute show time at which the track begins.

Accepted formats:

```text
H
H:M
H:M:S
H:M:S:F
```

Examples:

```text
1         -> 01:00:00:00
1:2       -> 01:02:00:00
1:2:30    -> 01:02:30:00
1:2:30:12 -> 01:02:30:12
```

If the track begins at:

```text
01:30:00:00
```

and a cue is set to:

```text
Minutes: 4
Seconds: 0
```

PLAN2SHOW generates:

```text
01:34:00:00
```

Supported frame rates:

```text
24 FPS
25 FPS
30 FPS
```

The selected frame rate must match the show timecode source. Calculated timecodes beyond 24 hours are rejected instead of wrapping silently.

---

## Generated macro

Macros are written to:

```text
export_macros/
```

Example filename:

```text
Macro_Exec_1.4_Dancing_Queen.txt
```

The exported file contains metadata, instructions and copy markers:

```text
==================== START COPY ====================
ClearAll ; Fixture 21 At 25 ; ...
===================== END COPY =====================
```

Copy only the command between the markers.

For each compiled cue, PLAN2SHOW can generate:

- programmer values;
- cue number and name;
- Fade assignment;
- timecode trigger;
- absolute trigger time;
- BPM and other runtime commands.

If the output file already exists, PLAN2SHOW asks before overwriting it. If overwriting is declined, a numbered name such as `_2` or `_3` is selected.

---

## dot2 configuration and troubleshooting

### Timecode

The target executor must use the correct timecode source, and incoming MIDI or SMPTE timecode must be enabled in the console setup.

PLAN2SHOW generates:

```text
/trig=timecode
```

and:

```text
/trigtime=<calculated timecode>
```

Always verify the incoming timecode, frame rate and executor settings before a production.

### Fade values displayed as `=0`

If the macro contains correct Fade values but dot2 displays:

```text
=0
```

`Use Exec Time` is overriding the cue Fade.

Disable the setting for new executors:

```text
Setup > Global Settings > Default Executor Settings > Use Exec Time: Off
```

Existing executors may retain the previous setting. Disable `Use Exec Time` in the individual executor settings or recreate the executor after changing the default.

The `=` symbol is the key indication that the stored Fade is being overridden.

---

## Validation and warnings

PLAN2SHOW validates:

- `.xlsx` input format;
- presence of the `TIMELINE` sheet;
- all required columns;
- presence of cue rows;
- non-empty Cue Number values;
- duplicate cue numbers;
- valid Minutes and Seconds;
- Seconds from 0 to 59;
- non-negative Fade values;
- whole-number BPM values;
- valid start timecode;
- valid frame values for the selected FPS;
- final timecodes within the 24-hour range;
- stage-profile structure;
- executor input in `page.executor` format.

Unrecognized Actions are inserted as raw command text and produce a warning containing the cue and Excel row:

```text
[WARNING] [Cue 12, Excel row 17] Command 'Cold White' not recognized. Inserted as raw text.
```

Review every warning before using the exported macro.

---

## Automated tests

Run the complete test suite from the project root:

```bash
python3 -m pytest tests -q
```

Verbose output:

```bash
python3 -m pytest tests -v
```

Stop at the first failure:

```bash
python3 -m pytest tests -x -v
```

Run a specific module:

```bash
python3 -m pytest tests/test_timecode.py -q
```

The test suite covers:

- all module imports;
- configuration persistence;
- stage-profile validation;
- Excel creation and reading;
- Actions compilation;
- fixture ranges and combinations;
- Exec and SpecialMaster recognition;
- warning locations;
- cue validation;
- timecode parsing and arithmetic;
- all valid start hours;
- frame-rate boundaries;
- multi-hour offsets;
- macro generation;
- the 24-hour limit.

At the time of this README revision, the local suite reports:

```text
134 passed
```

Automated tests reduce regression risk but do not replace testing the exported macro in dot2/onPC.

---

## AI-assisted development

PLAN2SHOW is a **vibe-coded, AI-assisted software project** created and directed by **Federico Rossatto**.

AI tools were used to support:

- code generation;
- debugging;
- refactoring;
- documentation;
- automated-test generation;
- review of possible edge cases.

The project concept, lighting workflow, feature requirements, stage-profile design, operational decisions and final acceptance were defined by the project author.

AI-generated or AI-assisted code can contain mistakes. For this reason, PLAN2SHOW includes automated tests, input validation, explicit warnings and a requirement to inspect generated commands before live use.

The use of AI-assisted development does not mean the software is guaranteed to be correct or safe for every console, show file, fixture patch or production environment.

---

## Development workflow

When changing `engine.py`:

1. add or update the relevant tests;
2. run the complete suite;
3. generate a macro from a representative workbook;
4. compare it with a known-good output;
5. test it in dot2/onPC.

When changing `excel_io.py`:

1. create a new workbook with menu option `2`;
2. inspect both `TIMELINE` and `HELP`;
3. enter representative cues;
4. save and close the workbook;
5. compile it with option `1`;
6. run the complete suite.

Do not treat a successful import or a green test suite as the only acceptance criterion. The final macro must be reviewed in the target lighting environment.

---

## Known limitations

- Input workbooks must use `.xlsx`.
- The `TIMELINE` sheet and required column names must not be renamed.
- Relative cue timing currently uses Minutes and Seconds; no dedicated per-cue Frames column is provided yet.
- Supported frame rates are 24, 25 and 30 FPS.
- Unsupported or misspelled Actions may be inserted as raw console text.
- PLAN2SHOW generates command text but does not connect directly to the console.
- Fixture patching, presets, effects, timecode routing and console configuration remain the operator's responsibility.
- Automated tests cannot reproduce every real console or show-file state.

---

## Live-use checklist

Before using a generated macro:

- verify the active stage profile;
- confirm fixture IDs and group definitions;
- confirm preset and effect numbers;
- confirm the target executor;
- confirm the track start time;
- confirm the frame rate;
- review all compiler warnings;
- verify `Use Exec Time` settings;
- test every cue in dot2/onPC;
- keep a backup of the show file;
- do not paste an unreviewed macro into a live production.

---

## Documentation

The complete user manual is intended to be included in source and compiled form:

```text
docs/PLAN2SHOW_User_Manual.tex
docs/PLAN2SHOW_User_Manual.pdf
```

The README provides installation and operational essentials. The full manual provides detailed workflow, stage-profile configuration, timecode setup, examples and troubleshooting.

---

## License

PLAN2SHOW is released under the **MIT License**.

```text
Copyright (c) 2026 Federico Rossatto
```

See the [`LICENSE`](LICENSE) file for the complete license text.

The MIT License permits use, copying, modification, distribution, sublicensing and commercial use, provided that the copyright notice and license text are retained.

---

## Disclaimer

PLAN2SHOW is provided **as is**, without warranty of any kind.

Generated commands can affect real lighting equipment. Always inspect and test macros in dot2/onPC before using them during rehearsals or live performances. The operator remains responsible for console configuration, fixture patching, timecode routing and the safe operation of connected equipment.

PLAN2SHOW is an independent project and is not affiliated with or endorsed by MA Lighting International GmbH. Product names and trademarks belong to their respective owners.

---

## Author

**Federico Rossatto**

PLAN2SHOW was created to simplify the preparation of timecode-triggered lighting cue lists for MA Lighting dot2 workflows.
