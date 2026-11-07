"""Planted tests for config_tables.py (SRHR map skill, phase c).

Synthetic config files with invented keys only. Run:  python test_config_tables.py
"""
import csv
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import config_tables as ct  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ': ' + detail}")
    if not cond:
        FAILS.append(name)


def make_root(tmp, codes, streams=None):
    root = Path(tmp)
    (root / "config").mkdir()
    with open(root / "config" / "ma_codes.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ma_code", "iso3", "org_name", "ticked_by", "tick_date"])
        w.writerows(codes)
    with open(root / "config" / "streams.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "label", "group", "colour"])
        w.writerows(streams or [["Stream A", "Label A", "G1", "111111"], ["Stream B", "Label B", "G2", "222222"]])
    return root


def test_unticked_codes_ignored():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_root(tmp, [["901", "XAA", "Org One", "Reviewer", "2026-11-08"],
                               ["902", "XBB", "Org Two", "", ""]])
        streams, codes = ct.load_config(root)
        check("only ticked codes are used", codes == {"901": "XAA"}, str(codes))
        check("streams keep their order", [s["key"] for s in streams] == ["Stream A", "Stream B"], str(streams))


def test_duplicate_code_raises():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_root(tmp, [["901", "XAA", "a", "R", "2026-11-08"], ["901", "XBB", "b", "R", "2026-11-08"]])
        try:
            ct.load_config(root)
            check("duplicate ma_code raises ConfigError", False, "no error")
        except ct.ConfigError as e:
            check("duplicate ma_code raises ConfigError", "901" in str(e), str(e))


def test_ticked_code_without_iso3_raises():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_root(tmp, [["901", "", "a", "R", "2026-11-08"]])
        try:
            ct.load_config(root)
            check("ticked code with no iso3 raises", False, "no error")
        except ct.ConfigError as e:
            check("ticked code with no iso3 raises", "901" in str(e), str(e))


def test_missing_file_plain_message():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            ct.load_config(Path(tmp))
            check("missing config file raises", False, "no error")
        except ct.ConfigError as e:
            check("missing config file raises a plain message", "config" in str(e) and "Traceback" not in str(e),
                  str(e))


def test_duplicate_stream_key_raises():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_root(tmp, [], streams=[["Stream A", "L", "G", "1"], ["Stream A", "L2", "G", "2"]])
        try:
            ct.load_config(root)
            check("duplicate stream key raises", False, "no error")
        except ct.ConfigError as e:
            check("duplicate stream key raises", "Stream A" in str(e), str(e))


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:
                check(name, False, f"{type(e).__name__}: {e}")
    print(f"\n{'PASS' if not FAILS else 'FAIL'}: {len(FAILS)} failing check(s)")
    sys.exit(1 if FAILS else 0)
