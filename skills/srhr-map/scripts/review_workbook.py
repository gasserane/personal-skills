"""Write the review workbook and read the answers back (SRHR map skill, phase c, refresh step 5).

write_workbook() turns review lines into a short branded workbook a colleague answers in one sitting:
  How to use   three steps, plus the Reviewer and Date answered cells
  Must check   at most compare_register.MAX_MUST lines
  Optional     overflow lines and rows the Intelligence Tool owner already ticked
  Detail       one row per change
  Glossary     plain-language terms
and a very hidden id list. read_answers() keys every answer on the hidden change_ids column and finds
columns by their header text on any sheet, so sorting, deleting rows or renaming a sheet cannot shift
an answer onto the wrong change; an id that disappeared is reported, never guessed.

Branding: with the organisation's reporting package (ane_package, found via WORK_FOLDER_ROOT, a parent
folder or the current folder) the workbook gets the IPPF formats, logo and pillar footer. Without it
(e.g. Cowork) the colours and font come from brand_fallback.json and there is no logo.
"""
import json
import os
import sys
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

import xlsxwriter
from openpyxl import load_workbook

HERE = Path(__file__).parent
CORRECT, WRONG, NOT_SURE = "Correct", "Wrong: right value in next column", "Not sure"
CHOICES = [CORRECT, WRONG, NOT_SURE]
REVIEWER_CELL, DATE_CELL = "B6", "B7"
IDS_SHEET = "_ids"
COLUMNS = ["What changed", "Country", "Last edition", "New value", "Look here", "What correct looks like",
           "Your answer", "Right value", "change_ids"]
WIDTHS = [48, 14, 22, 22, 30, 44, 30, 18, 12]
DETAIL = ["change_id", "kind", "country", "indicator", "year", "last edition", "new value", "sheet", "link",
          "guidance"]
UNTESTED = "not tested here (sandbox blocks this site)"
GLOSSARY = {
    "Register": "The table of every value the map shows, with who checked it and when.",
    "Edition": "One year's version of the register. A new edition never changes the previous one.",
    "Drop-in file": "A file someone saved into the drop_in folder for this refresh (for example a DHIS2 export).",
    "Tick": "A person's name and date on a row, saying they compared the value with its source.",
    "Change": "A value that is new, different, or no longer reported compared with the last edition.",
    "Reporting year": "The year the data describe.",
}


@dataclass
class Answer:
    choice: str
    corrected_value: str


# ---------------------------------------------------------------- branding
def brand_package():
    """Return (excel_native, plain_language, IPPF_FORMAT_TEMPLATE) when ane_package can be imported, else None."""
    try:
        import ane_package  # noqa: F401
    except ModuleNotFoundError:
        cands = [Path(os.environ["WORK_FOLDER_ROOT"])] if os.environ.get("WORK_FOLDER_ROOT") else []
        cands += list(HERE.resolve().parents) + [Path.cwd()]
        root = next((c for c in cands if (c / "ane_package" / "reporting" / "brand.py").is_file()), None)
        if root is None:
            return None
        sys.path.insert(0, str(root))
    try:
        from ane_package.reporting import excel_native, plain_language
        from ane_package.reporting.brand import IPPF_FORMAT_TEMPLATE
    except Exception:  # noqa: BLE001 - any import failure means: use the fallback
        return None
    return excel_native, plain_language, IPPF_FORMAT_TEMPLATE


def _brand(pkg):
    if pkg:
        t = pkg[2]
        return {"colours": t["colours"], "font": t["fonts"]["default"]}
    return json.loads((HERE / "brand_fallback.json").read_text(encoding="utf-8"))


def _formats(wb, pkg, brand):
    c, f = brand["colours"], brand["font"]
    base = {"font_name": f["name"], "font_size": f["size"]}
    cell = {**base, "border": 1, "border_color": c["platinum"], "valign": "top", "text_wrap": True}
    fm = pkg[0].apply_ippf_formatting(wb, pkg[2]) if pkg else {
        "chart_title": wb.add_format({**base, "bold": True, "font_size": 12, "font_color": c["dream"]}),
        "table_header": wb.add_format({**base, "bold": True, "font_color": c["white"], "bg_color": c["dream"],
                                       "border": 1, "border_color": c["platinum"], "valign": "vcenter"}),
    }
    fm["header"] = wb.add_format({**base, "bold": True, "font_color": c["white"], "bg_color": c["dream"],
                                  "border": 1, "border_color": c["platinum"], "valign": "vcenter", "text_wrap": True})
    fm["cell"] = wb.add_format(cell)
    fm["link"] = wb.add_format({**cell, "font_color": c["dream"], "underline": 1})
    fm["input"] = wb.add_format({**cell, "bg_color": "#FFFFFF", "bold": True, "border_color": c["fire_red"]})
    fm["input_date"] = wb.add_format({**cell, "bold": True, "border_color": c["fire_red"], "num_format": "dd.mm.yyyy"})
    fm["text"] = wb.add_format({**base, "text_wrap": True, "valign": "top"})
    fm["title"] = fm["chart_title"]
    return fm


def _brand_sheet(ws, pkg):
    if pkg:
        pkg[0].add_brand_header(ws, floating_logo=False)


# ---------------------------------------------------------------- links
def http_head(url, timeout=10):
    """True when the web page answers a HEAD request; False when it cannot be reached from here."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 - http(s) only, checked by caller
            return r.status < 400  # caller passes http(s) only
    except Exception:  # noqa: BLE001
        return False


def _link(raw, cache):
    """Return (url for xlsxwriter or None, label, extra guidance) for one link string."""
    raw = (raw or "").strip()
    if not raw:
        return None, "no link: ask the person who ran the refresh", ""
    scheme = urlparse(raw).scheme.lower()
    if scheme in ("http", "https"):
        if raw not in cache:
            cache[raw] = http_head(raw)
        return raw, "Open the web page" + ("" if cache[raw] else f": {UNTESTED}"), ""
    path, _, anchor = raw.partition("#")
    path = url2pathname(urlparse(path).path) if scheme == "file" else unquote(path)
    p = Path(path)
    if p not in cache:
        cache[p] = p.exists()
    if anchor and "!" not in anchor:
        anchor += "!A1"
    url = "external:" + str(p) + (f"#{anchor}" if anchor else "")
    if not cache[p]:
        return url, f"File not found when this workbook was made: {p.name}", ""
    if anchor:
        return url, f"Open {p.name}, sheet {anchor.split('!')[0].strip(chr(39))}", ""
    extra = " Filter the file to {codes}." if p.suffix.lower() == ".csv" else ""
    return url, f"Open {p.name}", extra


# ---------------------------------------------------------------- write
def _shown(r):
    if not r:
        return "-"
    return r.get("value_display") or r.get("value") or "-"


def _codes(cs):
    codes = sorted({x for c in cs for x in ((c.new or c.old or {}).get("ma_code") or "").split(";") if x})
    if codes:
        return "the organisation code(s) " + "; ".join(codes)
    return "the row(s) of " + ", ".join(sorted({c.iso3 for c in cs}))


def _write_lines(ws, lines, by_id, fm, cache):
    for i, h in enumerate(COLUMNS):
        ws.write(0, i, h, fm["header"])
        ws.set_column(i, i, WIDTHS[i], None, {"hidden": h == "change_ids"})
    ws.freeze_panes(1, 0)
    for r, line in enumerate(lines, start=1):
        cs = [by_id[i] for i in line.change_ids]
        one = len(cs) == 1
        url, label, extra = _link(line.link, cache)
        vals = [line.title, ", ".join(sorted({c.iso3 for c in cs})),
                _shown(cs[0].old) if one else "see Detail sheet", _shown(cs[0].new) if one else "see Detail sheet"]
        for col, v in enumerate(vals):
            ws.write_string(r, col, v, fm["cell"])
        if url:
            ws.write_url(r, 4, url, fm["link"], string=label)
        else:
            ws.write_string(r, 4, label, fm["cell"])
        ws.write_string(r, 5, line.guidance + extra.format(codes=_codes(cs)), fm["cell"])
        ws.write_blank(r, 6, None, fm["input"])
        ws.write_blank(r, 7, None, fm["input"])
        ws.write_string(r, 8, ";".join(line.change_ids), fm["cell"])
    if lines:
        ws.data_validation(1, 6, len(lines), 6, {
            "validate": "list", "source": CHOICES,
            "error_title": "Choose an answer", "error_message": "Pick one of the three answers in the list."})
    ws.autofilter(0, 0, max(len(lines), 1), len(COLUMNS) - 1)


def write_workbook(lines, changes, out, edition, reporting_year, notes=(), run_digest=""):
    """Write the review workbook for one refresh run and return its path.

    notes = plain lines a person must see that are not changes (unknown organisation code, a stream
    name with no crosswalk row, a file not dropped in); listed on 'How to use' under row 10.
    """
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pkg = brand_package()
    wb = xlsxwriter.Workbook(str(out))
    fm = _formats(wb, pkg, _brand(pkg))
    by_id = {c.change_id: c for c in changes}
    cache = {}
    must = [l for l in lines if l.sheet == "Must check"]
    opt = [l for l in lines if l.sheet != "Must check"]

    how = wb.add_worksheet("How to use")
    how.set_column(0, 0, 22)
    how.set_column(1, 1, 90)
    how.write(0, 0, f"Map register {edition}: check the changes found in the {reporting_year} files", fm["title"])
    steps = ["1. On the 'Must check' sheet, open the link in 'Look here' for each line.",
             "2. Compare what you see there with 'New value' and 'What correct looks like'.",
             f"3. Choose an answer in 'Your answer'. If you choose '{WRONG}', type the right value next to it. "
             "'Optional' holds more lines if you have time."]
    for i, s in enumerate(steps, start=1):
        how.write(i, 0, s, fm["text"])
    how.write(5, 0, "Reviewer", fm["header"])
    how.write_blank(5, 1, None, fm["input"])
    how.write(6, 0, "Date answered", fm["header"])
    how.write_blank(6, 1, None, fm["input_date"])
    wb.define_name("Reviewer", f"='How to use'!${REVIEWER_CELL[0]}${REVIEWER_CELL[1:]}")
    wb.define_name("DateAnswered", f"='How to use'!${DATE_CELL[0]}${DATE_CELL[1:]}")
    how.write(8, 0, f"{len(must)} line(s) on Must check, {len(opt)} on Optional, {len(changes)} change(s) in all.",
              fm["text"])
    if notes:
        how.write(10, 0, "Also tell the map owner about these (not changes, so no answer is needed):", fm["header"])
        for i, n in enumerate(notes, start=11):
            how.write_string(i, 0, f"- {n}", fm["text"])
    _brand_sheet(how, pkg)

    for name, ls in (("Must check", must), ("Optional", opt)):
        ws = wb.add_worksheet(name)
        _write_lines(ws, ls, by_id, fm, cache)
        _brand_sheet(ws, pkg)

    det = wb.add_worksheet("Detail")
    sheet_of = {i: l.sheet for l in lines for i in l.change_ids}
    for i, h in enumerate(DETAIL):
        det.write(0, i, h, fm["header"])
        det.set_column(i, i, 40 if h in ("link", "guidance") else 16)
    det.freeze_panes(1, 0)
    for r, c in enumerate(changes, start=1):
        vals = [c.change_id, c.kind, c.iso3, c.indicator_id, str(c.reference_year), _shown(c.old), _shown(c.new),
                sheet_of.get(c.change_id, ""), c.link, c.guidance]
        for col, v in enumerate(vals):
            det.write_string(r, col, v, fm["cell"])
    det.autofilter(0, 0, max(len(changes), 1), len(DETAIL) - 1)
    _brand_sheet(det, pkg)

    if pkg:
        pkg[1].add_glossary_sheet(wb, list(GLOSSARY), glossary=GLOSSARY, template=pkg[2],
                                  intro="Words used in this workbook, in everyday language.")
    else:
        g = wb.add_worksheet("Glossary")
        g.set_column(0, 0, 22)
        g.set_column(1, 1, 90)
        g.write(0, 0, "Term", fm["header"])
        g.write(0, 1, "Plain-language explanation", fm["header"])
        for r, (t, d) in enumerate(GLOSSARY.items(), start=1):
            g.write(r, 0, t, fm["cell"])
            g.write(r, 1, d, fm["cell"])

    ids = wb.add_worksheet(IDS_SHEET)
    for r, c in enumerate(changes):
        ids.write_string(r, 0, c.change_id)
    ids.write_string(0, 1, run_digest)
    ids.very_hidden()
    _brand_sheet(ids, pkg)
    wb.close()
    return out


# ---------------------------------------------------------------- read
def _iso(v):
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    s = str(v or "").strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            pass
    return s


def _named(wb, name, fallback_cell):
    dn = wb.defined_names.get(name)
    if dn is not None:
        for sheet, ref in dn.destinations:
            if sheet in wb.sheetnames:
                return wb[sheet][ref.replace("$", "")].value
    return wb["How to use"][fallback_cell].value if "How to use" in wb.sheetnames else None


def read_answers(path):
    """Return (header {reviewer, date, ids, run_digest}, {change_id: Answer}, problems).

    ids = the hidden id list the workbook was written with; run_digest = the fingerprint of the review run
    it was written from (apply refuses it when that run has changed since). 'Wrong' on a line that stands
    for several changes is a problem and leaves them unanswered: one value cannot be right for each.
    """
    wb = load_workbook(path, data_only=True)
    header = {"reviewer": str(_named(wb, "Reviewer", REVIEWER_CELL) or "").strip(),
              "date": _iso(_named(wb, "DateAnswered", DATE_CELL))}
    problems, answers = [], {}
    expected = [str(r[0]) for r in wb[IDS_SHEET].iter_rows(values_only=True) if r and r[0]] \
        if IDS_SHEET in wb.sheetnames else []
    header["ids"] = expected
    header["run_digest"] = str(wb[IDS_SHEET]["B1"].value or "").strip() if IDS_SHEET in wb.sheetnames else ""
    if not expected:
        problems.append("the workbook's hidden id list is gone; it cannot be applied. Run review again.")
    for ws in wb.worksheets:
        if ws.title == IDS_SHEET or ws.max_row < 1:
            continue
        hdr = [str(c.value or "").strip() for c in ws[1]]
        if not {"change_ids", "Your answer", "Right value"} <= set(hdr):
            continue
        ci, ai, vi = hdr.index("change_ids"), hdr.index("Your answer"), hdr.index("Right value")
        for r in ws.iter_rows(min_row=2, values_only=True):
            ids = [x for x in str(r[ci] or "").split(";") if x.strip()]
            if not ids:
                continue
            choice = str(r[ai] or "").strip()
            value = "" if r[vi] is None else str(r[vi]).strip()
            if choice and choice not in CHOICES:
                problems.append(f"{', '.join(ids)}: answer '{choice}' is not one of the three in the list; "
                                "treated as unanswered")
                choice = ""
            if choice == WRONG and len(ids) > 1:
                problems.append(f"{', '.join(ids)}: '{WRONG}' chosen on a line that stands for several changes; "
                                "one right value cannot fit each of them, so they stay unanswered. Tell the map "
                                "owner which value is wrong")
                choice = ""
            if choice == WRONG and not value:
                problems.append(f"{', '.join(ids)}: '{WRONG}' chosen but the Right value cell is empty; "
                                "treated as unanswered")
                choice = ""
            for i in ids:
                a = Answer(choice, value if choice == WRONG else "")
                if i in answers and answers[i] != a:
                    problems.append(f"{i}: answered twice with different answers; treated as unanswered")
                    a = Answer("", "")
                answers[i] = a
    for i in expected:
        if i not in answers:
            problems.append(f"change {i} is not in the workbook any more (row deleted?); it stays unticked")
    for i in answers:
        if expected and i not in expected:
            problems.append(f"change {i} is not one this workbook was written with; ignored")
    answers = {i: a for i, a in answers.items() if not expected or i in expected}
    return header, answers, problems
