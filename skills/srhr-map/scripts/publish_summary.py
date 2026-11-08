"""Write the summary web map for donors and partners (SRHR map skill, phase e).

One self-contained page with a computed headline ("N of the M countries of the WHO European Region")
and three maps: membership (A), funding in three bands (F) and new HIV diagnoses (D). It holds no
stream name, member association name or ma_code, and no hover text from a deck ScreenTip: every
string comes from the templates in this file and the register values. Geometry, the embedded d3 and
the page frame are reused from publish_webmap.py. Exit 1 = input error, exit 2 = the target exists.
"""
import argparse
import csv
import html
import re
from html.parser import HTMLParser
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
# Funding bands in FUNDING_BANDS order (core, other, none): IPPF Dream, Crystal and a Pear tint. Not the internal
# map C tints, whose first colour is a grey close to the context land; every band here is clearly not grey
# (CIEDE2000 >= 21 against --map-land). Ane chose this 2026-11-08 (phase e task 7).
F_COLOURS = ("#00313C", "#71C5E8", "#D5DE7C")
STATUS_ORDER = ("full member", "associate member", "Collaborative Partner")
KNOWN_STATUSES = STATUS_ORDER + ("withdrawn",)  # any other member_status stops the build (review minor 3)
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

HEADLINE = "IPPF member associations and partners work in {n} of the {m} countries of the WHO European Region."
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
                if any(";" in c for c in rd.fieldnames):
                    raise Stop(1, f"stop: {Path(path).name} uses semicolons between columns (Excel on a "
                                  "comma-decimal computer saves it so); save it again as CSV with commas")
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
    for r in rows:
        if r["member_status"] not in KNOWN_STATUSES:
            raise Stop(1, f"stop: member_status {r['member_status']!r} in the register row iso3 {r['iso3']}, "
                          f"indicator {r['indicator_id']}, year {r['reference_year']} is not one of "
                          + ", ".join(KNOWN_STATUSES) + ". It would be counted in the headline and share a "
                          "colour; correct the register, nothing written.")
    name = {r["iso3"]: r["country"] for r in master_rows}
    nm = lambda iso: name.get(iso, iso)  # noqa: E731
    status = computed.member_status_classes(rows)
    order = list(STATUS_ORDER)

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
    _classed(f, computed.FUNDING_BANDS, lambda i: F_COLOURS[i],
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
        _e(f"Edition {edition}, made on {_dmy(made_on)}")))


def _dmy(iso: str) -> str:
    """2026-11-08 -> 08.11.2026 (IPPF date style); any other text is kept as it is."""
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", iso)
    return f"{m.group(3)}.{m.group(2)}.{m.group(1)}" if m else iso


def footer_html(cfg: dict) -> str:
    return ("<p>Sources: {}.</p><p>For more information: <a href=\"mailto:{c}\">{c}</a></p>"
            "<p>Prepared by {}.</p><p>{}</p>").format(_e(SOURCES), _e(cfg["author_unit"]), _e(cfg["disclosure"]),
                                                      c=_e(cfg["contact"]))


# --- forbidden-text scan (design 6.1) -------------------------------------------------------------------

def forbidden_terms(streams_path, ma_codes_path) -> set:
    """Every stream key, label and ledger name, and every member association name and ma_code: none of
    them may appear on the summary page. A file that yields no term stops the build, so an unreachable
    or emptied file can never make the scan pass. A file missing a scanned column stops too, so a
    dropped column can never shrink the term list without anyone seeing it."""
    def read(path, columns):
        try:
            with open(path, encoding="utf-8-sig", newline="") as f:
                rd = csv.DictReader(f)
                have = {c.strip() for c in (rd.fieldnames or [])}
                gone = [c for c in columns if c not in have]
                if gone:
                    raise Stop(1, f"stop: {Path(path).name} has no {', '.join(gone)} column; the forbidden-text "
                                  "scan needs it")
                return [{(k or "").strip(): v for k, v in r.items()} for r in rd]
        except OSError as e:
            raise Stop(1, f"stop: cannot read {Path(path).name} for the forbidden-text scan: {e}")
    s_terms, m_terms = set(), set()
    for r in read(streams_path, ("key", "label", "ledger_names")):
        names = [r.get("key"), r.get("label")] + re.split(r"[;|]", r.get("ledger_names") or "")
        s_terms |= {(n or "").strip() for n in names}
    for r in read(ma_codes_path, ("org_name", "ma_code")):
        m_terms |= {(r.get("org_name") or "").strip(), (r.get("ma_code") or "").strip()}
    s_terms.discard("")
    m_terms.discard("")
    for path, terms in ((streams_path, s_terms), (ma_codes_path, m_terms)):
        if not terms:
            raise Stop(1, f"stop: {Path(path).name} yields no term; the forbidden-text scan would prove nothing")
    return s_terms | m_terms


class _PageText(HTMLParser):
    """Visible text outside <script>/<style>, plus the raw text of the map-data JSON element."""

    def __init__(self):
        super().__init__()
        self.text, self.data, self._in = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._in = "data" if tag == "script" and dict(attrs).get("id") == "map-data" else tag

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._in = None

    def handle_data(self, d):
        if self._in == "data":
            self.data = (self.data or "") + d
        elif self._in is None and d.strip():
            self.text.append(d.strip())


def _json_strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from _json_strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from _json_strings(v)


def page_strings(html_text: str) -> list:
    """The strings a reader can see: page text outside scripts and styles, and every string value in the
    embedded map data. Numbers (so geometry coordinates), dict keys and the d3 library are left out."""
    p = _PageText()
    p.feed(html_text)
    p.close()
    out = list(p.text)
    if p.data:
        out += [s for s in _json_strings(json.loads(p.data)) if s.strip()]
    return out


def scan(strings: list, terms: set, allow: set) -> list:
    """[(term, string)] for each whole-word, case-sensitive occurrence of a term not on the allowlist."""
    hits = []
    for t in sorted(terms - set(allow)):
        rx = re.compile(r"(?<!\w)" + re.escape(t) + r"(?!\w)")
        hits += [(t, s) for s in strings if rx.search(s)]
    return hits


def load_allow(path) -> set:
    """config/summary_scan_allow.csv (term,ticked_by,date): a term counts only once Ane has ticked it."""
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            return {r["term"].strip() for r in csv.DictReader(f)
                    if (r.get("term") or "").strip() and (r.get("ticked_by") or "").strip()}
    except FileNotFoundError:
        return set()


# --- build and command line -----------------------------------------------------------------------------

def partner_band_changes(rows: list) -> list:
    """Countries whose funding band depends on counting partner streams (design 4.3): a build note."""
    a, b = computed.funding_band(rows, True), computed.funding_band(rows, False)
    return sorted(i for i in a if a[i] != b.get(i))


def members_without_funding(rows: list) -> list:
    """Active members with no funding row: map F gives them no band and no grant hover (a build note)."""
    return sorted(set(computed.member_status_classes(rows)) - set(computed.funding_band(rows)))


def _d3_text(d3):
    try:
        data = Path(d3).read_bytes()
        text = data.decode("utf-8")
    except (OSError, TypeError, ValueError) as e:
        raise Stop(1, f"stop: cannot read the d3 library file: {e}")
    pw._d3_ok(data, Path(d3).name)
    if "</script" in text.lower():
        raise Stop(1, "stop: the d3 library text contains a closing script tag; it cannot be embedded")
    return text


def _topo(geometry):
    try:
        data = Path(geometry).read_bytes()
        pw._geometry_ok(data)
        return json.loads(data.decode("utf-8"))
    except (OSError, ValueError) as e:
        raise Stop(1, f"stop: cannot read the geometry file: {e}")


def summary_page_text(rows, master_rows, who, cfg, topo, d3_js, edition, made, names=None):
    """(page text, data, notes) for the summary page; publish.py check calls the same parts."""
    head = headline(rows, who)
    if head["outside"]:
        raise Stop(1, "stop: counted in the headline but missing from the WHO European Region list: "
                      + ", ".join(head["outside"]) + ". Check config/who_europe.csv; nothing written.")
    views, frame = summary_views(rows, master_rows)
    shapes = pw.countries(topo, master_rows, frame, names)
    drawn = {c["iso3"] for c in shapes if c["iso3"] and c["paths"]}
    notes = region_notes(master_rows, who, drawn, set(frame))
    newer = pw.newer_rate_years(rows)
    if newer:
        notes.append(f"note: the register has HIV rates for {', '.join(newer)}; map D shows {rdc.RATE_YEAR} "
                     "(register_deck_check.RATE_YEAR)")
    moved = partner_band_changes(rows)
    if moved:
        notes.append("note: counting partner streams moves these countries to another funding band: " + ", ".join(moved))
    unfunded = members_without_funding(rows)
    if unfunded:
        name = {r["iso3"]: r["country"] for r in master_rows}
        notes.append("note: active members with no funding row, so no band on the funding map: "
                     + ", ".join(f"{name.get(i, i)} ({i})" for i in unfunded))
    data = {"edition": edition, "made_on": made, "headline": {"n": head["n"], "m": head["m"]},
            "tab_letters": False, "views": views, "countries": shapes}
    text = pw.page(data, d3_js, header_html(head, edition, made), footer_html(cfg),
                   title=_e(PAGE_TITLE.format(edition=edition)))
    return text, data, notes


def build_summary(register, ma_codes, crosswalk, master, who, page_cfg, geometry, d3, out, edition=None, allow=None,
                  context_names=None):
    """Write the summary page; nothing is written when any check stops the build (the scan runs on the
    finished page text before the file is opened)."""
    pw.refuse_existing(out)
    names = pw.load_context_names(context_names) if context_names else None
    d3_js = _d3_text(d3)
    rows, _, _, edition = pw.load_inputs(register, None, None, edition)
    master_rows = pw._read(master)
    who_set = load_who(who)
    cfg = load_page_cfg(page_cfg)
    terms = forbidden_terms(crosswalk, ma_codes)
    allowed = load_allow(allow) if allow else set()
    text, data, notes = summary_page_text(rows, master_rows, who_set, cfg, _topo(geometry), d3_js, edition,
                                          pw.made_on(), names)
    for n in notes:
        print(n)
    hits = scan(page_strings(text), terms, allowed)
    if hits:
        raise Stop(1, "stop: the summary page would show a stream, member association name or ma_code; nothing "
                      "written." + "".join(f"\n  {t!r} in {s[:120]!r}" for t, s in hits))
    with pw.claimed(out, encoding="utf-8") as fh:
        fh.write(text)
    return Path(out), data


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for a in ("--register", "--ma-codes", "--crosswalk", "--master", "--who", "--page-config", "--geometry", "--d3",
              "--out"):
        ap.add_argument(a, required=True)
    ap.add_argument("--edition")
    ap.add_argument("--allow")
    ap.add_argument("--context-names", help="config/context_names.csv: hover names for the grey shapes")
    a = ap.parse_args(argv)
    try:
        out, data = build_summary(a.register, a.ma_codes, a.crosswalk, a.master, a.who, a.page_config, a.geometry,
                                  a.d3, a.out, a.edition, a.allow, a.context_names)
    except Stop as e:
        print(str(e), file=sys.stderr)
        return e.code
    for v in data["views"]:
        print(f"{v['id']}: {len(v['colour'])} coloured, {len(v['tips'])} tooltips")
    print(f"headline: {data['headline']['n']} of {data['headline']['m']}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
