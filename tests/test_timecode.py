"""Timecode parsing and arithmetic tests."""

import pytest

from engine import add_relative_timecode, format_dot2_timecode, parse_start_timecode


@pytest.mark.parametrize(
    ("raw", "fps", "normalized"),
    [
        ("0", 25, "00:00:00:00"),
        ("1", 25, "01:00:00:00"),
        ("1:2", 25, "01:02:00:00"),
        ("1:2:3", 25, "01:02:03:00"),
        ("1:2:3:4", 25, "01:02:03:04"),
        (" 1 : 2 : 3 : 4 ", 25, "01:02:03:04"),
        ("23:59:59:23", 24, "23:59:59:23"),
        ("23:59:59:24", 25, "23:59:59:24"),
        ("23:59:59:29", 30, "23:59:59:29"),
    ],
)
def test_parse_valid_timecodes(raw, fps, normalized):
    _, result = parse_start_timecode(raw, fps)
    assert result == normalized


@pytest.mark.parametrize("hour", range(24))
def test_every_valid_start_hour(hour):
    _, normalized = parse_start_timecode(str(hour), 25)
    assert normalized == f"{hour:02d}:00:00:00"


@pytest.mark.parametrize("fps", [24, 25, 30])
def test_last_valid_frame_for_each_rate(fps):
    _, normalized = parse_start_timecode(f"0:0:0:{fps - 1}", fps)
    assert normalized == f"00:00:00:{fps - 1:02d}"


@pytest.mark.parametrize(
    ("raw", "fps"),
    [
        ("hello", 25),
        ("1::2", 25),
        ("1:2:3:4:5", 25),
        ("24", 25),
        ("1:60", 25),
        ("1:2:60", 25),
        ("1:2:3:25", 25),
        ("1:2:3:-1", 25),
        ("1.5", 25),
    ],
)
def test_parse_rejects_invalid_timecodes(raw, fps):
    with pytest.raises(ValueError):
        parse_start_timecode(raw, fps)


@pytest.mark.parametrize(
    ("start", "minutes", "seconds", "fps", "expected"),
    [
        ("0", "0", "0", 25, (0, 0, 0, 0)),
        ("1:30", "4", "0", 25, (1, 34, 0, 0)),
        ("1:59:55:20", "0", "10", 25, (2, 0, 5, 20)),
        ("22:00", "60", "0", 25, (23, 0, 0, 0)),
        ("0:00:00:23", "0", "1", 24, (0, 0, 1, 23)),
        ("0:00:00:29", "0", "1", 30, (0, 0, 1, 29)),
    ],
)
def test_relative_time_addition(start, minutes, seconds, fps, expected):
    start_frames, _ = parse_start_timecode(start, fps)
    assert add_relative_timecode(start_frames, minutes, seconds, fps) == expected


def test_dot2_timecode_format():
    assert format_dot2_timecode(12, 3, 4, 5) == "12h3m4s5f"
