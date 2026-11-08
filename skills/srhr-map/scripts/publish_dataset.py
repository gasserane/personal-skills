"""Write the map's Power BI dataset for one edition (SRHR map skill, phase d, publish step).

    python publish_dataset.py --register <map_register_<edition>.csv> --sources <source_register.csv>
                              --master <master_countries.csv> --out-dir <publish folder>/<edition>
                              [--edition <edition>]

Writes powerbi_dataset_<edition>.csv (UTF-8 with BOM, which Power BI Desktop reads without asking)
and powerbi_dataset_<edition>.xlsx (the same table, branded, with a glossary of the columns).
Long format: one row per register row (country x indicator x year). Country only: no member
association code or name, because shared summary views leave out data that identifies an
association. Its keys (iso3, topic, reference_year) match the mapping evidence register, so the
two can be joined in Power BI.

value_number holds the value when it is a number and is blank otherwise, because the register mixes
numbers and categories and Power BI types a mixed column as text.

Neither file is ever overwritten: if either exists the script stops (exit 2), names it and writes
nothing. Exit 1 = input error.
"""
import argparse
import csv
import math
import sys
from pathlib import Path

import xlsxwriter

import publish_workbook as pw
import review_workbook as rw

DATA_SHEET = "Data"
DATASET_COLUMNS = ["edition", "iso3", "country", "topic", "indicator_id", "indicator", "value", "value_number",
                   "value_display", "unit", "reference_year", "source_id", "source", "source_url", "confirmed",
                   "confirmed_by", "date_confirmed"]
GLOSSARY = {
    "edition": "The year of the maps this row belongs to.",
    "iso3": "Three-letter country code. Use it to join this table with other country tables.",
    "country": "Country name.",
    "topic": "Map topic the value belongs to.",
    "indicator_id": "Short code of the indicator, the same in every edition.",
    "indicator": "The indicator in plain words, with its unit.",
    "value": "The value as stored in the register: a number or a category.",
    "value_number": "The value as a number, for sums and averages. Blank when the value is a category.",
    "value_display": "The words or number a reader sees on the map.",
    "unit": "Unit of the value, where it has one.",
    "reference_year": "The year the value describes, which can be earlier than the edition.",
    "source_id": "Short code of the source.",
    "source": "The source the value was read from.",
    "source_url": "Web page of the source. Blank for internal files with no web page.",
    "confirmed": "'yes' when a person compared the value with its source; otherwise 'not yet confirmed'.",
    "confirmed_by": "Who confirmed the value.",
    "date_confirmed": "When the value was confirmed.",
}


def as_number(value):
    """Return the value as int or float when it is a plain finite number, else None."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(f):
        return None
    return int(f) if f.is_integer() and "." not in value else f


def dataset_rows(register, sources, countries, edition):
    out = []
    for r in sorted(register, key=lambda r: (r["iso3"], r.get("indicator_id", ""), r.get("reference_year", ""))):
        label, url = pw.source_of(r.get("source_id", "").strip(), sources)
        value = (r.get("value") or "").strip()
        ticked = bool((r.get("ticked_by") or "").strip())
        out.append({
            "edition": edition, "iso3": r["iso3"], "country": countries.get(r["iso3"], r["iso3"]),
            "topic": (r.get("topic") or "").strip(), "indicator_id": (r.get("indicator_id") or "").strip(),
            "indicator": pw.plain_indicator(r.get("indicator_id", ""), r.get("unit", "")),
            "value": value, "value_number": as_number(value),
            "value_display": (r.get("value_display") or "").strip() or value,
            "unit": (r.get("unit") or "").strip(), "reference_year": (r.get("reference_year") or "").strip(),
            "source_id": (r.get("source_id") or "").strip(), "source": label, "source_url": url,
            "confirmed": "yes" if ticked else pw.NOT_CONFIRMED,
            "confirmed_by": (r.get("ticked_by") or "").strip(), "date_confirmed": (r.get("tick_date") or "").strip(),
        })
    return out


def _csv_cell(v):
    return "" if v is None else str(v)


def write_csv(path, rows, fh=None):
    """Write the csv to path, or into fh (a text file `claimed` opened for path) when given."""
    if fh is None:
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            return write_csv(path, rows, f)
    w = csv.writer(fh, lineterminator="\r\n")
    w.writerow(DATASET_COLUMNS)
    for r in rows:
        w.writerow([_csv_cell(r[h]) for h in DATASET_COLUMNS])
    return path


def write_xlsx(path, rows, fh=None):
    pkg = rw.brand_package()
    if pkg is None:
        print("note: the organisation's reporting package was not found; the workbook has the brand colours "
              "but no logo, and the brand checker will flag it")
    wb = xlsxwriter.Workbook(fh if fh is not None else str(path))
    fm = rw._formats(wb, pkg, rw._brand(pkg))
    num = wb.add_format({**{"font_name": rw._brand(pkg)["font"]["name"], "font_size": rw._brand(pkg)["font"]["size"]},
                         "border": 1, "border_color": rw._brand(pkg)["colours"]["platinum"], "valign": "top"})
    ws = wb.add_worksheet(DATA_SHEET)
    ws.add_table(0, 0, max(len(rows), 1), len(DATASET_COLUMNS) - 1, {
        "name": "MapDataset", "style": None, "autofilter": True,
        "columns": [{"header": h, "header_format": fm["header"]} for h in DATASET_COLUMNS]})
    for i, h in enumerate(DATASET_COLUMNS):
        ws.set_column(i, i, 30 if h in ("indicator", "source", "source_url") else 14)
    ws.freeze_panes(1, 0)
    for r, row in enumerate(rows, start=1):
        for c, h in enumerate(DATASET_COLUMNS):
            v = row[h]
            if h == "value_number" and v is not None:
                ws.write_number(r, c, v, num)
            else:
                ws.write_string(r, c, _csv_cell(v), fm["cell"])
    rw._brand_sheet(ws, pkg)
    if pkg:
        pkg[1].add_glossary_sheet(wb, list(GLOSSARY), glossary=GLOSSARY, template=pkg[2],
                                  intro="The columns of this table, in everyday language.")
    else:
        g = wb.add_worksheet("Glossary")
        g.set_column(0, 0, 22)
        g.set_column(1, 1, 90)
        g.write(0, 0, "Term", fm["header"])
        g.write(0, 1, "Plain-language explanation", fm["header"])
        for r, (t, d) in enumerate(GLOSSARY.items(), start=1):
            g.write(r, 0, t, fm["cell"])
            g.write(r, 1, d, fm["cell"])
    wb.close()
    return path


def build(register_path, sources_path, master_path, out_dir, edition=None):
    register, sources, countries, edition = pw.load_inputs(register_path, sources_path, master_path, edition)
    out_dir = Path(out_dir)
    c, x = out_dir / f"powerbi_dataset_{edition}.csv", out_dir / f"powerbi_dataset_{edition}.xlsx"
    pw.refuse_existing(c, x)
    rows = dataset_rows(register, sources, countries, edition)
    # both targets are claimed before either is written: if the xlsx cannot be claimed, the csv is removed
    with pw.claimed(c, encoding="utf-8-sig", newline="") as fc, pw.claimed(x, binary=True) as fx:
        return write_csv(c, rows, fc), write_xlsx(x, rows, fx)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--register", required=True)
    ap.add_argument("--sources", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--edition")
    a = ap.parse_args(argv)
    try:
        paths = build(a.register, a.sources, a.master, a.out_dir, a.edition)
    except pw.Stop as e:
        print(str(e), file=sys.stderr)
        return e.code
    for p in paths:
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
