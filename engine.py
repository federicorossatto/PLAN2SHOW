"""Pure translation, validation, timecode, and macro generation engine."""

import re

from constants import SUPPORTED_FRAME_RATES

SIMPLE_FIXTURE_RE = re.compile(r'^Fixture\s+\d+$')
EXEC_TARGET_RE = re.compile(
    r"^(?:"
    r"SpecialMaster\s+\d+(?:\.\d+)?"
    r"|"
    r"Exec(?:utor)?\s+\d+(?:\.\d+)?"
    r")$",
    re.IGNORECASE
)
INVALID_FILENAME_CHARS_RE = re.compile(r'[\\/*?:"<>|]')

def normalize_key(text):
    return text.lower().replace(" ", "").replace("_", "")

def escape_dot2_string(text):
    """
    Make text safe to embed inside a double-quoted dot2 command
    (e.g. Store Exec ... "Cue Name" ...). dot2's command line does not
    support backslash-escaping inside quoted strings, so a literal '"'
    would terminate the string early and corrupt the macro. We replace
    it with a single quote, which keeps the macro syntactically valid
    without silently dropping the character.
    """
    return text.replace('"', "'")

def extract_fixture_number(fixture_string, pick="first"):
    numbers = re.findall(r'\d+', fixture_string)
    if not numbers:
        return fixture_string
    if pick == "min":
        return str(min(int(n) for n in numbers))
    if pick == "max":
        return str(max(int(n) for n in numbers))
    return numbers[0]

def compile_actions(
    excel_text,
    profile,
    cue_number=None,
    source_row=None
):
    patch_norm = {normalize_key(k): v for k, v in profile["FIXTURE_PATCH"].items()}
    macros_norm = {normalize_key(k): v for k, v in profile["MACRO_GROUPS"].items()}
    cmds_norm = {normalize_key(k): v for k, v in profile["COMMANDS_PRESETS"].items()}

    def resolve_target(token):
        key = normalize_key(token)
        if key in macros_norm:
            return macros_norm[key]
        return patch_norm.get(key, token.strip())

    def translate_subject(text):
        if ".." in text:
            start_raw, end_raw = text.split("..", 1)
            start_resolved = resolve_target(start_raw)
            end_resolved = resolve_target(end_raw)

            if SIMPLE_FIXTURE_RE.match(start_resolved.strip()):
                start_str = start_resolved.strip()
            else:
                start_str = f"Fixture {extract_fixture_number(start_resolved, pick='min')}"

            end_num = extract_fixture_number(end_resolved, pick='max')
            return f"{start_str} Thru {end_num}"

        if "+" in text:
            parts = text.split("+")
            resolved = [resolve_target(p) for p in parts]
            out = [resolved[0].strip()]
            base_is_simple = bool(SIMPLE_FIXTURE_RE.match(resolved[0].strip()))
            for p in resolved[1:]:
                p_stripped = p.strip()
                if base_is_simple and SIMPLE_FIXTURE_RE.match(p_stripped):
                    out.append(extract_fixture_number(p_stripped))
                else:
                    out.append(p_stripped)
            return " + ".join(out)

        return resolve_target(text)

    lights_cmds = []
    exec_cmds = []
    blocks = [b for b in excel_text.split(";") if ":" in b]
    
    for block in blocks:
        subject, actions_str = block.split(":", 1)
        target = translate_subject(subject)
        
        is_exec = bool(
            EXEC_TARGET_RE.fullmatch(target.strip())
        )              
        
        for action in [a.strip() for a in actions_str.split(",")]:
            action_norm = normalize_key(action)
            action_clean = action_norm.replace('%', '').replace('bpm', '')
            
            if action_clean.isdigit(): 
                final_cmd = f"{target} At {action_clean}"
            elif action_norm == "stopfx": 
                final_cmd = f"Stomp {target}"
            elif action_norm in cmds_norm: 
                final_cmd = f"{target} {cmds_norm[action_norm]}"
            else: 
                final_cmd = f"{target} {action}"
                if not is_exec:
                    location_parts = []

                    if cue_number:
                        location_parts.append(f"Cue {cue_number}")

                    if source_row:
                        location_parts.append(f"Excel row {source_row}")

                    location = (
                        f" [{', '.join(location_parts)}]"
                        if location_parts
                        else ""
                    )

                    print(
                        f"[WARNING]{location} Command '{action}' "
                        "not recognized. Inserted as raw text."
                    )
            
            if is_exec:
                exec_cmds.append(final_cmd)
            else:
                lights_cmds.append(final_cmd)
                
    return " ; ".join(lights_cmds), " ; ".join(exec_cmds)

def validate_rows(rows):
    """
    Validate Cue Number/Minutes/Seconds/Fade/BPM across the workbook before
    compiling anything. Timecode fields feed directly into the dot2
    /trigtime= syntax, so a bad value here can silently produce a cue
    that never fires (or fires at the wrong moment) instead of an
    obvious error. We collect every problem across all Excel rows and raise
    once, so the user can fix the whole sheet in one pass instead of
    re-running the tool row by row.
    """
    errors = []
    seen_cues = {}

    for i, row in enumerate(rows):
        cue_num = row.get("Cue Number", "").strip()
        label = f"Cue '{cue_num}'" if cue_num else f"row {i + 1} (data row, not counting headers)"

        if not cue_num:
            errors.append(f"{label}: 'Cue Number' is empty.")
        elif cue_num in seen_cues:
            errors.append(
                f"{label}: duplicate cue number; first used on Excel row "
                f"{seen_cues[cue_num]}."
            )
        else:
            seen_cues[cue_num] = row.get("_source_row", str(i + 1))

        minutes_raw = row.get("Minutes", "0").strip() or "0"

        if not minutes_raw.isdigit():
            errors.append(
                f"{label}: Minutes '{minutes_raw}' is not a whole number."
            )
        elif int(minutes_raw) < 0:
            errors.append(
                f"{label}: Minutes '{minutes_raw}' cannot be negative."
            )

        seconds_raw = row.get("Seconds", "0").strip() or "0"
        if not seconds_raw.isdigit():
            errors.append(f"{label}: Seconds '{seconds_raw}' is not a whole number.")
        elif int(seconds_raw) > 59:
            errors.append(f"{label}: Seconds '{seconds_raw}' is greater than 59.")

        fade_raw = row.get("Fade", "0").strip() or "0"
        try:
            if float(fade_raw) < 0:
                errors.append(f"{label}: Fade '{fade_raw}' cannot be negative.")
        except ValueError:
            errors.append(f"{label}: Fade '{fade_raw}' is not a valid number.")

        bpm_raw = row.get("BPM", "").strip()
        if bpm_raw and not bpm_raw.isdigit():
            errors.append(f"{label}: BPM '{bpm_raw}' is not a whole number (leave the cell empty if not needed).")

    if errors:
        details = "\n  - ".join(errors)
        raise ValueError(
            f"Found {len(errors)} problem(s) in the Excel track before compiling. Nothing was written.\n  - {details}"
        )

def parse_start_timecode(value, fps):
    """
    Parse a flexible absolute show start time.

    Accepted formats:
        H
        H:M
        H:M:S
        H:M:S:F

    Missing components default to zero. For example, "1:2" becomes
    "01:02:00:00".

    Returns:
        tuple: (total_frames, normalized_timecode)
    """
    raw_value = value.strip()

    if not raw_value:
        raw_value = "0"

    parts = [part.strip() for part in raw_value.split(":")]

    if len(parts) > 4:
        raise ValueError(
            "Invalid start timecode. Use H, H:M, H:M:S, or H:M:S:F."
        )

    if any(not part.isdigit() for part in parts):
        raise ValueError(
            "Invalid start timecode. Use numbers separated by colons, "
            "for example 1:2:30:12."
        )

    while len(parts) < 4:
        parts.append("0")

    hours, minutes, seconds, frames = map(int, parts)

    if hours > 23:
        raise ValueError(
            f"Invalid start timecode: hours must be between 0 and 23, "
            f"found {hours}."
        )

    if minutes > 59:
        raise ValueError(
            f"Invalid start timecode: minutes must be between 0 and 59, "
            f"found {minutes}."
        )

    if seconds > 59:
        raise ValueError(
            f"Invalid start timecode: seconds must be between 0 and 59, "
            f"found {seconds}."
        )

    if frames >= fps:
        raise ValueError(
            f"Invalid start timecode: frames must be between 0 and "
            f"{fps - 1} at {fps} FPS, found {frames}."
        )

    total_frames = (
        hours * 3600 * fps
        + minutes * 60 * fps
        + seconds * fps
        + frames
    )

    normalized_timecode = (
        f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"
    )

    return total_frames, normalized_timecode

def add_relative_timecode(start_frames, minutes, seconds, fps):
    """
    Add a track-relative MM:SS cue time to an absolute show start time.

    Returns the absolute timecode components as hours, minutes,
    seconds, and frames.
    """
    relative_seconds = int(minutes) * 60 + int(seconds)
    absolute_frames = start_frames + relative_seconds * fps

    hours, remainder = divmod(absolute_frames, 3600 * fps)
    output_minutes, remainder = divmod(remainder, 60 * fps)
    output_seconds, frames = divmod(remainder, fps)

    return hours, output_minutes, output_seconds, frames

def format_dot2_timecode(hours, minutes, seconds, frames):
    """
    Format an absolute timecode using dot2 command-line components.
    """
    return f"{hours}h{minutes}m{seconds}s{frames}f"

def sanitize_component(raw_text, fallback="Untitled"):
    """
    Strip characters that are invalid in filenames (including the double
    quote, which would otherwise also break out of quoted dot2 strings if
    reused verbatim). Used both for output filenames and for the song name
    embedded in the compiled show.
    """
    text = (raw_text or "").strip()
    if not text:
        text = fallback
    text = INVALID_FILENAME_CHARS_RE.sub("_", text)
    text = text.replace(" ", "_")
    return text

def generate_show(
    rows,
    track_title,
    target_exec,
    start_timecode,
    frame_rate,
    profile
):
    macro = ["ClearAll"]
    total_cues = 0

    start_frames, normalized_start_timecode = parse_start_timecode(
    start_timecode,
    frame_rate
)

    validate_rows(rows)

    # Prefer the track title stored in cell B2 of the TIMELINE sheet.
    # Fall back to the first cue name only when the track title is empty.
    song_name = sanitize_component(track_title, fallback="Untitled") if track_title else None

    for i, row in enumerate(rows):
        if song_name is None and i == 0:
            song_name = sanitize_component(row.get("Name", "Untitled"), fallback="Untitled")

        cue_num = row.get("Cue Number", str(i + 1)).strip()
        minutes = row.get("Minutes", "0").strip() or "0"
        seconds = row.get("Seconds", "0").strip() or "0"
        fade = row.get("Fade", "0").strip() or "0"
        bpm = row.get("BPM", "").strip()
        raw_cue_name = row.get("Name", "").strip() or f"Cue {cue_num}"
        cue_name = escape_dot2_string(raw_cue_name)
        actions = row.get("Actions", "").strip()

        # BPM must fire at the same timecode-triggered moment as the rest of the
        # cue, not immediately when the macro is run. Build it now and fold it
        # into the exec-side /cmd= below instead of appending it to the flat
        # macro list.
        bpm_cmd = f"SpecialMaster 3.1 At {bpm}" if bpm.isdigit() else None

        # A row can carry only a BPM change with no light Actions (e.g. a tempo
        # bump mid-song); it still needs its own timecode trigger, so we only
        # skip the row entirely when there is truly nothing to do.
        if not actions and not bpm_cmd:
            continue

        hours, absolute_minutes, absolute_seconds, frames = (
            add_relative_timecode(
                start_frames=start_frames,
                minutes=minutes,
                seconds=seconds,
                fps=frame_rate
            )
        )
        if hours > 23:
            source_row = row.get("_source_row", "?")

            raise ValueError(
                f"Cue '{cue_num}' on Excel row {source_row} exceeds "
                "the 24-hour timecode range after applying the track "
                f"start offset. Calculated hour: {hours}."
            )

        formatted_timecode = format_dot2_timecode(
            hours=hours,
            minutes=absolute_minutes,
            seconds=absolute_seconds,
            frames=frames
        )

        lights_cmds, exec_cmds = (
            compile_actions(
                actions,
                profile,
                cue_number=cue_num,
                source_row=row.get("_source_row")
            )
            if actions
            else ("", "")
        )

        if lights_cmds:
            macro.append(lights_cmds)

        macro.append(
        f'Store Exec {target_exec} Cue {cue_num} "{cue_name}"'
        )

        macro.append(
    f'Assign Fade {fade} Cue {cue_num} Executor {target_exec}'
)
            
        total_exec_cmds = []
        if total_cues == 0:
            page = target_exec.split('.')[0] if '.' in target_exec else "1"
            total_exec_cmds.append(f"Exec {target_exec} At 100")
            total_exec_cmds.append(f"Exec {page}.1 Thru {page}.100 - Exec {target_exec} At 0")

        if bpm_cmd:
            total_exec_cmds.append(bpm_cmd)

        if exec_cmds:
            total_exec_cmds.append(exec_cmds)

        extra_cmd = ""
        if total_exec_cmds:
            extra_cmd = f' /cmd="{" ; ".join(total_exec_cmds)}"'

        macro.append(f'Assign Exec {target_exec} Cue {cue_num} /trig=timecode /trigtime={formatted_timecode}{extra_cmd}')
        macro.append("ClearAll")
        total_cues += 1

    if song_name is None:
        song_name = "Untitled"

    return (
    " ; ".join(macro),
    song_name,
    total_cues,
    normalized_start_timecode
)

