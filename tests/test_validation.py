"""Validation tests for compiler rows."""

import pytest

from engine import validate_rows


def valid_row(**changes):
    row = {
        "Cue Number": "1",
        "Name": "Test",
        "Minutes": "0",
        "Seconds": "0",
        "Fade": "0",
        "BPM": "120",
        "Actions": "Smoke: 25%",
        "Director Notes": "",
        "_source_row": "6",
    }
    row.update(changes)
    return row


def test_valid_rows_pass():
    validate_rows([valid_row()])


def test_minutes_may_exceed_59():
    validate_rows([valid_row(Minutes="180")])


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"Cue Number": ""}, "Cue Number"),
        ({"Minutes": "1.5"}, "Minutes"),
        ({"Minutes": "-1"}, "Minutes"),
        ({"Seconds": "60"}, "Seconds"),
        ({"Seconds": "x"}, "Seconds"),
        ({"Fade": "-0.1"}, "Fade"),
        ({"Fade": "abc"}, "Fade"),
        ({"BPM": "120.5"}, "BPM"),
    ],
)
def test_invalid_fields_raise(changes, message):
    with pytest.raises(ValueError, match=message):
        validate_rows([valid_row(**changes)])


def test_duplicate_cues_raise_with_excel_row():
    rows = [valid_row(), valid_row(**{"Cue Number": "1", "_source_row": "9"})]
    with pytest.raises(ValueError) as error:
        validate_rows(rows)
    assert "duplicate cue number" in str(error.value)
    assert "Excel row 6" in str(error.value)


def test_collects_multiple_errors():
    rows = [valid_row(**{"Cue Number": "", "Seconds": "99", "Fade": "bad"})]
    with pytest.raises(ValueError) as error:
        validate_rows(rows)
    message = str(error.value)
    assert "Found 3 problem(s)" in message
