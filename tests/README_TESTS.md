# PLAN2SHOW test suite

Copy all files from this folder into the existing `tests/` directory, replacing the original small test when prompted.

Run the complete suite from the project root:

```bash
python3 -m pytest -q
```

Run a focused group:

```bash
python3 -m pytest tests/test_timecode.py -q
python3 -m pytest tests/test_actions.py -q
python3 -m pytest tests/test_excel_io.py -q
```

The large number of parameterized cases covers all start hours from 00 through 23, all supported frame rates, invalid timecodes, action translations, Excel I/O, configuration persistence, profiles, and macro generation. The suite should still finish in seconds rather than hours.
