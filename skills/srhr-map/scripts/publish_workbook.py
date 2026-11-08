"""Write the map's data workbook for one edition (SRHR map skill, phase d, publish step).

    python publish_workbook.py --register <map_register_<edition>.csv> --sources <source_register.csv>
                               --master <master_countries.csv> --out <publish folder>/map_data_<edition>.xlsx
                               [--edition <edition>]

Sheets:
  About     plain method note, edition, data years and counts, all computed from the register
  Values    one row per register row: country, indicator in plain words, value, how the map shows it,
            source, source link, reference year, confirmed yes / not yet confirmed, by, date
  Glossary  plain-language terms
Rows nobody has ticked yet are listed and marked "not yet confirmed", not dropped, because the decks
show them too. A source with no web page gets the words "no web link", never an empty link.

The target is never overwritten: if the file exists the script stops (exit 2) and names it, because
once a person edits a published workbook a fresh build would erase their edits. Exit 1 = input error.
Branding comes from review_workbook (the organisation's reporting package, or brand_fallback.json).
"""
import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

import xlsxwriter

import review_workbook as rw

REGISTER_FIELDS = ["iso3", "ma_code", "member_status", "topic", "indicator_id", "value", "value_display", "unit",
                   "reference_year", "source_id", "date_read", "machine_check", "ticked_by", "tick_date",
                   "snapshot_tag"]
VALUE_COLUMNS = ["Country", "Indicator", "Value", "Shown on the map as", "Source", "Source link",
                 "Reference year", "Confirmed", "Confirmed by", "Date confirmed"]
WIDTHS = [18, 40, 14, 22, 34, 24, 12, 18, 18, 14]
NO_LINK = "no web link"
OPEN_LINK = "Open the source page"
NOT_CONFIRMED = "not yet confirmed"
INTERNAL = "Internal source: "
PLAIN = {
    "ecdc_hiv_diagnosis_rate": "HIV diagnosis rate",
    "ippf_bp_hiv_focus": "HIV as a focus in the business plan",
    "ippf_funding_streams": "Grant streams held",
    "ippf_funding_streams_partner": "Grant streams held as a partner",
    "ippf_grant_streams_count": "Number of grant streams",
    "ippf_hiv_services": "HIV services reported",
    "ippf_membership": "Membership status",
}
TITLE = "SRHR map data, edition {edition}"
ABOUT_TEMPLATES = [
    "What this is: every value shown on the edition {edition} maps, one row per value, with the source it was "
    "read from.",
    "Data years: {first} to {last}.",
    "Values: {n}. Confirmed by a person against the source: {k}. Not yet confirmed: {u}.",
    "How the values were checked: a person opened the source named in each row, compared the value, and ticked "
    "the row with their name and the date. Rows without a tick are listed too, because the maps show them. "
    "Treat them as provisional.",
    "Links: where a source has a web page, the 'Source link' column opens it. Internal files have no web page "
    "and show 'no web link'.",
    "Made on {made_on} from the map register.",
]
GLOSSARY = {
    "Register": "The table of every value the map shows, with who checked it and when.",
    "Edition": "One year's version of the maps and their register. A new edition never changes an old one.",
    "Reference year": "The year the value describes, which can be earlier than the edition.",
    "Shown on the map as": "The words or number a reader sees on the map for this value.",
    "Confirmed": "A person compared the value with its source and put their name and date on the row.",
    "Not yet confirmed": "Nobody has compared this value with its source yet. Treat it as provisional.",
}


class Stop(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def made_on():
    return date.today().isoformat()


def _read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def plain_indicator(indicator_id, unit):
    name = PLAIN.get(indicator_id) or indicator_id.replace("_", " ").strip()
    unit = (unit or "").strip()
    if unit and unit.lower() not in name.lower():
        name += f" ({unit})"
    return name


def source_of(source_id, sources):
    """Return (label, url or '') for one register source_id."""
    s = sources.get(source_id)
    if s:
        label = s.get("source", "").strip() or source_id
        pub = (s.get("publisher") or "").strip()
        if pub and pub.lower() not in label.lower():
            label += f" ({pub})"
        return label, (s.get("url") or "").strip()
    if source_id.startswith("ippf_"):
        return INTERNAL + source_id[len("ippf_"):].replace("_", " "), ""
    return source_id, ""


def value_rows(register, sources, countries):
    """One dict per register row, keys = VALUE_COLUMNS plus '_url'; sorted country, indicator, year."""
    out = []
    for r in register:
        label, url = source_of(r.get("source_id", "").strip(), sources)
        ticked = bool((r.get("ticked_by") or "").strip())
        value = (r.get("value") or "").strip()
        out.append({
            "Country": countries.get(r["iso3"], r["iso3"]),
            "Indicator": plain_indicator(r.get("indicator_id", ""), r.get("unit", "")),
            "Value": value,
            "Shown on the map as": (r.get("value_display") or "").strip() or value,
            "Source": label,
            "Source link": url,
            "Reference year": (r.get("reference_year") or "").strip(),
            "Confirmed": "yes" if ticked else NOT_CONFIRMED,
            "Confirmed by": (r.get("ticked_by") or "").strip(),
            "Date confirmed": (r.get("tick_date") or "").strip(),
            "_url": url,
        })
    return sorted(out, key=lambda v: (v["Country"], v["Indicator"], v["Reference year"]))


def about_lines(edition, rows):
    years = sorted({v["Reference year"] for v in rows if v["Reference year"]})
    k = sum(1 for v in rows if v["Confirmed"] == "yes")
    f = {"edition": edition, "first": years[0] if years else "-", "last": years[-1] if years else "-",
         "n": len(rows), "k": k, "u": len(rows) - k, "made_on": made_on()}
    return TITLE.format(**f), [t.format(**f) for t in ABOUT_TEMPLATES]


def write(out, edition, rows):
    pkg = rw.brand_package()
    if pkg is None:
        print("note: the organisation's reporting package was not found; the workbook has the brand colours "
              "but no logo, and the brand checker will flag it")
    out.parent.mkdir(parents=True, exist_ok=True)
    wb = xlsxwriter.Workbook(str(out))
    fm = rw._formats(wb, pkg, rw._brand(pkg))

    about = wb.add_worksheet("About")
    about.set_column(0, 0, 110)
    title, lines = about_lines(edition, rows)
    about.write_string(0, 0, title, fm["title"])
    for i, s in enumerate(lines, start=2):
        about.write_string(i, 0, s, fm["text"])
    rw._brand_sheet(about, pkg)

    ws = wb.add_worksheet("Values")
    ws.add_table(0, 0, len(rows), len(VALUE_COLUMNS) - 1, {
        "name": "MapValues", "style": None, "autofilter": True,
        "columns": [{"header": h, "header_format": fm["header"]} for h in VALUE_COLUMNS]})
    for i, w in enumerate(WIDTHS):
        ws.set_column(i, i, w)
    ws.freeze_panes(1, 0)
    link_col = VALUE_COLUMNS.index("Source link")
    for r, v in enumerate(rows, start=1):
        for c, h in enumerate(VALUE_COLUMNS):
            if c == link_col:
                if v["_url"]:
                    ws.write_url(r, c, v["_url"], fm["link"], string=OPEN_LINK)
                else:
                    ws.write_string(r, c, NO_LINK, fm["cell"])
            else:
                ws.write_string(r, c, str(v[h]), fm["cell"])
    rw._brand_sheet(ws, pkg)

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
    wb.close()
    return out


def refuse_existing(*targets):
    """Stop (exit 2) before anything is written when any target file already exists."""
    for out in map(Path, targets):
        if out.exists():
            raise Stop(2, f"stop: {out.name} already exists in {out.parent}. It is never overwritten, because a "
                          "person may have edited it. Move or rename it first if a new build is really wanted.")


def load_inputs(register_path, sources_path, master_path, edition=None):
    """Return (register rows, sources by id, country name by iso3, edition); Stop(1) on bad input."""
    register = _read(register_path)
    if not register:
        raise Stop(1, f"stop: the register {Path(register_path).name} has no rows")
    missing = [f for f in ("iso3", "indicator_id", "value", "reference_year", "source_id", "ticked_by")
               if f not in register[0]]
    if missing:
        raise Stop(1, f"stop: the register lacks column(s) {', '.join(missing)}")
    if edition is None:
        m = re.search(r"(\d{4})", Path(register_path).stem)
        if not m:
            raise Stop(1, "stop: no edition in the register file name; pass --edition")
        edition = m.group(1)
    sources = {s["source_id"]: s for s in _read(sources_path)} if sources_path else {}
    countries = {c["iso3"]: c["country"] for c in _read(master_path)} if master_path else {}
    return register, sources, countries, edition


def build(register_path, sources_path, master_path, out, edition=None):
    refuse_existing(out)
    register, sources, countries, edition = load_inputs(register_path, sources_path, master_path, edition)
    return write(Path(out), edition, value_rows(register, sources, countries))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--register", required=True)
    ap.add_argument("--sources", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--edition")
    a = ap.parse_args(argv)
    try:
        out = build(a.register, a.sources, a.master, a.out, a.edition)
    except Stop as e:
        print(str(e), file=sys.stderr)
        return e.code
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
