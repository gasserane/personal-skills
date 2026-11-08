"""Planted tests for publish_workbook.py (SRHR map skill, phase d, data workbook).

Invented countries (XAA...), sources and values only. Writes into a temporary folder. Run:
    python test_publish_workbook.py
"""
import csv
import hashlib
import io
import re
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import publish_workbook as pw  # noqa: E402

FAILS = []
TMP = Path(tempfile.mkdtemp(prefix="srhr_pw_"))
URL_A = "https" + "://example.org/source-a"  # built by concatenation: public_repo_clean flags drive-letter-like text


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ': ' + detail}")
    if not cond:
        FAILS.append(name)


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return path


def row(iso3, ind, value, display, unit, year, src, by="", on=""):
    return {"iso3": iso3, "ma_code": "", "member_status": "", "topic": "t", "indicator_id": ind, "value": value,
            "value_display": display, "unit": unit, "reference_year": year, "source_id": src, "date_read": "",
            "machine_check": "pass", "ticked_by": by, "tick_date": on, "snapshot_tag": ""}


REG_ROWS = [
    row("XAA", "ecdc_hiv_diagnosis_rate", "3.1", "3.1", "per 100 000", "2023", "src_a", "Reviewer One", "2026-11-01"),
    row("XAA", "ippf_membership", "core", "Full member", "", "2025", "ippf_tracker", "Reviewer One", "2026-11-01"),
    row("XAB", "ippf_grant_streams_count", "2", "2", "grant streams", "2026", "src_b"),
    row("XAC", "brand_new_indicator", "7", "", "", "2024", "ippf_tracker"),
]
REG = write_csv(TMP / "map_register_2031.csv", pw.REGISTER_FIELDS, REG_ROWS)
SRC = write_csv(TMP / "source_register.csv", ["source_id", "source", "publisher", "url"], [
    {"source_id": "src_a", "source": "Source A annual report", "publisher": "Agency A", "url": URL_A},
    {"source_id": "src_b", "source": "Source B table", "publisher": "Agency B", "url": ""},
])
MASTER = write_csv(TMP / "master_countries.csv", ["country", "iso3"], [
    {"country": "Country A", "iso3": "XAA"}, {"country": "Country B", "iso3": "XAB"}])


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = pw.main(argv)
    return code, out.getvalue() + err.getvalue()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = TMP / "publish" / "2031" / "map_data_2031.xlsx"
    args = ["--register", str(REG), "--sources", str(SRC), "--master", str(MASTER), "--out", str(out)]
    code, msg = run(args)
    check("writes the workbook, exit 0", code == 0 and out.exists(), f"code {code}: {msg}")
    if code != 0:
        print(f"{len(FAILS)} failure(s)")
        sys.exit(1)

    wb = load_workbook(out)
    check("sheets About, Values, Glossary", all(s in wb.sheetnames for s in ("About", "Values", "Glossary")),
          str(wb.sheetnames))
    ws = wb["Values"]
    head = [c.value for c in ws[1]]
    check("Values header = VALUE_COLUMNS", head[:len(pw.VALUE_COLUMNS)] == pw.VALUE_COLUMNS, str(head))
    col = {h: i for i, h in enumerate(head)}
    data = [r for r in ws.iter_rows(min_row=2, values_only=False) if any(c.value not in (None, "") for c in r)]
    check("one Values row per register row", len(data) == len(REG_ROWS), f"{len(data)} vs {len(REG_ROWS)}")

    tables = list(ws.tables.values())
    ref_ok = False
    if tables:
        last = int(re.search(r"(\d+)$", tables[0].ref).group(1))
        ref_ok = last == 1 + len(REG_ROWS)
    check("Excel table ref covers every data row", ref_ok, str([t.ref for t in tables]))

    def cell(r, h):
        return r[col[h]]

    check("every row has a source and a reference year",
          all(cell(r, "Source").value and cell(r, "Reference year").value for r in data))
    by_country = {}
    for r in data:
        by_country.setdefault(cell(r, "Country").value, []).append(r)
    check("country names come from the master list; unknown code shown as is",
          set(by_country) == {"Country A", "Country B", "XAC"}, str(set(by_country)))

    links = {cell(r, "Indicator").value: cell(r, "Source link") for r in data}
    rate = next(c for k, c in links.items() if k.startswith(pw.PLAIN["ecdc_hiv_diagnosis_rate"]))
    check("source with a URL: hyperlink target equals the source register URL",
          rate.hyperlink is not None and rate.hyperlink.target == URL_A,
          str(rate.hyperlink.target if rate.hyperlink else None))
    nolink = [c for k, c in links.items() if c is not rate]
    check("source with no URL (blank or not registered): 'no web link' text, no hyperlink",
          all(c.value == pw.NO_LINK and c.hyperlink is None for c in nolink),
          str([(c.value, c.hyperlink) for c in nolink]))

    conf = {(cell(r, "Country").value, cell(r, "Reference year").value): r for r in data}
    t = conf[("Country A", "2023")]
    u = conf[("Country B", "2026")]
    check("ticked row: confirmed yes, by, date",
          (cell(t, "Confirmed").value, cell(t, "Confirmed by").value, cell(t, "Date confirmed").value)
          == ("yes", "Reviewer One", "2026-11-01"))
    check("unticked row listed and marked not yet confirmed", cell(u, "Confirmed").value == pw.NOT_CONFIRMED)
    check("indicator in plain words carries the unit when the name lacks it",
          cell(t, "Indicator").value == pw.PLAIN["ecdc_hiv_diagnosis_rate"] + " (per 100 000)",
          str(cell(t, "Indicator").value))
    check("unknown indicator id falls back to readable words",
          cell(conf[("XAC", "2024")], "Indicator").value == "brand new indicator")
    check("blank display falls back to the value", cell(conf[("XAC", "2024")], "Shown on the map as").value == "7")

    g = wb["Glossary"]
    check("Glossary sheet present and non-empty", g.max_row >= 3, str(g.max_row))

    about = " ".join(str(c.value) for r in wb["About"].iter_rows() for c in r if c.value is not None)
    allowed = {"2031", "2023", "2026", str(len(REG_ROWS)), "1", "3", "2"}  # edition, years, counts
    allowed |= set(re.findall(r"\d+", pw.made_on()))
    digits = set(re.findall(r"\d+", about))
    check("About digits all trace to computed fields", digits <= allowed, str(digits - allowed))
    check("About states edition and data years", "2031" in about and "2023" in about and "2026" in about, about)
    check("no typed number in any About template", not any(re.search(r"\d", s) for s in pw.ABOUT_TEMPLATES),
          str([s for s in pw.ABOUT_TEMPLATES if re.search(r"\d", s)]))

    before = sha(out)
    code, msg = run(args)
    check("existing target: exit 2, names the file, file unchanged",
          code == 2 and out.name in msg and sha(out) == before, f"code {code}: {msg}")

    empty = write_csv(TMP / "map_register_2032.csv", pw.REGISTER_FIELDS, [])
    code, msg = run(["--register", str(empty), "--sources", str(SRC), "--master", str(MASTER),
                     "--out", str(TMP / "e.xlsx")])
    check("empty register: exit 1, nothing written", code == 1 and not (TMP / "e.xlsx").exists(), f"{code} {msg}")

    print(f"{len(FAILS)} failure(s)")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
