# PLAN2SHOW

**PLAN2SHOW** is a Python command-line tool created and directed by **Federico Rossatto**. It reads a lighting cue list from an Excel worksheet and converts it into ready-to-paste command macros for **MA Lighting dot2 / dot2 onPC**.

Development of PLAN2SHOW was AI-assisted (see [AI-assisted development](#ai-assisted-development)); the application itself does not include any AI component. It is a deterministic compiler: identical input consistently produces identical output.

> **Project status:** pre-release, under active development. Generated commands must always be inspected and tested in dot2/onPC before use in rehearsal or during a live performance.

---

## Purpose

Running a timecode-driven show typically requires calculating the exact absolute time of each lighting change and entering the corresponding commands into the console individually. This process is time-consuming and error-prone.

PLAN2SHOW allows the cue list to be prepared in a standard Excel worksheet instead: one row per cue, specifying when it occurs (relative to the start of the track, e.g. "4 minutes in") and what it does, expressed in plain terms (e.g. `Sides: Blue, 30%`). PLAN2SHOW reads the worksheet, calculates the absolute timecode for each cue, translates the plain-text actions into dot2 commands using a configuration file referred to as a **stage profile** (which maps fixture and group names to the corresponding dot2 references), and produces a single block of text to be pasted into the dot2 command line.

In summary: the show is described in Excel, and PLAN2SHOW converts it into the corresponding dot2 commands with the correct timecodes, removing the need for manual calculation and entry.

---

## Features

- **Cue list authored in Excel.** One row per cue, specifying timing and the corresponding action.
- **Automatic timecode calculation.** Cue times are entered relative to the start of the track; PLAN2SHOW calculates the corresponding absolute, frame-accurate timecode, including correct rollovers, for 24, 25 or 30 FPS shows.
- **Plain-text action syntax.** Actions such as `Sides: Blue, 30%` or `Pars: StopFX` are translated into dot2 commands via the stage profile, which maps fixture, group and command names.
- **Fixture ranges and combinations**, e.g. `White 1..White 4` or `Blinder 1+Blinder 2`.
- **BPM changes** synchronized with the cue's timecode.
- **Per-cue fade time**, written automatically into the cue command.
- **Persistent configuration**: workspace directory and active stage profile are retained between sessions.
- **Early error detection**: duplicate cue numbers, missing columns, out-of-range values and similar issues are reported before export, together with the cue number and Excel row.
- Supported by an automated test suite that verifies core compiler behavior on every change (see [Automated tests](#automated-tests)).

---

## Requirements

- Python 3.10 or newer recommended
- `openpyxl`
- `pytest` to run the automated tests
- Microsoft Excel, LibreOffice Calc or OnlyOffice to edit track workbooks
- MA Lighting dot2 or dot2 onPC to test and use generated macros

Install dependencies with:

```bash
python3 -m pip install -r requirements.txt
```

On Linux, `openpyxl` and `pytest` are typically also available through the distribution's package manager, as an alternative to pip.

---

## Installation

Clone or download the repository, then open a terminal in the project directory:

```bash
git clone https://github.com/federicorossatto/PLAN2SHOW.git
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

Current repository contents:

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

At first launch, PLAN2SHOW also creates a local, machine-specific `plan2show_config.json` next to `plan2show.py` and a `workspace/` (see [Workspace](#workspace)). These are runtime data, not part of the repository, and are excluded via `.gitignore`.

Planned but not yet included: `docs/` with a LaTeX-sourced user manual. See [Documentation](#documentation).

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

*Note for first-time use: option 2 should be used to create the Excel template before option 1 is used to compile it.*

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

At first launch, PLAN2SHOW asks where the workspace should be stored. The selected location is saved in `plan2show_config.json` next to `plan2show.py`. This file is local to your machine and is not tracked by git.

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

The operational lighting cue list read by PLAN2SHOW.

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
| `Fade` | Yes | Cue transition time (fade), in seconds, zero or greater |
| `BPM` | No | Whole-number BPM change synchronized with the cue |
| `Actions` | Usually | Lighting and runtime commands written with PLAN2SHOW syntax |
| `Director Notes` | No | Production notes ignored by the compiler |

Rows containing neither `Actions` nor `BPM` are skipped because they contain nothing to execute.

Do not rename the `TIMELINE` sheet or its required columns.

> **BPM column vs. `BPM Show` action:** if a row sets a value in the `BPM` column **and** also includes a `BPM Show: X BPM` action in the same row, both commands are compiled into the same cue and applied in sequence — the Actions-column value is applied last and silently overrides the column value. Use only one of the two per row to avoid ambiguity.

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

## Scope: what PLAN2SHOW does and does not do

This section defines the boundaries of what PLAN2SHOW is able to interpret.

**What it does:** PLAN2SHOW translates the contents of the `Actions` column into dot2 command text, based on the mapping defined in the active stage profile (fixture patch, groups, and named commands/presets). It also calculates the correct absolute timecode and fade value for each cue, and assembles the result into a single macro for pasting into dot2.

**What it does not do:** PLAN2SHOW has no knowledge of lighting design. It does not evaluate colour, position or effect parameters; it reproduces whatever command text has been defined in the stage profile for a given name. In particular:

- **Moving heads (pan/tilt, positions):** PLAN2SHOW does not calculate or assign a position. To trigger a moving-head position from a cue, the position must first be stored as a Preset in dot2, and the corresponding stage-profile command must reference that preset (e.g. `"Center Stage": "At Preset 7.3"`). The Actions syntax triggers the preset; PLAN2SHOW does not compute pan/tilt values.
- **Colour, intensity, effects:** the same principle applies — PLAN2SHOW triggers the preset, effect or level number configured in the stage profile. It does not process colour mixing, DMX values or effect parameters.
- **Anything absent from the active stage profile:** a fixture, group or command not defined in the stage profile cannot be resolved. Unrecognized actions are inserted as raw text with a warning, but are not validated against the actual dot2 show file.
- **Console communication:** PLAN2SHOW does not connect to dot2 directly; the generated macro must be copied and pasted manually.

See also [Known limitations](#known-limitations) for additional constraints.

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

PLAN2SHOW does **not** currently detect or warn about a row that sets both the `BPM` column and a `BPM Show` action at once (see [Timeline columns](#timeline-columns)).

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

PLAN2SHOW itself contains no AI component; it is a deterministic compiler. The term "AI-assisted" refers to how the software was developed, not to its runtime behavior.

Federico Rossatto defined the project concept, the lighting workflow, the Excel/Actions syntax, the stage-profile format, and all operational decisions, and used AI tools to assist with writing, debugging, refactoring, documentation and test generation.

AI-assisted code can still contain errors. For this reason, PLAN2SHOW includes automated tests, input validation and explicit warnings, and this documentation repeatedly recommends verifying generated commands before live use. None of these measures guarantee correctness or safety for every console, show file, fixture patch or production environment.

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

For what the Actions syntax can and cannot control (e.g. moving heads), see [Scope: what PLAN2SHOW does and does not do](#scope-what-plan2show-does-and-does-not-do) above.

- Input workbooks must use `.xlsx`.
- The `TIMELINE` sheet and required column names must not be renamed.
- Relative cue timing currently uses Minutes and Seconds; no dedicated per-cue Frames column is provided yet.
- Supported frame rates are 24, 25 and 30 FPS.
- Unsupported or misspelled Actions may be inserted as raw console text.
- If a row combines a `BPM` column value with a `BPM Show` action, the Actions value silently overrides the column value; PLAN2SHOW does not warn about this (see [Timeline columns](#timeline-columns)).
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

This README is currently the complete and only documentation for PLAN2SHOW: installation, workflow, Actions syntax, stage profiles, timecode setup, troubleshooting and known limitations are all covered above.

A dedicated user manual (LaTeX source and compiled PDF, under `docs/`) is planned for a future release and is not yet part of the repository.

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
