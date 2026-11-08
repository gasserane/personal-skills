"""Write the summary web map for donors and partners (SRHR map skill, phase e).

One self-contained page with a computed headline ("N of the M countries of the WHO European Region")
and three maps: membership (A), funding in three bands (F) and new HIV diagnoses (D). It holds no
stream name, member association name or ma_code, and no hover text from a deck ScreenTip: every
string comes from the templates in this file and the register values. Geometry, the embedded d3 and
the page frame are reused from publish_webmap.py. Exit 1 = input error, exit 2 = the target exists.
"""
import csv
import html
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import json  # noqa: E402
import computed  # noqa: E402
import publish_webmap as pw  # noqa: E402
import register_deck_check as rdc  # noqa: E402
from publish_workbook import Stop  # noqa: E402

PAGE_TITLE = "IPPF across Europe, {edition}"
NAMES = {"A": "Members and partners", "F": "IPPF funding", "D": "New HIV diagnoses"}
TITLES = {"A": "IPPF members and partners, {year}", "F": "IPPF funding to members, {year}",
          "D": "New HIV diagnoses, {year}"}
SUBTITLES = {"A": "Countries where an IPPF member association or collaborative partner is based",
             "F": "Countries by the IPPF grants their member or partner receives",
             "D": "Rate of new HIV diagnoses per country. Source: ECDC/WHO"}
STATUS_ORDER = ("full member", "associate member", "Collaborative Partner")
STATUS_LABELS = {"full member": "Full member", "associate member": "Associate member",
                 "Collaborative Partner": "Collaborative Partner"}
HOVER = {
    "A": {"full member": "{country}: IPPF member association",
          "Collaborative Partner": "{country}: IPPF collaborative partner",
          "associate member": "{country}: IPPF associate member"},
    "F": {"core": "{country}: receives the IPPF core grant in {year}",
          "other": "{country}: receives other IPPF grants in {year}",
          "none": "{country}: IPPF {member}, no IPPF grant in {year}"},
    "D": "{country}: {rate} new HIV diagnoses {unit}, {year}. Source: ECDC/WHO",
    "D_none": "{country}: no {year} data",
}

HEADLINE = "IPPF member associations and partners work in {n} of the {m} countries of the WHO European Region"
DEFINITION = ("\"Work in\" means an IPPF member association or partner organisation is based in the country. "
              "It does not mean service coverage.")


# --- the WHO list and the headline -----------------------------------------------------------------------

def load_who(path) -> set:
    """Upper-cased iso3 codes of the WHO European Region member states (config/who_europe.csv).
    A file saved by Excel (byte-order mark, blank rows, lower case) loads the same as a clean one."""
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            rd = csv.DictReader(f)
            rd.fieldnames = [c.strip() for c in (rd.fieldnames or [])]
            if "iso3" not in rd.fieldnames:
                raise Stop(1, f"stop: {Path(path).name} has no iso3 column")
            out = {(r.get("iso3") or "").strip().upper() for r in rd}
    except OSError as e:
        raise Stop(1, f"stop: cannot read the WHO European Region list: {e}")
    out.discard("")
    if not out:
        raise Stop(1, f"stop: {Path(path).name} lists no country; the headline cannot be computed")
    return out


def headline(rows: list, who: set) -> dict:
    """{"n", "m", "outside"}: n = countries coloured on map A (active members), m = WHO member states,
    outside = counted countries missing from the WHO list (the build refuses when there is any)."""
    counted = computed.member_status_classes(rows)
    return {"n": len(counted), "m": len(who), "outside": sorted(i for i in counted if i not in who)}


def region_notes(master_rows: list, who: set, drawn: set, counted: set) -> list:
    """Build notes, empty when the master list, the WHO list and the geometry agree."""
    master = {r["iso3"] for r in master_rows}
    notes = []
    if master - who:
        notes.append("note: master countries not on the WHO European Region list: " + ", ".join(sorted(master - who)))
    if who - master:
        notes.append("note: WHO European Region countries not in the master list: " + ", ".join(sorted(who - master)))
    undrawn = sorted(counted - drawn)
    if undrawn:
        notes.append("note: counted in the headline but no map geometry, so not drawn: " + ", ".join(undrawn))
    return notes


# --- the three views ------------------------------------------------------------------------------------

def _year(rows, indicator):
    return max((r["reference_year"] for r in rows if r["indicator_id"] == indicator), default="")


def _classed(v, order, colour_of, label_of, filters=True):
    """Legend (and filters) for the classes that hold a country, in `order`; a class keeps the colour of
    its position in `order`, so an empty class never shifts the colours of the later ones."""
    for i, key in enumerate(order):
        isos = sorted(iso for iso, k in v["colour"].items() if k == key)
        if not isos:
            continue
        text = pw._text(label_of(key), len(isos))
        v["legend"].append({"key": key, "label": label_of(key), "count": len(isos), "half": 0,
                            "colour": colour_of(i), "text": text})
        if filters:
            v["filters"].append({"key": key, "text": text, "colour": colour_of(i), "members": isos})


def _view(m, year, legend_title):
    return {"id": m, "name": NAMES[m], "title": computed.render(TITLES[m], year=year),
            "subtitle": computed.render(SUBTITLES[m]), "legend_title": legend_title,
            "legend": [], "filters": [], "colour": {}, "tips": {}}


def summary_views(rows: list, master_rows: list):
    """([view A, view F, view D], frame): the summary page's maps in the dict shape publish_webmap.page
    draws. Every hover string comes from HOVER and register values; deck ScreenTips are never read.
    frame = the active member countries (design 4.1)."""
    name = {r["iso3"]: r["country"] for r in master_rows}
    nm = lambda iso: name.get(iso, iso)  # noqa: E731
    status = computed.member_status_classes(rows)
    order = list(STATUS_ORDER) + sorted(set(status.values()) - set(STATUS_ORDER))

    a = _view("A", _year(rows, "ippf_membership"), "Membership")
    a["colour"] = dict(status)
    a["tips"] = {iso: HOVER["A"].get(st, "{country}: " + st).format(country=nm(iso)) for iso, st in status.items()}
    pal_a = pw.PALETTE["A"]
    _classed(a, order, lambda i: pal_a[min(i, len(pal_a) - 1)], lambda k: STATUS_LABELS.get(k, k))

    fyear = _year(rows, "ippf_funding_streams")
    f = _view("F", fyear, "IPPF funding")
    f["colour"] = computed.funding_band(rows, with_partner=True)
    for iso, band in f["colour"].items():
        member = "partner" if status.get(iso) == "Collaborative Partner" else "member"
        f["tips"][iso] = HOVER["F"][band].format(country=nm(iso), year=fyear, member=member)
    _classed(f, computed.FUNDING_BANDS, lambda i: pw.PALETTE["C"][i],
             lambda k: computed.FUNDING_LABELS[k].format(year=fyear))

    rates = [r for r in pw._rates(rows) if r["reference_year"] == rdc.RATE_YEAR]
    unit = next((r.get("unit", "") for r in rates if r.get("unit")), "")
    d = _view("D", rdc.RATE_YEAR, f"New HIV diagnoses, {unit}" if unit else "New HIV diagnoses")
    d["colour"] = {r["iso3"]: computed.d_class(float(r["value"])) for r in rates}
    by_rate = {r["iso3"]: r for r in rates}
    for iso in sorted(set(status) | set(d["colour"])):
        r = by_rate.get(iso)
        d["tips"][iso] = (HOVER["D"].format(country=nm(iso), rate=r["value"].strip(), unit=r.get("unit", ""),
                                            year=rdc.RATE_YEAR).replace("  ", " ") if r
                          else HOVER["D_none"].format(country=nm(iso), year=rdc.RATE_YEAR))
    for i in range(len(computed.D_BANDS) + 1):
        n = sum(1 for c in d["colour"].values() if c == i)
        lab = computed.d_band_label(i)
        d["legend"].append({"key": i, "label": lab, "count": n, "half": 0, "colour": pw.PALETTE["D"][i],
                            "text": pw._text(lab, n)})
    return [a, f, d], set(status)


# --- page header, footer and the page config -----------------------------------------------------------

SOURCES = "IPPF membership and grant records; ECDC/WHO HIV surveillance; WHO European Region member list"
PAGE_KEYS = ("contact", "author_unit", "disclosure")


def _e(s):
    return html.escape(str(s), quote=True)


def load_page_cfg(path) -> dict:
    """config/summary_page.csv (key,value): contact, author_unit and disclosure, all non-empty. They live in
    the map root, not in this public repository."""
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            cfg = {(r.get("key") or "").strip(): (r.get("value") or "").strip() for r in csv.DictReader(f)}
    except OSError as e:
        raise Stop(1, f"stop: cannot read the summary page config: {e}")
    missing = [k for k in PAGE_KEYS if not cfg.get(k)]
    if missing:
        raise Stop(1, f"stop: {Path(path).name} lacks a value for: {', '.join(missing)}")
    return {k: cfg[k] for k in PAGE_KEYS}


def header_html(head: dict, edition: str, made_on: str) -> str:
    return ("<h1>{}</h1><p>{}</p><p>{}</p><p>{}</p>".format(
        _e(PAGE_TITLE.format(edition=edition)),
        _e(HEADLINE.format(n=head["n"], m=head["m"])),
        _e(DEFINITION),
        _e(f"Edition {edition}, made on {made_on}")))


def footer_html(cfg: dict) -> str:
    return ("<p>Sources: {}.</p><p>For more information: <a href=\"mailto:{c}\">{c}</a></p>"
            "<p>Prepared by {}.</p><p>{}</p>").format(_e(SOURCES), _e(cfg["author_unit"]), _e(cfg["disclosure"]),
                                                      c=_e(cfg["contact"]))
