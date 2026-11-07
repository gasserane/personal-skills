"""Planted tests for refresh.py (SRHR map skill, phase c, the refresh CLI).

Builds a synthetic map root (invented countries XAA..., invented codes) in a temporary folder and
drives refresh.main() the way a colleague would from the command line. Run:
    python test_refresh.py
"""
import contextlib
import csv
import io
import json
import os
import sys
import tempfile
from datetime import date
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import apply_answers as aa  # noqa: E402
import refresh  # noqa: E402
import review_workbook as rw  # noqa: E402
from test_dropin_check import make, spec_of, valid_row  # noqa: E402

FAILS = []
FIELDS = [f["name"] for f in aa.load_register_contract()["fields"]]


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ': ' + detail}")
    if not cond:
        FAILS.append(name)


def run(*argv, env_root=None):
    """Run refresh.main(argv); return (exit code, printed text)."""
    old = os.environ.pop("SRHR_MAP_ROOT", None)
    if env_root:
        os.environ["SRHR_MAP_ROOT"] = str(env_root)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            try:
                code = refresh.main(list(argv))
            except SystemExit as e:
                code = e.code
    finally:
        os.environ.pop("SRHR_MAP_ROOT", None)
        if old is not None:
            os.environ["SRHR_MAP_ROOT"] = old
    return code, buf.getvalue()


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def planted_root():
    """Config tables plus a 2026 baseline: XAA HIV services 2025 = 100."""
    root = Path(tempfile.mkdtemp(prefix="srhr_rf_"))
    write_csv(root / "config" / "streams.csv", [{"key": "SA", "label": "Stream A", "group": "g", "colour": "#000000"}],
              ["key", "label", "group", "colour"])
    write_csv(root / "config" / "ma_codes.csv",
              [{"ma_code": "100", "iso3": "XAA", "org_name": "Org A", "ticked_by": "T", "tick_date": "2026-01-01"}],
              ["ma_code", "iso3", "org_name", "ticked_by", "tick_date"])
    base = {f: "" for f in FIELDS}
    base.update(iso3="XAA", ma_code="100", topic="HIV", indicator_id="ippf_hiv_services", value="100",
                value_display="100", reference_year="2025", source_id="ippf_dhis2_service_stats",
                date_read="2026-01-01", machine_check="pass", member_status="Full member",
                ticked_by="Earlier Person", tick_date="2026-01-02")
    write_csv(root / "map_register" / "map_register_2026.csv", [base], FIELDS)
    return root


def dhis2(root, year, period, extra=()):
    spec = spec_of("ippf_dhis2_annual", "services")
    folder = root / "drop_in" / str(year)
    folder.mkdir(parents=True, exist_ok=True)
    row = dict(valid_row(spec, period), dataelement="SRV-HIV and AIDS counselling",
               orgunit="Static Clinics (XX100-0000)", categoryoptioncombo="0 - 24", value="120")
    return make(folder, "dataValueSets.csv", spec, period, rows=[row, *extra])


def test_no_map_root_message():
    code, out = run("list", "--year", "2025")
    check("no map root: exit is not 0", code not in (0, None), f"code {code}")
    check("no map root: asks where the folder is", "Tell me where the SRHR map data folder is" in out, out)


def test_map_root_from_environment():
    root = planted_root()
    code, out = run("list", "--year", "2025", env_root=root)
    check("SRHR_MAP_ROOT is used when --map-root is absent", code == 0 and "dataValueSets.csv" in out, out)


def test_list_names_every_expected_file():
    root = planted_root()
    dhis2(root, 2025, 2025)
    code, out = run("list", "--year", "2025", "--map-root", str(root))
    check("list exits 0", code == 0, out)
    for pattern in ("dataValueSets.csv", "*.xlsx", "business_plan_focus_*.csv"):
        check(f"list names {pattern}", pattern in out, out)
    check("list says which files are already there", "found" in out and "not found" in out, out)


def test_broken_file_stops_plain():
    root = planted_root()
    spec = spec_of("ippf_subgranting", "ledger_projects")
    folder = root / "drop_in" / "2025"
    folder.mkdir(parents=True)
    make(folder, "ledger.xlsx", spec, 2026, sheet="Renamed sheet")
    code, out = run("check", "--year", "2025", "--map-root", str(root))
    first = next((l for l in out.splitlines() if l.strip()), "")
    stop = [l for l in out.splitlines() if l.startswith("Stopped:")]
    check("renamed sheet: exit 1", code == 1, f"code {code}: {out}")
    check("renamed sheet: one plain 'Stopped:' line naming the file and the fix",
          len(stop) == 1 and "ledger.xlsx does not match its contract" in stop[0]
          and stop[0].endswith("Fix the file and run check again."), out)
    check("renamed sheet: no stack trace", "Traceback" not in out, out)
    check("renamed sheet: the Stopped line is not buried under other output", first.startswith(("Stopped:", "Checking")),
          first)


def test_wrong_year_stops():
    root = planted_root()
    dhis2(root, 2026, 2025)  # a 2025 export dropped into the 2026 folder
    code, out = run("check", "--year", "2026", "--map-root", str(root))
    check("wrong-year file: check exits 1 with 'Stopped:'", code == 1 and "Stopped:" in out and "period" in out, out)
    code, out = run("review", "--year", "2026", "--map-root", str(root))
    check("wrong-year file: review stops too", code == 1 and "Stopped:" in out, out)
    check("wrong-year file: no workbook and no run file written",
          not list((root / "review").glob("*")) if (root / "review").exists() else True,
          str(list((root / "review").glob("*"))) if (root / "review").exists() else "")


def test_review_writes_workbook_and_run():
    root = planted_root()
    unknown = dict(valid_row(spec_of("ippf_dhis2_annual", "services"), 2025),
                   dataelement="SRV-HIV and AIDS counselling", orgunit="Static Clinics (XX123A-0000)",
                   categoryoptioncombo="0 - 24", value="5")
    dhis2(root, 2025, 2025, extra=[unknown])
    code, out = run("review", "--topic", "HIV", "--year", "2025", "--edition", "2027", "--map-root", str(root))
    books = sorted((root / "review").glob("review_2027_*.xlsx"))
    runf = root / "review" / "run_2027_HIV.json"
    check("review exits 0", code == 0, out)
    check("review writes one review_<edition>_<timestamp>.xlsx", len(books) == 1, str(books))
    check("review --topic HIV writes run_<edition>_HIV.json through save_run (I1: one run file per topic)",
          runf.exists(), out)
    if runf.exists():
        r = json.loads(runf.read_text(encoding="utf-8"))
        check("run file records baseline 2026 and reporting year 2025",
              r["baseline_edition"] == 2026 and r["reporting_year"] == 2025, str(r)[:200])
        check("run file holds the revised XAA change",
              any(c["kind"] == "revised" and c["iso3"] == "XAA" for c in r["changes"]), str(r["changes"])[:300])
    if books:
        how = [str(c.value) for row in load_workbook(books[0])["How to use"].iter_rows() for c in row if c.value]
        check("unknown organisation code reaches the reviewer on 'How to use'",
              any("unknown organisation code '123A'" in t for t in how), str(how))
    check("review prints the workbook path", books and str(books[0].name) in out, out)


def test_files_in_role_subfolders_are_found():
    """The real folder holds drop_in/<year>/dhis2, subgranting, business_plans; files there must be found."""
    root = planted_root()
    sub = root / "drop_in" / "2025" / "dhis2"
    sub.mkdir(parents=True)
    spec = spec_of("ippf_dhis2_annual", "services")
    row = dict(valid_row(spec, 2025), dataelement="SRV-HIV and AIDS counselling",
               orgunit="Static Clinics (XX100-0000)", categoryoptioncombo="0 - 24", value="120")
    make(sub, "dataValueSets.csv", spec, 2025, rows=[row])
    code, out = run("list", "--year", "2025", "--map-root", str(root))
    check("list finds a file in drop_in/<year>/dhis2", "found: dataValueSets.csv" in out, out)
    check("list names the subfolder for each file", "dhis2" in out and "subgranting" in out and "business_plans" in out,
          out)
    code, out = run("review", "--topic", "HIV", "--year", "2025", "--edition", "2027", "--map-root", str(root))
    runf = root / "review" / "run_2027_HIV.json"
    changes = json.loads(runf.read_text(encoding="utf-8"))["changes"] if runf.exists() else []
    check("review derives rows from the subfolder file", code == 0 and any(c["iso3"] == "XAA" for c in changes), out)


def test_apply_and_approve_through_cli():
    root = planted_root()
    dhis2(root, 2025, 2025)
    run("review", "--topic", "HIV", "--year", "2025", "--edition", "2027", "--map-root", str(root))
    book = sorted((root / "review").glob("review_2027_*.xlsx"))[0]
    code, out = run("apply", "--year", "2025", "--edition", "2027", "--workbook", str(book), "--map-root", str(root))
    check("apply with a blank reviewer: exit 1, 'Refused', nothing written",
          code == 1 and "Refused" in out and not (root / "map_register" / "map_register_2027.csv").exists(), out)
    wb = load_workbook(book)
    wb["How to use"][rw.REVIEWER_CELL].value = "Test Reviewer"
    wb["How to use"][rw.DATE_CELL].value = date(2026, 3, 1)
    for ws in wb.worksheets:
        hdr = [c.value for c in ws[1]]
        if "change_ids" in hdr:
            for r in ws.iter_rows(min_row=2):
                if r[hdr.index("change_ids")].value:
                    r[hdr.index("Your answer")].value = rw.CORRECT
    wb.save(book)
    code, out = run("apply", "--year", "2025", "--edition", "2027", "--workbook", str(book), "--map-root", str(root))
    check("apply exits 0 and writes the 2027 edition",
          code == 0 and (root / "map_register" / "map_register_2027.csv").exists(), out)
    code, out = run("approve", "--year", "2025", "--edition", "2027", "--map-root", str(root))
    check("approve without --by: exit 1, 'Not approved'", code == 1 and "Not approved" in out, out)
    code, out = run("approve", "--year", "2025", "--edition", "2027", "--by", "Owner", "--map-root", str(root))
    check("approve with every change ticked: exit 0, approval file written",
          code == 0 and (root / "map_register" / "approval_2027.json").exists(), out)


def test_corrupt_ledger_and_lock_file_stop_plain():
    """I6: a damaged ledger, or Excel's '~$' lock file beside it, gives a 'Stopped:' line, no stack trace."""
    root = planted_root()
    sub = root / "drop_in" / "2025" / "subgranting"
    sub.mkdir(parents=True)
    (sub / "ledger.xlsx").write_bytes(b"this is not a workbook")
    (sub / "~$ledger.xlsx").write_bytes(b"lock")
    for cmd in ("check", "review"):
        try:
            code, out = run(cmd, "--topic", "funding", "--year", "2025", "--map-root", str(root))
        except Exception as e:  # noqa: BLE001
            code, out = None, f"{type(e).__name__}: {e}"
        check(f"I6: {cmd} on a damaged ledger exits 1 with 'Stopped:'", code == 1 and "Stopped:" in out
              and "~$" not in out, out)


def test_apply_bad_workbook_or_config_exit_1():
    """I6: cmd_apply turns a missing or non-xlsx workbook and a config error into exit 1, not a crash."""
    root = planted_root()
    dhis2(root, 2025, 2025)
    run("review", "--topic", "HIV", "--year", "2025", "--edition", "2027", "--map-root", str(root))
    for bad in ("nope.xlsx", str(root / "map_register" / "map_register_2026.csv")):
        try:
            code, out = run("apply", "--year", "2025", "--edition", "2027", "--workbook", bad, "--map-root", str(root))
        except Exception as e:  # noqa: BLE001
            code, out = None, f"{type(e).__name__}: {e}"
        check(f"I6: apply --workbook {Path(bad).name}: exit 1, plain line", code == 1 and "Traceback" not in out, out)


def main():
    for t in (test_corrupt_ledger_and_lock_file_stop_plain, test_apply_bad_workbook_or_config_exit_1, test_no_map_root_message, test_map_root_from_environment, test_list_names_every_expected_file,
              test_broken_file_stops_plain, test_wrong_year_stops, test_review_writes_workbook_and_run,
              test_files_in_role_subfolders_are_found, test_apply_and_approve_through_cli):
        print(f"-- {t.__name__}")
        try:
            t()
        except Exception as e:  # a crash is a failure, reported by name
            check(t.__name__, False, f"{type(e).__name__}: {e}")
    print(f"{'PASS' if not FAILS else 'FAIL'}: {len(FAILS)} failing check(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
