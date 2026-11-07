"""Planted tests for review_workbook.py (SRHR map skill, phase c, refresh step 5).

Invented countries (XAA...) and values only. Writes into a temporary folder. Run:
    python test_review_workbook.py
The branded case needs the organisation's reporting package (found via WORK_FOLDER_ROOT or the
current folder); without it the case is reported as SKIPPED, never as passed.
"""
import csv
import sys
import tempfile
from datetime import date
from pathlib import Path

from openpyxl import Workbook, load_workbook

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import compare_register as cr  # noqa: E402
import review_workbook as rw  # noqa: E402

FAILS, SKIPS = [], []
TMP = Path(tempfile.mkdtemp(prefix="srhr_rw_"))
SVC = "ippf_hiv_services"


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ': ' + detail}")
    if not cond:
        FAILS.append(name)


def planted_files():
    xlsx = TMP / "ledger.xlsx"
    wb = Workbook()
    wb.active.title = "projects 2026"
    wb.save(xlsx)
    csvf = TMP / "dataValueSets.csv"
    with open(csvf, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["orgUnit", "value"])
    return xlsx, csvf


XLSX, CSVF = planted_files()


def row(iso3, year, value, link):
    return {"iso3": iso3, "indicator_id": SVC, "reference_year": str(year), "value": str(value),
            "value_display": str(value), "ticked_by": "", "_link": link}


def build(n_revised=3, link=None, name="review.xlsx"):
    """n_revised revised rows (each its own line) plus three grouped new rows."""
    link = link or str(CSVF)
    isos = [f"X{chr(65 + i // 26)}{chr(65 + i % 26)}" for i in range(n_revised + 3)]
    base = [row(i, 2025, 100, link) for i in isos[:n_revised]] + [row(i, 2024, 100, link) for i in isos[n_revised:]]
    new = [row(i, 2025, 200, link) for i in isos[:n_revised]] + [row(i, 2025, 110, link) for i in isos[n_revised:]]
    changes = cr.compare(base, new, {SVC: {"year": "2025", "link": link}})
    lines = cr.group_changes(changes)
    out = rw.write_workbook(lines, changes, TMP / name, edition=2026, reporting_year=2025)
    return out, lines, changes


def data_rows(ws):
    hdr = [c.value for c in ws[1]]
    return hdr, [r for r in ws.iter_rows(min_row=2) if any(c.value for c in r)]


def test_every_check_line_has_hyperlink():
    out, lines, _ = build(link=f"{XLSX}#'projects 2026'")
    ws = load_workbook(out)["Must check"]
    hdr, rows = data_rows(ws)
    col = hdr.index("Look here")
    must = [l for l in lines if l.sheet == "Must check"]
    targets = [r[col].hyperlink.target if r[col].hyperlink else None for r in rows]
    check("one sheet row per Must-check line", len(rows) == len(must), f"{len(rows)} rows, {len(must)} lines")
    check("every Must-check row has a hyperlink target", rows and all(targets), str(targets))
    check("xlsx link points at the planted file and names the sheet",
          all(t and "ledger.xlsx" in t for t in targets)
          and all(r[col].hyperlink.location and "projects 2026" in r[col].hyperlink.location for r in rows),
          str([(r[col].hyperlink.target, r[col].hyperlink.location) for r in rows]))


def test_csv_link_names_filter():
    out, _, _ = build(link=str(CSVF), name="csv.xlsx")
    ws = load_workbook(out)["Must check"]
    hdr, rows = data_rows(ws)
    g = hdr.index("What correct looks like")
    check("csv line tells the reader which country to filter on",
          all("Filter" in (r[g].value or "") for r in rows), str([r[g].value for r in rows]))


def test_must_check_at_most_30():
    out, lines, _ = build(n_revised=40, name="many.xlsx")
    wb = load_workbook(out)
    _, must = data_rows(wb["Must check"])
    _, opt = data_rows(wb["Optional"])
    check("Must check holds at most 30 lines", len(must) <= cr.MAX_MUST, str(len(must)))
    check("overflow lines are on Optional, none lost", len(must) + len(opt) == len(lines),
          f"{len(must)}+{len(opt)} vs {len(lines)}")


def _answer(ws, choice_by_row):
    hdr, rows = data_rows(ws)
    a, v = hdr.index("Your answer"), hdr.index("Right value")
    for r, (choice, value) in zip(rows, choice_by_row):
        r[a].value, r[v].value = choice, value


def test_answers_keyed_by_change_id_after_sort():
    out, lines, changes = build(name="sorted.xlsx")
    wb = load_workbook(out)
    wb["How to use"][rw.REVIEWER_CELL].value = "Test Reviewer"
    wb["How to use"][rw.DATE_CELL].value = date(2026, 1, 15)
    ws = wb["Must check"]
    hdr, rows = data_rows(ws)
    ids_col = hdr.index("change_ids")
    _answer(ws, [("Correct", None)] * len(rows))
    values = [[c.value for c in r] for r in rows]
    for r, vals in zip(rows, reversed(values)):  # colleague sorts the sheet
        for c, v in zip(r, vals):
            c.value = v
    deleted = rows[0][ids_col].value
    ws.delete_rows(2)  # colleague deletes the first row
    ws.title = "My check"  # and renames the sheet
    wb.save(out)
    header, answers, problems = rw.read_answers(out)
    gone = deleted.split(";")
    kept = [c.change_id for c in changes if c.change_id not in gone]
    check("reviewer and date read back", header == {"reviewer": "Test Reviewer", "date": "2026-01-15"}, str(header))
    check("answers of kept rows found by change_id, not position",
          all(answers.get(i) and answers[i].choice == "Correct" for i in kept), str(answers))
    check("deleted row's change_ids are reported missing",
          all(any(i in p for p in problems) for i in gone) and not any(i in answers for i in gone), str(problems))


def test_wrong_needs_value_and_blank_is_not_sure():
    out, lines, _ = build(name="wrong.xlsx")
    wb = load_workbook(out)
    ws = wb["Must check"]
    _, rows = data_rows(ws)
    _answer(ws, [(rw.WRONG, "")] + [(rw.WRONG, "250")] + [(None, None)] * (len(rows) - 2))
    wb.save(out)
    _, answers, problems = rw.read_answers(out)
    first = [l for l in lines if l.sheet == "Must check"][0].change_ids[0]
    second = [l for l in lines if l.sheet == "Must check"][1].change_ids[0]
    check("'Wrong' without a right value is a problem", any(first in p and "Right value" in p for p in problems),
          str(problems))
    check("'Wrong' with a value carries the corrected value", answers[second].corrected_value == "250",
          str(answers.get(second)))
    check("blank answers come back as blank choice", all(a.choice == "" for i, a in answers.items()
                                                         if i not in (first, second)), str(answers))


def test_dropdown_values_exact():
    out, _, _ = build(name="dv.xlsx")
    ws = load_workbook(out)["Must check"]
    dvs = [d for d in ws.data_validations.dataValidation if d.type == "list"]
    got = dvs[0].formula1.strip('"').split(",") if dvs else []
    check("dropdown values exactly as specified", got == ["Correct", "Wrong: right value in next column", "Not sure"],
          str(got))


def test_untestable_link_labelled():
    rw.http_head = lambda url, timeout=10: False  # the sandbox blocks the site
    out, _, _ = build(link="https" + "://example.invalid/page", name="web.xlsx")
    ws = load_workbook(out)["Must check"]
    hdr, rows = data_rows(ws)
    col = hdr.index("Look here")
    texts = [r[col].value or "" for r in rows]
    check("unreachable web link labelled 'not tested here'",
          all("not tested here (sandbox blocks this site)" in t for t in texts), str(texts))
    check("unreachable web link still written as a hyperlink",
          all(r[col].hyperlink and r[col].hyperlink.target.startswith("https") for r in rows))


def test_detail_one_row_per_change():
    out, _, changes = build(name="detail.xlsx")
    wb = load_workbook(out)
    hdr, rows = data_rows(wb["Detail"])
    ids = [r[hdr.index("change_id")].value for r in rows]
    check("Detail has one row per change_id", sorted(ids) == sorted(c.change_id for c in changes), str(ids))
    check("the id list sheet is very hidden", wb[rw.IDS_SHEET].sheet_state == "veryHidden",
          wb[rw.IDS_SHEET].sheet_state)


def test_branded_when_package_available():
    if not rw.brand_package():
        SKIPS.append("branded")
        print("SKIPPED branded workbook (reporting package not found; set WORK_FOLDER_ROOT)")
        return
    import zipfile
    out, _, _ = build(name="branded.xlsx")
    z = zipfile.ZipFile(out)
    names = z.namelist()
    sheets = [n for n in names if n.startswith("xl/worksheets/sheet")]
    check("branded workbook embeds the logo/pillar images", any(n.startswith("xl/media/") for n in names))
    check("every sheet carries the print header/footer",
          all("<headerFooter" in z.read(n).decode("utf-8") for n in sheets))


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print(f"\n{'PASS' if not FAILS else 'FAIL'}: {len(FAILS)} failing check(s)"
          + (f", {len(SKIPS)} skipped" if SKIPS else ""))
    sys.exit(1 if FAILS else 0)
