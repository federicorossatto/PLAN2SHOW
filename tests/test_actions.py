"""Action parser and profile translation tests."""

import pytest

from engine import EXEC_TARGET_RE, compile_actions, escape_dot2_string


@pytest.mark.parametrize(
    ("actions", "expected_lights", "expected_runtime"),
    [
        ("Smoke: 25%", "Fixture 21 At 25", ""),
        ("Sides: Blue, 30%", "Fixture 13 Thru 20 At Preset 4.5 ; Fixture 13 Thru 20 At 30", ""),
        ("Full Rig: Blackout", "Fixture 1 Thru 6 + 9 Thru 20 At 0", ""),
        ("White 1..White 4: Full", "Fixture 1 Thru 4 At 100", ""),
        ("Blinder 1+Blinder 2: Strobe", "Fixture 5 + 6 At Effect 6", ""),
        ("Pars: StopFX", "Stomp Fixture 9 Thru 12", ""),
        ("BPM Show: 120 BPM", "", "SpecialMaster 3.1 At 120"),
        ("Sides: blue, 30%", "Fixture 13 Thru 20 At Preset 4.5 ; Fixture 13 Thru 20 At 30", ""),
        ("Sides: Light Blue", "Fixture 13 Thru 20 At Preset 4.9", ""),
    ],
)
def test_compile_actions(actions, expected_lights, expected_runtime, default_profile):
    lights, runtime = compile_actions(actions, default_profile)
    assert lights == expected_lights
    assert runtime == expected_runtime


def test_multiple_blocks(default_profile):
    lights, runtime = compile_actions(
        "Smoke: 25% ; Sides: Blue, 30% ; BPM Show: 125 BPM",
        default_profile,
    )
    assert lights == (
        "Fixture 21 At 25 ; Fixture 13 Thru 20 At Preset 4.5 ; "
        "Fixture 13 Thru 20 At 30"
    )
    assert runtime == "SpecialMaster 3.1 At 125"


@pytest.mark.parametrize("target", ["Exec 1.4", "Executor 1.4", "SpecialMaster 3.1"])
def test_exec_target_regex_accepts_runtime_targets(target):
    assert EXEC_TARGET_RE.fullmatch(target)


@pytest.mark.parametrize("target", ["Executive Wash", "Executor Wash", "MyExecFixture", "Fixture 1"])
def test_exec_target_regex_rejects_fixture_like_names(target):
    assert not EXEC_TARGET_RE.fullmatch(target)


def test_warning_contains_cue_and_excel_row(default_profile, capsys):
    compile_actions(
        "Sides: UnknownCommand",
        default_profile,
        cue_number="12",
        source_row="17",
    )
    output = capsys.readouterr().out
    assert "Cue 12" in output
    assert "Excel row 17" in output
    assert "UnknownCommand" in output


def test_double_quotes_are_made_safe():
    assert escape_dot2_string('Intro "Live"') == "Intro 'Live'"
