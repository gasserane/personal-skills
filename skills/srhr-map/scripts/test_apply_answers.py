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
    wb, changes = review(root, base, proposed, {SVC: {"year": "2025", "link": "f.csv"}})
    return root, wb, {c.kind + ":" + c.iso3: c.change_id for c in changes}


def review(root, base, proposed, covered, name="review_2027.xlsx", topic=None):
    """What refresh.py review does: compare, save the run file, write the workbook carrying the run digest."""
    changes = cr.compare(base, proposed, covered)
    run = aa.save_run(root, 2027, 2025, 2026, changes, topic=topic)
    digest = json.loads(run.read_text(encoding="utf-8"))["digest"]
    wb = rw.write_workbook(cr.group_changes(changes), changes, root / "review" / name, 2027, 2025,
                           run_digest=digest)
    return wb, changes


def edit_edition(root, ed, fn):
    """Hand-edit an edition file the way a person would in Excel/Notepad (fn changes the row list)."""
    rows = read_edition(root, ed)
    rows = fn(rows) or rows
    write_csv(root / "map_register" / f"map_register_{ed}.csv", rows, FIELDS)


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
    runf = root / "review" / "run_2027.json"
    run = json.loads(runf.read_text(encoding="utf-8"))
    for c in run["changes"]:
        if c["kind"] == "revised":
            c["new"]["reference_year"] = "20x5"  # breaks the int type (digest kept: a damaged file, same run)
    runf.write_text(json.dumps(run), encoding="utf-8")
    res = aa.apply(root, 2027, wb)
    check("a row breaking the contract is reported", any("reference_year" in p for p in res.problems), str(res.problems))
    check("the edition file is restored byte for byte", (root / "map_register" / "map_register_2027.csv").read_bytes()
          == good)
    root2, wb2, ids2 = planted_root()
    runf2 = root2 / "review" / "run_2027.json"
    run2 = json.loads(runf2.read_text(encoding="utf-8"))
    run2["changes"][0]["new"] = dict(run2["changes"][0]["new"] or {}, reference_year="20x5")
    runf2.write_text(json.dumps(run2), encoding="utf-8")
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


def test_stale_workbook_refused():
    """C1: a second review changes the value behind the same change_id; the first workbook must not tick it."""
    root, wb1, ids = planted_root()
    base = read_edition(root, 2026)
    proposed = [dict(reg_row("XAA", 2025, 125, tick=False), _link="f.csv"),
                dict(reg_row("XBB", 2025, 55, tick=False), _link="f.csv")]
    wb2, _ = review(root, base, proposed, {SVC: {"year": "2025", "link": "f.csv"}}, name="review_2027_b.xlsx")
    answer(wb1, {ids["revised:XAA"]: (rw.CORRECT, None)})
    res = aa.apply(root, 2027, wb1)
    check("C1: workbook from an earlier review is refused", any(p.startswith("Refused") and "earlier review" in p
                                                                for p in res.problems), str(res.problems))
    check("C1: nothing written for the stale workbook", not (root / "map_register" / "map_register_2027.csv").exists())
    answer(wb2, {ids["revised:XAA"]: (rw.CORRECT, None)})
    res = aa.apply(root, 2027, wb2)
    xaa = find(read_edition(root, 2027), "XAA", 2025)
    check("C1: the current workbook applies the value it showed (125)", res.problems == [] and xaa
          and xaa[0]["value"] == "125" and xaa[0]["ticked_by"] == "Test Reviewer", f"{res.problems} {xaa}")


def test_missing_ids_sheet_refused():
    """minor: without the hidden id list the workbook cannot be matched to its run; apply must stop."""
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)})
    book = load_workbook(wb)
    del book[rw.IDS_SHEET]
    book.save(wb)
    res = aa.apply(root, 2027, wb)
    check("no _ids sheet: apply refused, nothing written",
          any(p.startswith("Refused") for p in res.problems)
          and not (root / "map_register" / "map_register_2027.csv").exists(), str(res.problems))


def test_ids_differ_from_run_refused():
    """I1: ids on the hidden sheet that the run does not hold (or the reverse) are listed and refused."""
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)})
    book = load_workbook(wb)
    book[rw.IDS_SHEET]["A1"].value = "zzzzzzzzzz"
    book.save(wb)
    res = aa.apply(root, 2027, wb)
    check("I1: one-sided ids listed and refused, nothing written",
          any(p.startswith("Refused") and "zzzzzzzzzz" in p for p in res.problems)
          and not (root / "map_register" / "map_register_2027.csv").exists(), str(res.problems))


def test_topic_reviews_keep_both_answers():
    """I1: a --topic review must not overwrite the other topic's run; both workbooks apply and approve."""
    root, _, _ = planted_root()
    fund = dict(reg_row("XAA", 2026, 1, topic="funding", indicator_id="ippf_funding_streams", value_display="SA"))
    base = read_edition(root, 2026) + [fund]
    write_csv(root / "map_register" / "map_register_2026.csv", base, FIELDS)
    hiv_new = [dict(reg_row("XAA", 2025, 120, tick=False), _link="f.csv"),
               dict(reg_row("XBB", 2025, 55, tick=False), _link="f.csv"),
               dict(reg_row("XCC", 2025, 7, tick=False), _link="f.csv")]
    fund_new = [dict(fund, value="2", value_display="SA, SB", ticked_by="", tick_date="", _link="l.xlsx")]
    wbh, ch = review(root, [b for b in base if b["topic"] == "HIV"], hiv_new, {SVC: {"year": "2025", "link": "f"}},
                     name="hiv.xlsx", topic="HIV")
    wbf, cf = review(root, [fund], fund_new, {"ippf_funding_streams": {"year": "2026", "link": "l"}},
                     name="fund.xlsx", topic="funding")
    answer(wbh, {c.change_id: (rw.CORRECT, None) for c in ch})
    answer(wbf, {c.change_id: (rw.CORRECT, None) for c in cf})
    r1, r2 = aa.apply(root, 2027, wbh), aa.apply(root, 2027, wbf)
    rows = read_edition(root, 2027)
    f = [r for r in rows if r["indicator_id"] == "ippf_funding_streams" and r["reference_year"] == "2026"]
    check("I1: both topic workbooks apply", r1.problems == [] and r2.problems == [], f"{r1.problems} {r2.problems}")
    check("I1: funding answer ticked", f and f[0]["value"] == "2" and f[0]["ticked_by"] == "Test Reviewer", str(f))
    check("I1: HIV answer ticked", find(rows, "XAA", 2025)[0]["ticked_by"] == "Test Reviewer")
    try:
        aa.approve(root, 2027, "Owner")
        check("I1: approve sees both topics resolved", True)
    except aa.ApproveRefused as e:
        check("I1: approve sees both topics resolved", False, str(e))


def test_approved_edition_not_rewritten():
    """C2: once approval_<edition>.json exists, apply refuses and the file stays byte-identical."""
    root, wb, ids = planted_root()
    answer(wb, {i: (rw.CORRECT, None) for i in ids.values()})
    aa.apply(root, 2027, wb)
    aa.approve(root, 2027, "Owner")
    before = sha(root / "map_register" / "map_register_2027.csv")
    answer(wb, {ids["revised:XAA"]: (rw.WRONG, "999")})
    res = aa.apply(root, 2027, wb)
    check("C2: apply to an approved edition refused", any(p.startswith("Refused") and "approved" in p
                                                          for p in res.problems), str(res.problems))
    check("C2: approved file unchanged", sha(root / "map_register" / "map_register_2027.csv") == before)


def test_target_not_made_by_apply_refused():
    """C2: a map_register_<edition>.csv that apply did not create (hand-made, migration) is never rewritten."""
    root, wb, ids = planted_root()
    shutil.copy(root / "map_register" / "map_register_2026.csv", root / "map_register" / "map_register_2027.csv")
    before = sha(root / "map_register" / "map_register_2027.csv")
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)})
    res = aa.apply(root, 2027, wb)
    check("C2: existing edition apply did not create is refused", any(p.startswith("Refused") for p in res.problems),
          str(res.problems))
    check("C2: that file unchanged", sha(root / "map_register" / "map_register_2027.csv") == before)


def test_reapply_keeps_later_hand_tick():
    """I3: 'Wrong' / 'Not sure' answered again must not untick a row a person ticked by hand since."""
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.WRONG, "130"), ids["new:XBB"]: (rw.NOT_SURE, None)})
    aa.apply(root, 2027, wb)

    def hand_tick(rows):
        for r in rows:
            if (r["iso3"], r["reference_year"]) in (("XAA", "2025"), ("XBB", "2025")):
                r.update(ticked_by="Hand Person", tick_date="2026-04-01")
    edit_edition(root, 2027, hand_tick)
    aa.apply(root, 2027, wb)
    rows = read_edition(root, 2027)
    check("I3: corrected row ticked by hand stays ticked after re-apply",
          find(rows, "XAA", 2025)[0]["ticked_by"] == "Hand Person", str(find(rows, "XAA", 2025)))
    check("I3: 'Not sure' row ticked by hand stays ticked after re-apply",
          find(rows, "XBB", 2025)[0]["ticked_by"] == "Hand Person", str(find(rows, "XBB", 2025)))


def test_partner_changes_can_be_approved():
    """I5: partner rows key on their value; a missing partner and a corrected partner must both resolve."""
    root, _, _ = planted_root()
    P = cr.PARTNER
    old = reg_row("XDD", 2024, "SA", topic="funding", indicator_id=P)
    base = read_edition(root, 2026) + [old]
    write_csv(root / "map_register" / "map_register_2026.csv", base, FIELDS)
    proposed = [dict(reg_row("XAA", 2025, 100, tick=False), _link="f.csv"),
                dict(reg_row("XBB", 2025, 50, tick=False), _link="f.csv"),
                dict(reg_row("XCC", 2025, 7, tick=False), _link="f.csv"),
                dict(reg_row("XEE", 2025, "SB", tick=False, topic="funding", indicator_id=P), _link="l.xlsx")]
    wb, changes = review(root, base, proposed, {SVC: {"year": "2025", "link": "f.csv"},
                                                P: {"year": "2025", "link": "l.xlsx"}})
    by = {c.kind + ":" + c.iso3: c.change_id for c in changes}
    answer(wb, {c.change_id: (rw.CORRECT, None) for c in changes} | {by["new:XEE"]: (rw.WRONG, "SC")})
    res = aa.apply(root, 2027, wb)

    def hand_tick(rows):
        for r in rows:
            if r["iso3"] == "XEE":
                r.update(ticked_by="Hand Person", tick_date="2026-04-01")
    edit_edition(root, 2027, hand_tick)
    left = aa.unresolved(root, 2027)
    check("I5: missing partner (Correct) and corrected partner (hand-ticked) both resolved",
          res.problems == [] and left == [], f"{res.problems} {left}")


def test_truncated_target_refused():
    """I7: an edition file that lost rows of the last edition is not built on."""
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)})
    aa.apply(root, 2027, wb)
    edit_edition(root, 2027, lambda rows: [r for r in rows if r["iso3"] != "XBB"])
    before = sha(root / "map_register" / "map_register_2027.csv")
    res = aa.apply(root, 2027, wb)
    check("I7: target missing rows of the last edition is refused", any(p.startswith("Refused") and "XBB" in p
                                                                       for p in res.problems), str(res.problems))
    check("I7: truncated file left as it was", sha(root / "map_register" / "map_register_2027.csv") == before)


def test_interrupted_write_keeps_target():
    """I7: a write that dies half-way (disk full, file locked) leaves the earlier edition file whole."""
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)})
    aa.apply(root, 2027, wb)
    target = root / "map_register" / "map_register_2027.csv"
    good = target.read_bytes()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None), ids["new:XBB"]: (rw.CORRECT, None)})
    real = Path.write_bytes

    def half(self, data):
        real(self, data[: len(data) // 2])
        raise OSError("disk full (planted)")
    Path.write_bytes = half
    try:
        res = aa.apply(root, 2027, wb)
    except OSError as e:
        res = aa.ApplyResult(problems=[f"CRASH {e}"])
    finally:
        Path.write_bytes = real
    check("I7: interrupted write reported as a plain 'Stopped' line, no crash",
          any(p.startswith("Stopped") for p in res.problems), str(res.problems))
    check("I7: target byte-identical after an interrupted write", target.read_bytes() == good)
    check("I7: no temporary file left behind", not list(target.parent.glob("*.tmp")), str(list(target.parent.iterdir())))


def test_bad_workbook_path_is_plain_refusal():
    """I6: a mistyped path or a .csv given as --workbook gives a 'Refused' line, not a stack trace."""
    root, wb, ids = planted_root()
    for bad in (root / "review" / "nope.xlsx", root / "map_register" / "map_register_2026.csv"):
        try:
            res = aa.apply(root, 2027, bad)
            ok = any(p.startswith("Refused") for p in res.problems)
        except Exception as e:  # noqa: BLE001
            ok, res = False, f"{type(e).__name__}: {e}"
        check(f"I6: --workbook {bad.name} refused plainly", ok, str(res))


def test_config_error_is_plain_stop():
    """I6: a broken config table during apply gives a 'Stopped' line, not a stack trace."""
    root, wb, ids = planted_root()
    answer(wb, {ids["revised:XAA"]: (rw.CORRECT, None)})
    (root / "config" / "ma_codes.csv").unlink()
    try:
        res = aa.apply(root, 2027, wb)
        ok = any(p.startswith("Stopped") and "ma_codes.csv" in p for p in res.problems)
    except Exception as e:  # noqa: BLE001
        ok, res = False, f"{type(e).__name__}: {e}"
    check("I6: missing ma_codes.csv stops apply plainly", ok, str(res))


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
            try:
                fn()
            except Exception as e:  # a crash is a failure, reported by name
                check(name, False, f"{type(e).__name__}: {e}")
    print(f"\n{'PASS' if not FAILS else 'FAIL'}: {len(FAILS)} failing check(s)")
    sys.exit(1 if FAILS else 0)
