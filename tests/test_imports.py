"""Smoke tests for the modular project structure."""


def test_all_modules_import():
    import config
    import constants
    import engine
    import excel_io
    import plan2show
    import profiles


def test_shared_constants():
    from constants import APP_NAME, REQUIRED_COLUMNS, SUPPORTED_FRAME_RATES

    assert APP_NAME == "PLAN2SHOW"
    assert "Cue Number" in REQUIRED_COLUMNS
    assert "Actions" in REQUIRED_COLUMNS
    assert SUPPORTED_FRAME_RATES == (24, 25, 30)
