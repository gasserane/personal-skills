"""Planted tests for apply_answers.py (SRHR map skill, phase c, refresh steps 6 and 7).

Builds a synthetic map root (invented countries XAA..., invented codes) in a temporary folder:
config tables, a baseline register edition, a run file and an answered review workbook. Run:
    python test_apply_answers.py
"""
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import apply_answers as aa  # noqa: E402
import compare_register as cr  # noqa: E402
import review_workbook as rw  # noqa: E402

FAILS = []
SVC = "ippf_hiv_services"
FIELDS = [f["name"] for f in aa.load_register_contract()["fields"]]


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ': ' + detail}")
    if not cond:
        FAILS.append(name)


def reg_row(iso3, year, value, tick=True, **kw):
    r = {f: "" for f in FIELDS}
    r.update(iso3=iso3, topic="HIV", indicator_id=SVC, value=str(value), value_display=str(value),
             reference_year=str(year), source_id="ippf_dhis2", date_read="2026-01-01", machine_check="pass",
             member_status="Full member")
    if tick:
        r.update(ticked_by="Earlier Person", tick_date="2026-01-02")
    r.update(kw)
    return r


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def planted_root():
    """Baseline 2026: XAA 2025=100 (to be revised), XBB 2024=50 (gets a new 2025 value), XCC 2025=7 (missing)."""
    root = Path(tempfile.mkdtemp(prefix="srhr_aa_"))
    write_csv(root / "config" / "streams.csv", [{"key": "SA", "label": "Stream A", "group": "g", "colour": "#000000"}],
              ["key", "label", "group", "colour"])
    write_csv(root / "config" / "ma_codes.csv",
              [{"ma_code": "XA1", "iso3": "XAA", "org_name": "Org A", "ticked_by": "T", "tick_date": "2026-01-01"}],
              ["ma_code", "iso3", "org_name", "ticked_by", "tick_date"])
    base = [reg_row("XAA", 2025, 100), reg_row("XBB", 2024, 50), reg_row("XCC", 2025, 7)]
    write_csv(root / "map_register" / "map_register_2026.csv", base, FIELDS)
    proposed = [dict(reg_row("XAA", 2025, 120, tick=False), _link="f.csv"),
                dict(reg_row("XBB", 2025, 55, tick=False), _link="f.csv")]
    changes = cr.compare(base, proposed, {SVC: {"year": "2025", "link": "f.csv"}})
    aa.save_run(root, 2027, 2025, 2026, changes)
    lines = cr.group_changes(changes)
    wb = rw.write_workbook(lines, changes, root / "review" / "review_2027.xlsx", 2027, 2025)
    return root, wb, {c.kind + ":" + c.iso3: c.change_id for c in changes}


def answer(wb_path, by_id, reviewer="Test Reviewer", day=date(2026, 3, 1)):
    wb = load_workbook(wb_path)
    wb["How to use"][rw.REVIEWER_CELL].value = reviewer
    wb["How to use"][rw.DATE_CELL].value = day
    for ws in wb.worksheets:
        hdr = [c.value for c in ws[1]]
        if "change_ids" not in hdr:
            continue
        ci, ai, vi = hdr.index("change_ids"), hdr.index("Your answer"), hdr.index("Right value")
        for r in ws.iter_rows(min_row=2):
            for cid, (choice, value) in by_id.items():
                if r[ci].value and cid in r[ci].value.split(";"):
                    r[ai].value, r[vi].value = choice, value
    wb.save(wb_path)


def read_edition(root, ed):
    with open(root / "map_register" / f"map_register_{ed}.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def find(rows, iso3, year):
    return [r for r in rows if r["iso3"] == iso3 and r["reference_year"] == str(year)]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def test_planted_correct_row_enters_ticked():
    root, wb, ids = planted_root()
    before = sha(root / "map_register" / "map_register_2026.csv")
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)})
    res = aa.apply(root, 2027, wb)
    rows = read_edition(root, 2027)
    xaa = find(rows, "XAA", 2025)
    check("apply reports no problems", res.problems == [], str(res.problems))
    check("Correct row enters with the new value, ticked by the reviewer on the answer date",
          len(xaa) == 1 and xaa[0]["value"] == "120" and xaa[0]["ticked_by"] == "Test Reviewer"
          and xaa[0]["tick_date"] == "2026-03-01", str(xaa))
    check("ma_code filled from ma_codes.csv", xaa and xaa[0]["ma_code"] == "XA1", str(xaa))
    check("baseline rows carried with their old tick", find(rows, "XBB", 2024)[0]["ticked_by"] == "Earlier Person")
    check("baseline edition file byte-identical", sha(root / "map_register" / "map_register_2026.csv") == before)
    check("no private '_' columns in the written file", not any(k.startswith("_") for k in rows[0]), str(list(rows[0])))


def test_unanswered_rows_stay_unticked():
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None), ids["new:XBB"]: (rw.NOT_SURE, None)})
    res = aa.apply(root, 2027, wb)
    rows = read_edition(root, 2027)
    xbb = find(rows, "XBB", 2025)
    check("'Not sure' new row written unticked", len(xbb) == 1 and xbb[0]["ticked_by"] == ""
          and xbb[0]["tick_date"] == "", str(xbb))
    check("unanswered 'missing' writes no row", find(rows, "XCC", 2025) == [
        r for r in read_edition(root, 2026) if r["iso3"] == "XCC"], str(find(rows, "XCC", 2025)))
    check("counts: ticked 1, unticked 1", (res.ticked, res.unticked) == (1, 1), str(res))


def test_wrong_and_missing_correct():
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.WRONG, "130"), ids["missing:XCC"]: (rw.CORRECT, None)})
    aa.apply(root, 2027, wb)
    rows = read_edition(root, 2027)
    xaa, xcc = find(rows, "XAA", 2025), find(rows, "XCC", 2025)
    check("'Wrong' writes the corrected value, unticked, flagged for a second check",
          len(xaa) == 1 and xaa[0]["value"] == "130" and xaa[0]["ticked_by"] == ""
          and xaa[0]["machine_check"] == "colleague correction: second check", str(xaa))
    check("'missing' + Correct replaces the row: blank value, 'no report 2025', ticked",
          len(xcc) == 1 and xcc[0]["value"] == "" and xcc[0]["value_display"] == "no report 2025"
          and xcc[0]["ticked_by"] == "Test Reviewer", str(xcc))


def test_blank_reviewer_refuses_no_write():
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)}, reviewer="")
    res = aa.apply(root, 2027, wb)
    check("blank reviewer refused with a problem", any("Reviewer" in p for p in res.problems), str(res.problems))
    check("no edition file written", not (root / "map_register" / "map_register_2027.csv").exists())
    root2, wb2, ids2 = planted_root()
    answer(wb2, {ids2["revised:XAA"]: (rw.CORRECT, None)}, day=None)
    res2 = aa.apply(root2, 2027, wb2)
    check("blank date refused, no file", any("Date" in p for p in res2.problems)
          and not (root2 / "map_register" / "map_register_2027.csv").exists(), str(res2.problems))


def test_reapply_no_duplicates():
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None), ids["new:XBB"]: (rw.CORRECT, None)})
    aa.apply(root, 2027, wb)
    first = read_edition(root, 2027)
    res = aa.apply(root, 2027, wb)
    second = read_edition(root, 2027)
    check("second apply of the same workbook writes the same rows", first == second,
          f"{len(first)} vs {len(second)}")
    check("second apply backed up the first file", any((root / "map_register" / "_backup").glob("map_register_2027.*")))
    check("second apply reports no problems", res.problems == [], str(res.problems))


def test_later_unanswered_keeps_earlier_tick():
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)})
    aa.apply(root, 2027, wb)
    blank = root / "review" / "blank.xlsx"
    shutil.copy(root / "review" / "review_2027.xlsx", blank)
    answer(blank, {ids["revised:XAA"]: (None, None)})
    aa.apply(root, 2027, blank)
    xaa = find(read_edition(root, 2027), "XAA", 2025)
    check("a later unanswered workbook does not untick an earlier confirmed row",
          xaa and xaa[0]["ticked_by"] == "Test Reviewer", str(xaa))


def test_bad_row_restores_backup():
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)})
    aa.apply(root, 2027, wb)
    good = (root / "map_register" / "map_register_2027.csv").read_bytes()
    run = json.loads((root / "review" / "run_2027.json").read_text(encoding="utf-8"))
    for c in run["changes"]:
        if c["kind"] == "revised":
            c["new"]["reference_year"] = "20x5"  # breaks the int type
    (root / "review" / "run_2027.json").write_text(json.dumps(run), encoding="utf-8")
    res = aa.apply(root, 2027, wb)
    check("a row breaking the contract is reported", any("reference_year" in p for p in res.problems), str(res.problems))
    check("the edition file is restored byte for byte", (root / "map_register" / "map_register_2027.csv").read_bytes()
          == good)
    root2, wb2, ids2 = planted_root()
    run2 = json.loads((root2 / "review" / "run_2027.json").read_text(encoding="utf-8"))
    run2["changes"][0]["new"] = dict(run2["changes"][0]["new"] or {}, reference_year="20x5")
    (root2 / "review" / "run_2027.json").write_text(json.dumps(run2), encoding="utf-8")
    answer(wb2, {run2["changes"][0]["change_id"]: (rw.CORRECT, None)})
    aa.apply(root2, 2027, wb2)
    check("with no earlier file, a failing write leaves no edition file",
          not (root2 / "map_register" / "map_register_2027.csv").exists())


def test_never_writes_baseline_edition():
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)})
    before = sha(root / "map_register" / "map_register_2026.csv")
    res = aa.apply(root, 2026, wb)
    check("apply to the baseline's own edition refused", res.problems and "2026" in res.problems[0], str(res.problems))
    res = aa.apply(root, 2025, wb)
    check("apply to an earlier edition refused", bool(res.problems), str(res.problems))
    check("baseline untouched", sha(root / "map_register" / "map_register_2026.csv") == before)


def test_approve_refuses_with_unticked_changes():
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)})
    aa.apply(root, 2027, wb)
    try:
        aa.approve(root, 2027, "Owner")
        check("approve refuses while changes are unticked", False, "no refusal")
    except aa.ApproveRefused as e:
        check("approve refuses and lists the unticked changes",
              ids["new:XBB"] in str(e) and ids["missing:XCC"] in str(e), str(e))
    check("no approval file written", not (root / "map_register" / "approval_2027.json").exists())
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None), ids["new:XBB"]: (rw.CORRECT, None),
                ids["missing:XCC"]: (rw.CORRECT, None)})
    aa.apply(root, 2027, wb)
    p = aa.approve(root, 2027, "Owner")
    a = json.loads(p.read_text(encoding="utf-8"))
    check("approval names edition, approver and the register's sha256",
          a["edition"] == 2027 and a["approved_by"] == "Owner"
          and a["register_sha256"] == sha(root / "map_register" / "map_register_2027.csv"), str(a))


def test_check_register_rules():
    c = aa.load_register_contract()
    rows = [reg_row("XAA", 2025, 1), reg_row("xaa", 2025, 1), reg_row("XAA", 2025, 1, ticked_by="A", tick_date=""),
            reg_row("XAA", 2025, 1, source_id="public_src", snapshot_tag="")]
    probs = aa.check_register(rows, c)
    check("good row passes; bad iso3, half tick and public row without snapshot_tag each reported",
          len(probs) == 3 and not any("row 1 " in p for p in probs), str(probs))


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print(f"\n{'PASS' if not FAILS else 'FAIL'}: {len(FAILS)} failing check(s)")
    sys.exit(1 if FAILS else 0)
