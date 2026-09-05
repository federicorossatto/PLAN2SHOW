"""Macro generation integration tests without Excel I/O."""

import pytest

from engine import generate_show


def make_row(cue="1", name="Intro", minutes="0", seconds="0", fade="0", bpm="", actions="Smoke: 25%", row="6"):
    return {
        "Cue Number": cue,
        "Name": name,
        "Minutes": minutes,
        "Seconds": seconds,
        "Fade": fade,
        "BPM": bpm,
        "Actions": actions,
        "Director Notes": "",
        "_source_row": row,
    }


def test_complete_macro_generation(default_profile):
    rows = [
        make_row(bpm="120"),
        make_row(cue="2", name="Verse", seconds="5", fade="2", actions="Sides: Blue, 30%", row="7"),
    ]
    macro, song, count, start = generate_show(rows, "Dancing Queen", "1.4", "1:30", 25, default_profile)
    assert song == "Dancing_Queen"
    assert count == 2
    assert start == "01:30:00:00"
    assert 'Store Exec 1.4 Cue 1 "Intro"' in macro
    assert 'Assign Fade 2 Cue 2 Executor 1.4' in macro
    assert '/trigtime=1h30m5s0f' in macro
    assert 'SpecialMaster 3.1 At 120' in macro


def test_first_compiled_cue_gets_initialization(default_profile):
    rows = [make_row(cue="10")]
    macro, _, _, _ = generate_show(rows, "Track", "2.7", "0", 25, default_profile)
    assert 'Exec 2.7 At 100' in macro
    assert 'Exec 2.1 Thru 2.100 - Exec 2.7 At 0' in macro


def test_blank_name_gets_fallback(default_profile):
    rows = [make_row(name="")]
    macro, _, _, _ = generate_show(rows, "Track", "1.2", "0", 25, default_profile)
    assert 'Cue 1 "Cue 1"' in macro


def test_quote_in_name_is_safe(default_profile):
    rows = [make_row(name='Intro "Live"')]
    macro, _, _, _ = generate_show(rows, "Track", "1.2", "0", 25, default_profile)
    assert '"Intro \'Live\'"' in macro


def test_bpm_only_row_is_compiled(default_profile):
    rows = [make_row(actions="", bpm="130")]
    macro, _, count, _ = generate_show(rows, "Track", "1.2", "0", 25, default_profile)
    assert count == 1
    assert "SpecialMaster 3.1 At 130" in macro


def test_empty_row_action_is_skipped(default_profile):
    rows = [make_row(actions="", bpm="")]
    _, _, count, _ = generate_show(rows, "Track", "1.2", "0", 25, default_profile)
    assert count == 0


def test_timecode_beyond_24_hours_is_rejected(default_profile):
    rows = [make_row(minutes="10")]
    with pytest.raises(ValueError, match="24-hour timecode range"):
        generate_show(rows, "Track", "1.2", "23:55", 25, default_profile)


@pytest.mark.parametrize("hour", range(0, 23))
def test_macro_can_start_across_many_hours(hour, default_profile):
    rows = [make_row(seconds="5")]
    macro, _, count, normalized = generate_show(rows, "Track", "1.2", str(hour), 25, default_profile)
    assert count == 1
    assert normalized == f"{hour:02d}:00:00:00"
    assert f"/trigtime={hour}h0m5s0f" in macro
