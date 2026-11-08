"""Write the web map for one edition (SRHR map skill, phase d, publish step).

    python publish_webmap.py --register <map_register_<edition>.csv> --crosswalk <config/streams.csv>
                             --master <master_countries.csv> --decks <folder with Map A..D *.pptx>
                             --geometry <countries-50m.json> --out <publish folder>/webmap_<edition>.html
                             [--edition <edition>]

One self-contained HTML page with one view per map A to D. Every number comes from the register at
publish time through computed.py, the same functions the decks use:
  colours   A and B by class (computed.country_classes), C by membership status, D by rate band
            (computed.d_class); withdrawn members are never coloured on A to C
  legend    class counts (computed.class_counts); D counts countries per band
  filters   the deck filter layers: A and B per class, C per stream (a partner stream counts as held,
            as on the deck); D has none
  tooltip   the deck ScreenTip of slide 1, with register values put into its value spans by
            publish_plan.new_tip (the same function the deck swap uses), so after a swap the web map and
            the deck say the same words; a country outside the register keeps the deck text
  titles    digit-free templates (TEMPLATES) filled through computed.render
Geometry: the pinned world-atlas topology (GEOMETRY_URL), joined to the master list by its m49 code,
or by name when a country has no m49 code; neighbouring countries are drawn grey for context.
The page embeds everything: the pinned d3 7.9.0 library (--d3, refused unless it matches D3_SRI), the
geometry (refused unless it matches GEOMETRY_SHA256) and the data, so it opens offline and is shared as a
file. Only the Google Fonts stylesheet is external; offline the page falls back to Arial.
The target is never overwritten (exit 2). Exit 1 = input error.
"""
import argparse
import base64
import hashlib
import html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import computed  # noqa: E402
import deck_shapes  # noqa: E402
import publish_plan as pp  # noqa: E402
import register_deck_check as rdc  # noqa: E402
from publish_workbook import Stop, _read, claimed, load_inputs, made_on, refuse_existing  # noqa: E402

WEB = "https" + "://"  # split so public_repo_clean does not read the scheme as a drive letter
GEOMETRY_URL = WEB + "cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json"
# sha256 of that file as downloaded and cached in Task 7 (prefix 04342cdc recorded then; full value 2026-11-08).
GEOMETRY_SHA256 = "04342cdc1e3016bcd7db1630de95684d67b79fe3c8c460321e87aef469502394"
D3_URL = WEB + "cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"
# Integrity hash cdnjs publishes for d3 7.9.0 d3.min.js (read from the cdnjs API, 2026-11-08).
D3_SRI = "sha512-vc58qvvBdrDR4etbxMdlTt4GBQk1qjvyORR2nrsPsFPyrs+/u5c3+1Ct6upOgdZoIl7eq6k3a1UPDSNAQi/32A=="
FRAME_MARGIN = 6  # degrees around the deck countries kept as grey context
MAP_NAMES = {"A": "Members and partners", "B": "Other grant streams", "C": "Funding streams",
             "D": "HIV need and MA focus"}
TEMPLATES = {
    "page": ("SRHR maps", "Edition {edition}, made on {made_on} from the map register"),
    "A": ("Members and partners",
          "{ma} Member Association{ma_s} (MAs) and {cp} Collaborative Partner{cp_s} in {n} countr{n_y}"),
    "B": ("Other grant streams", "Grants other than the core grant, {year}. {reached} of {n} members reached"),
    "C": ("Funding streams",
          "All IPPF streams, core grant included, {year}. {reached} of {n} members reached; {none} get none"),
    "D": ("HIV need and MA focus", "New HIV diagnoses in {year}, {unit}. {n} countries with data"),
}
# Class colours as painted on the approved decks (IPPF Visual Identity 2025), in legend order.
PALETTE = {
    "A": ["#00313C", "#71C5E8", "#D1DC72"],
    "B": ["#CBD3D5", "#98A7AC", "#677D85", "#37565F", "#00313C"],
    "C": ["#BFC8CB", "#A8D9F0", "#D5DE7C"],
    "D": ["#CBD3D5", "#A2B1B1", "#6C878A", "#365C63", "#00313C"],
}
STREAM_FALLBACK = "#00313C"


# --- geometry ---------------------------------------------------------------------------------------

def _arcs(topo):
    t = topo.get("transform")
    out = []
    for arc in topo["arcs"]:
        if t:
            x = y = 0
            pts = []
            for dx, dy in arc:
                x, y = x + dx, y + dy
                pts.append([x * t["scale"][0] + t["translate"][0], y * t["scale"][1] + t["translate"][1]])
        else:
            pts = [list(p) for p in arc]
        out.append(pts)
    return out


def _ring(idx, arcs):
    pts = []
    for i in idx:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts += a if not pts else a[1:]
    q = []
    for x, y in pts:
        p = [round(x, 2), round(y, 2)]
        if not q or q[-1] != p:
            q.append(p)
    return q


def _polygons(g, arcs):
    if g["type"] == "Polygon":
        return [[_ring(r, arcs) for r in g["arcs"]]]
    if g["type"] == "MultiPolygon":
        return [[_ring(r, arcs) for r in poly] for poly in g["arcs"]]
    return []


def _bbox(polys):
    xs = [p[0] for poly in polys for ring in poly for p in ring]
    ys = [p[1] for poly in polys for ring in poly for p in ring]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def countries(topo, master_rows, frame_isos):
    """[{iso3, name, paths}] for the master countries and the grey context countries around them."""
    arcs = _arcs(topo)
    obj = topo["objects"].get("countries") or next(iter(topo["objects"].values()))
    by_m49 = {r["m49"].zfill(3): r for r in master_rows if r.get("m49", "").strip().isdigit()}
    by_name = {r["country"]: r for r in master_rows if not r.get("m49", "").strip().isdigit()}
    found, context = {}, []
    for g in obj["geometries"]:
        gid = str(g.get("id", "")).strip()
        name = (g.get("properties") or {}).get("name", "")
        r = by_m49.get(gid.zfill(3)) if gid.isdigit() else None
        r = r or (by_name.get(name) if not gid else None)
        polys = _polygons(g, arcs)
        if not polys:
            continue
        if r:
            found.setdefault(r["iso3"], {"iso3": r["iso3"], "name": r["country"], "paths": []})["paths"] += polys
        else:
            context.append({"iso3": "", "name": name, "paths": polys})
    boxes = [_bbox(c["paths"]) for i, c in found.items() if i in frame_isos] or \
            [_bbox(c["paths"]) for c in found.values()]
    boxes = [b for b in boxes if b]
    out = list(found.values())
    for r in master_rows:
        if r["iso3"] not in found:
            out.append({"iso3": r["iso3"], "name": r["country"], "paths": []})
    if boxes:
        x0, y0 = min(b[0] for b in boxes) - FRAME_MARGIN, min(b[1] for b in boxes) - FRAME_MARGIN
        x1, y1 = max(b[2] for b in boxes) + FRAME_MARGIN, max(b[3] for b in boxes) + FRAME_MARGIN
        for c in context:
            b = _bbox(c["paths"])
            if b and b[0] <= x1 and b[2] >= x0 and b[1] <= y1 and b[3] >= y0:
                out.append(c)
    return out


def _download(url, what):
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read()
    except (urllib.error.URLError, OSError) as e:
        raise Stop(1, f"stop: cannot download the {what} ({e}); nothing written. Check the network, or place "
                      "the cached file by hand.") from None


def _geometry_ok(data: bytes):
    if hashlib.sha256(data).hexdigest() != GEOMETRY_SHA256:
        raise Stop(1, "stop: the geometry file does not match the pinned world-atlas hash; delete it and run again")


def fetch_geometry(dest: Path) -> str:
    """Download the pinned topology once into dest; refuse any file (cached or downloaded) whose hash differs."""
    dest = Path(dest)
    if dest.exists():
        data = dest.read_bytes()
    else:
        data = _download(GEOMETRY_URL, "geometry")
        _geometry_ok(data)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    _geometry_ok(data)
    return GEOMETRY_SHA256


def _sri(data: bytes) -> str:
    return "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()


def _d3_ok(data: bytes, name: str):
    if _sri(data) != D3_SRI:
        raise Stop(1, f"stop: {name} does not match the pinned d3 integrity hash; delete it and run again")


def fetch_d3(dest: Path) -> str:
    """Download the pinned d3 once into dest; refuse any file (cached or downloaded) whose hash differs."""
    dest = Path(dest)
    if dest.exists():
        data = dest.read_bytes()
    else:
        data = _download(D3_URL, "d3 library")
        if _sri(data) != D3_SRI:
            raise Stop(1, "stop: the downloaded d3 does not match the pinned integrity hash; nothing written")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    _d3_ok(data, dest.name)
    return D3_SRI


# --- views ------------------------------------------------------------------------------------------

def _plural(n, one="", many="s"):
    return one if n == 1 else many


def _text(label, n, half=0):
    return f"{label} ({n} + {half} half)" if half else f"{label} ({n})"


def _deck_order(inv, prefix):
    seen = []
    for r in inv:
        if r["kind"] == "legend_count" and r["shape_name"].startswith(prefix):
            lab = computed.legend_label(r["current"])
            if lab not in seen:
                seen.append(lab)
    return seen


def _ordered(labels, deck_order, key=None):
    labels = list(labels)
    rest = sorted((x for x in labels if x not in deck_order), key=key)
    return [x for x in deck_order if x in labels] + rest


def _deck_colour(m, labels, deck_order, low=False):
    """{label: colour}: a class keeps the colour of its position in the full deck legend, so an edition
    with an empty class does not shift every later class one step; labels the deck lacks follow it."""
    norm = (lambda x: x.lower()) if low else (lambda x: x)
    deck = [norm(x) for x in deck_order]
    pal = PALETTE[m]
    out, j = {}, len(deck)
    for lab in labels:
        if norm(lab) in deck:
            i = deck.index(norm(lab))
        else:
            i, j = j, j + 1
        out[lab] = pal[min(i, len(pal) - 1)]
    return out


def tips_for(m, deck_tips, by, names, crosswalk):
    """{iso3: tooltip}: the deck tip with register values in its spans (publish_plan.new_tip)."""
    in_reg = pp._in_register(m, by)
    out = {}
    for name, tip in deck_tips.items():
        iso = names.get(name)
        if not iso:
            continue
        out[iso] = pp.new_tip(m, tip, by, iso, crosswalk) if iso in in_reg else tip
    return out


def _active_rows(rows, indicator):
    return [r for r in rows if r["indicator_id"] == indicator and r["member_status"] != "withdrawn"]


def _rates(rows):
    return [r for r in rows if r["indicator_id"] == rdc.D_INDICATORS[0] and r["value"].strip()]


def newer_rate_years(rows):
    """Rate years in the register later than rdc.RATE_YEAR: reported by the build, never shown on map D."""
    return sorted({r["reference_year"] for r in _rates(rows) if r["reference_year"] > rdc.RATE_YEAR})


def view(m, rows, crosswalk, colours, deck_tips, inv, names):
    by = rdc._index(rows)
    v = {"id": m, "name": MAP_NAMES[m], "tips": tips_for(m, deck_tips, by, names, crosswalk),
         "legend": [], "colour": {}, "filters": [], "legend_title": ""}
    members = _active_rows(rows, "ippf_membership")
    if m in ("A", "B"):
        classes = computed.country_classes(m, rows, crosswalk)
        counts = computed.class_counts(m, rows, crosswalk)
        deck_order = _deck_order(inv, "Filter button: ")
        order = _ordered(counts, deck_order,
                         key=(lambda s: int(re.match(r"\d+", s).group())) if m == "B" else (lambda s: -counts[s][0]))
        cols = _deck_colour(m, order, deck_order)
        for lab in order:
            n, h = counts[lab]
            col = cols[lab]
            isos = sorted(iso for iso, cs in classes.items() if lab in cs)
            v["legend"].append({"key": lab, "label": lab, "count": n, "half": h, "colour": col, "text": _text(lab, n, h)})
            v["filters"].append({"key": lab, "text": _text(lab, n, h), "colour": col, "members": isos})
        v["colour"] = {iso: sorted(cs)[0] for iso, cs in classes.items()}
        v["legend_title"] = "Membership" if m == "A" else "Grant streams other than the core grant"
    elif m == "C":
        counts = computed.class_counts("C", rows, crosswalk)
        streams = _active_rows(rows, "ippf_funding_streams")
        statuses = {}
        for r in streams:
            statuses[r["member_status"]] = statuses.get(r["member_status"], 0) + 1
        deck = [x.lower() for x in _deck_order(inv, "Legend text: ")]
        order = sorted(statuses, key=lambda s: (deck.index(s.lower()) if s.lower() in deck else len(deck),
                                                -statuses[s], s))
        cols = _deck_colour("C", order, deck, low=True)
        for st in order:
            v["legend"].append({"key": st, "label": st[:1].upper() + st[1:], "count": statuses[st], "half": 0,
                                "colour": cols[st],
                                "text": _text(st[:1].upper() + st[1:], statuses[st])})
        v["colour"] = {r["iso3"]: r["member_status"] for r in streams}
        held = {}
        for r in streams:
            for k in computed.stream_keys(r["value_display"]):
                held.setdefault(k, set()).add(r["iso3"])
        for iso, keys in computed.partner_keys(rows).items():
            for k in keys:
                held.setdefault(k, set()).add(iso)
        for k, lab in crosswalk:
            if k not in counts:
                continue
            n, h = counts[k]
            v["filters"].append({"key": k, "text": _text(lab, n, h), "colour": colours.get(k) or STREAM_FALLBACK,
                                 "members": sorted(held.get(k, ()))})
        v["legend_title"] = "Membership status"
    else:
        rates = _rates(rows)
        v["colour"] = {r["iso3"]: computed.d_class(float(r["value"])) for r in rates
                       if r["reference_year"] == rdc.RATE_YEAR}
        unit = next((r["unit"] for r in rates if r["unit"]), "")
        for i in range(len(computed.D_BANDS) + 1):
            n = sum(1 for c in v["colour"].values() if c == i)
            lab = computed.d_band_label(i)
            v["legend"].append({"key": i, "label": lab, "count": n, "half": 0, "colour": PALETTE["D"][i],
                                "text": _text(lab, n)})
        v["legend_title"] = f"New HIV diagnoses, {unit}" if unit else "New HIV diagnoses"
    v["title"], v["subtitle"] = _titles(m, rows, crosswalk, members, v)
    return v


def _titles(m, rows, crosswalk, members, v):
    title, sub = TEMPLATES[m]
    n = len(members)
    if m == "A":
        cp = sum(1 for r in members if r["member_status"] == "Collaborative Partner")
        ma = n - cp
        vals = dict(ma=ma, ma_s=_plural(ma), cp=cp, cp_s=_plural(cp), n=n, n_y=_plural(n, "y", "ies"))
    elif m == "B":
        cnt = _active_rows(rows, "ippf_grant_streams_count")
        vals = dict(year=max((r["reference_year"] for r in cnt), default=""), n=len(cnt),
                    reached=sum(1 for r in cnt if r["value"].strip() not in ("", "0")))
    elif m == "C":
        st = _active_rows(rows, "ippf_funding_streams")
        partner = computed.partner_keys(rows)
        reached = sum(1 for r in st if computed.stream_keys(r["value_display"]) or partner.get(r["iso3"]))
        vals = dict(year=max((r["reference_year"] for r in st), default=""), n=len(st), reached=reached,
                    none=len(st) - reached)
    else:
        rates = _rates(rows)
        vals = dict(year=rdc.RATE_YEAR, n=len(v["colour"]),
                    unit=next((r["unit"] for r in rates if r["unit"]), ""))
    return computed.render(title, **vals), computed.render(sub, **vals)


# --- page -------------------------------------------------------------------------------------------

def _json(data):
    # "<" occurs only inside JSON strings, so < keeps the JSON valid while no "</script" or "<!--"
    # can end or confuse the script element that holds it.
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


FOOTER = ("Colours, counts and texts are computed from the approved map register. The text for each country is "
          "the same text as the hover text on the map slides.")


def page(data, d3_js, header_html=None, footer_html=None, title=None):
    """The page text. header_html / footer_html / title are ready-made (already escaped) markup for the
    summary page (publish_summary.py); left as None they give the internal page, unchanged."""
    head_title, head_sub = TEMPLATES["page"]
    if header_html is None:
        header_html = "<h1>{}</h1><p>{}</p>".format(
            html.escape(computed.render(head_title)),
            html.escape(computed.render(head_sub, edition=data["edition"], made_on=data["made_on"])))
    fill = {"TITLE": html.escape(head_title) if title is None else title,
            "HEADER": header_html, "FOOTER": html.escape(FOOTER, quote=False) if footer_html is None else footer_html,
            "WEB": WEB, "DATA": _json(data), "D3JS": d3_js}
    # one pass over the template: an inserted value is never searched for another placeholder
    return re.sub(r"@@([A-Z0-9]+)@@", lambda m: fill[m.group(1)], PAGE)


def build(register, crosswalk_path, master, decks, geometry, out, edition=None, d3=None):
    refuse_existing(out)
    try:
        d3_bytes = Path(d3).read_bytes()
        d3_js = d3_bytes.decode("utf-8")
    except (OSError, TypeError, ValueError) as e:
        raise Stop(1, f"stop: cannot read the d3 library file: {e}")
    _d3_ok(d3_bytes, Path(d3).name)  # the standalone CLI embeds only the pinned library, as publish.py does
    if "</script" in d3_js.lower():
        raise Stop(1, "stop: the d3 library text contains a closing script tag; it cannot be embedded")
    rows, _, _, edition = load_inputs(register, None, None, edition)
    master_rows = _read(master)
    newer = newer_rate_years(rows)
    if newer:
        print(f"note: the register has HIV rates for {', '.join(newer)}; map D still shows {rdc.RATE_YEAR} "
              "(register_deck_check.RATE_YEAR), as the decks do. Moving year changes the deck sentences.")
    views, frame = build_views(rows, crosswalk_path, master_rows, decks)
    try:
        geo_bytes = Path(geometry).read_bytes()
        _geometry_ok(geo_bytes)
        topo = json.loads(geo_bytes.decode("utf-8"))
    except (OSError, ValueError) as e:
        raise Stop(1, f"stop: cannot read the geometry file: {e}")
    data = {"edition": edition, "made_on": made_on(), "views": views,
            "countries": countries(topo, master_rows, frame)}
    text = page(data, d3_js)
    with claimed(out, encoding="utf-8") as fh:  # creates a new edition's folder; never overwrites (mode "x")
        fh.write(text)
    return Path(out), data


def build_views(rows, crosswalk_path, master_rows, decks):
    """([view per map A-D], set of iso3 with a tip): everything the page shows that comes from the
    register and the decks. `publish.py check` calls it too, so a kept page is compared field by field."""
    names = {r["country"]: r["iso3"] for r in master_rows}
    xw = _read(crosswalk_path)
    crosswalk = [(r["key"], r["label"]) for r in xw]
    colours = {r["key"]: "#" + r["colour"].strip().lstrip("#") for r in xw if r.get("colour", "").strip()}
    views, frame = [], set()
    for m in "ABCD":
        found = sorted(Path(decks).glob(rdc.deck_glob(m)))
        if len(found) != 1:
            raise Stop(1, f"stop: expected one deck '{rdc.deck_glob(m)}' in the decks folder, found {len(found)}")
        slides = rdc.deck_tips(found[0])
        if not slides:
            raise Stop(1, f"stop: no country ScreenTips in {found[0].name}")
        inv = [r for r in deck_shapes.inventory(found[0], names) if r["slide"] == slides[0][0]]
        try:
            v = view(m, rows, crosswalk, colours, slides[0][1], inv, names)
        except pp.Structure as e:
            raise Stop(1, f"stop: map {m}: {e}. The deck tip cannot take the register value: run publish plan; "
                          "this is a structure change for phase (e).")
        views.append(v)
        frame |= set(v["tips"])
    return views, frame


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for a in ("--register", "--crosswalk", "--master", "--decks", "--geometry", "--out", "--d3"):
        ap.add_argument(a, required=True)
    ap.add_argument("--edition")
    a = ap.parse_args(argv)
    try:
        out, data = build(a.register, a.crosswalk, a.master, a.decks, a.geometry, a.out, a.edition, a.d3)
    except Stop as e:
        print(str(e), file=sys.stderr)
        return e.code
    for v in data["views"]:
        print(f"map {v['id']}: {len(v['colour'])} coloured, {len(v['tips'])} tooltips, {len(v['filters'])} filters")
    print(f"wrote {out}")
    return 0


PAGE = r"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>@@TITLE@@</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="@@WEB@@fonts.googleapis.com">
<link rel="stylesheet" href="@@WEB@@fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Semi+Condensed:wght@600;700&display=swap">
<style>
/* Layout: masthead, map tabs, then a map stage with legend and filters beside it (stacked on phones). */
:root {
  --bg: #F6F7F6; --surface: #FFFFFF; --ink: #00313C; --ink-2: #3E5A61; --muted: #6E8288;
  --line: #D8DCD8; --land: #E6E9E6; --land-line: #FFFFFF; --off: #EEF0EE; --accent: #EB3300;
  --tip-bg: #00313C; --tip-ink: #FFFFFF;
  /* the map card stays light in both themes: the deck class colours were chosen for a light ground */
  --map-bg: #F3F5F4; --map-land: #E3E7E6; --map-line: #FFFFFF; --map-off: #EEF0EE;
  --display: "Barlow Semi Condensed", "Arial Narrow", Arial, sans-serif;
  --body: "Barlow", "Segoe UI", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0E1E22; --surface: #132A30; --ink: #E8EEEE; --ink-2: #B9C7C9; --muted: #8FA2A6;
  --line: #2A4249; --land: #1C343A; --land-line: #0E1E22; --off: #23393F; --accent: #EB3300;
  --tip-bg: #00313C; --tip-ink: #FFFFFF; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #0E1E22; --surface: #132A30; --ink: #E8EEEE; --ink-2: #B9C7C9; --muted: #8FA2A6;
  --line: #2A4249; --land: #1C343A; --land-line: #0E1E22; --off: #23393F; --accent: #EB3300;
  --tip-bg: #00313C; --tip-ink: #FFFFFF; color-scheme: dark }
body { background: var(--bg); color: var(--ink); font: 16px/1.5 var(--body); margin: 0; }
.wrap { max-width: 1180px; margin: 0 auto; padding-block: 24px 40px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
header { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 16px; border-bottom: 3px solid var(--ink); padding-bottom: 12px; }
header h1 { font: 700 2rem/1.1 var(--display); margin: 0; letter-spacing: .01em; }
header p { margin: 0; color: var(--muted); font-size: .9rem; }
nav.tabs { display: flex; flex-wrap: wrap; gap: 0; margin: 16px 0 0; border-bottom: 1px solid var(--line); }
nav.tabs a { font: 600 1rem var(--display); color: var(--ink-2); text-decoration: none; padding: 10px 14px;
  border-bottom: 3px solid transparent; margin-bottom: -1px; }
nav.tabs a[aria-current="page"] { color: var(--ink); border-bottom-color: var(--accent); }
nav.tabs a:focus-visible, button:focus-visible, path.c:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.view-head { margin: 20px 0 12px; max-width: 70ch; }
.view-head h2 { font: 700 1.6rem/1.15 var(--display); margin: 0 0 4px; text-wrap: balance; }
.view-head p { margin: 0; color: var(--ink-2); }
.stage { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 20px; align-items: start; }
@media (max-width: 820px) { .stage { grid-template-columns: minmax(0, 1fr); } }
.map { background: var(--map-bg); border: 1px solid var(--line); position: relative; min-width: 0; overflow: hidden; }
.map svg { display: block; width: 100%; height: auto; overflow: hidden; }
path.ctx { fill: var(--map-land); stroke: var(--map-line); stroke-width: .5; vector-effect: non-scaling-stroke; }
path.c { stroke: var(--map-line); stroke-width: .6; cursor: default; vector-effect: non-scaling-stroke; }
.map svg { cursor: grab; touch-action: pan-x pan-y; }
.map svg:active { cursor: grabbing; }
.zoom { position: absolute; top: 10px; left: 10px; display: grid; gap: 4px; z-index: 4; }
.zoom button { font: 600 1rem/1 var(--body); min-width: 36px; height: 36px; padding: 0 8px; color: #00313C; background: #FFFFFF;
  border: 1px solid #B8C2C0; border-radius: 3px; cursor: pointer; }
.zoom button:disabled { color: #9AA7A9; cursor: default; }
.zoom #zoom-reset { font-size: .78rem; }
.map-col { min-width: 0; }
.hint { margin: 6px 0 0; font-size: .82rem; color: var(--muted); }
path.c.has-tip { cursor: pointer; }
path.c.dim { fill: var(--map-off) !important; }
path.c.hot { stroke: var(--accent); stroke-width: 1.6; }
path.hl { fill: none; stroke: var(--accent); stroke-width: 1.6; vector-effect: non-scaling-stroke; pointer-events: none; }
aside { min-width: 0; display: grid; gap: 18px; }
aside h3 { font: 600 .78rem var(--body); text-transform: uppercase; letter-spacing: .08em; color: var(--muted); margin: 0 0 6px; }
ul.legend { list-style: none; margin: 0; padding: 0; display: grid; gap: 4px; }
ul.legend li { display: grid; grid-template-columns: 14px 1fr; gap: 8px; align-items: center; font-size: .92rem; font-variant-numeric: tabular-nums; }
.sw { width: 14px; height: 14px; border: 1px solid var(--line); }
.filters { display: flex; flex-wrap: wrap; gap: 6px; }
.filters button { font: 500 .85rem var(--body); color: var(--ink); background: var(--surface); border: 1px solid var(--line);
  padding: 5px 10px; border-radius: 3px; cursor: pointer; display: inline-flex; gap: 6px; align-items: center; font-variant-numeric: tabular-nums; }
.filters button .dot { width: 9px; height: 9px; border-radius: 50%; }
.filters button[aria-pressed="true"] { border-color: var(--ink); box-shadow: inset 0 0 0 1px var(--ink); }
#tip { position: absolute; pointer-events: none; max-width: 320px; background: var(--tip-bg); color: var(--tip-ink);
  font-size: .88rem; line-height: 1.4; padding: 8px 10px; border-radius: 3px; z-index: 5; box-shadow: 0 2px 8px rgba(0, 49, 60, .25); }
.readout { min-height: 3em; font-size: .92rem; color: var(--ink-2); border-left: 3px solid var(--accent); padding-left: 10px; }
details { margin-top: 20px; }
summary { cursor: pointer; font-weight: 600; }
.tbl { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: .9rem; margin-top: 8px; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-weight: 600; color: var(--muted); }
footer { margin-top: 28px; font-size: .82rem; color: var(--muted); max-width: 75ch; }
@media (prefers-reduced-motion: no-preference) { path.c { transition: fill .15s; } }
</style>
<div class="wrap">
  <header>@@HEADER@@</header>
  <nav class="tabs" id="tabs" aria-label="Maps"></nav>
  <section class="view-head"><h2 id="v-title"></h2><p id="v-sub"></p></section>
  <div class="stage">
    <div class="map-col">
      <div class="map" id="map"><div id="tip" hidden></div>
        <div class="zoom" role="group" aria-label="Map zoom">
          <button type="button" id="zoom-in" aria-label="Zoom in" title="Zoom in">+</button>
          <button type="button" id="zoom-out" aria-label="Zoom out" title="Zoom out">&minus;</button>
          <button type="button" id="zoom-reset" aria-label="Reset zoom" title="Reset zoom">Reset</button>
        </div>
      </div>
      <p class="hint">Use the + and &minus; buttons, or hold Ctrl and turn the mouse wheel, to zoom. Once the map is zoomed in, the wheel zooms and you drag to move the map. On a phone, pinch with two fingers.</p>
    </div>
    <aside>
      <div><h3 id="lg-title">Legend</h3><ul class="legend" id="legend"></ul></div>
      <div id="flt-box"><h3>Show only</h3><div class="filters" id="filters"></div></div>
      <div><h3>Country</h3><div class="readout" id="readout">Point at or tap a country to read its values.</div></div>
    </aside>
  </div>
  <details><summary>All values as a table</summary><div class="tbl"><table id="table"><thead><tr><th>Country</th><th>Map text</th></tr></thead><tbody></tbody></table></div></details>
  <footer>@@FOOTER@@</footer>
</div>
<script type="application/json" id="map-data">@@DATA@@</script>
<script>/* d3 7.9.0, embedded so the page runs offline */
@@D3JS@@
</script>
<script>
(function () {
  var data = JSON.parse(document.getElementById("map-data").textContent);
  var views = {}; data.views.forEach(function (v) { views[v.id] = v; });
  var names = {}; data.countries.forEach(function (c) { if (c.iso3) names[c.iso3] = c.name; });
  var W = 900, H = 640;
  var shapes = data.countries.filter(function (c) { return c.paths && c.paths.length; });
  function feat(c) { return { type: "Feature", properties: c, geometry: { type: "MultiPolygon", coordinates: c.paths } }; }
  var frameIsos = {}; data.views.forEach(function (v) { Object.keys(v.tips).forEach(function (k) { frameIsos[k] = 1; }); });
  var frame = shapes.filter(function (c) { return frameIsos[c.iso3]; }).map(feat);
  var proj = d3.geoAzimuthalEqualArea().rotate([-30, -52]);
  proj.fitExtent([[8, 8], [W - 8, H - 8]], { type: "FeatureCollection", features: frame.length ? frame : shapes.map(feat) });
  var path = d3.geoPath(proj);
  var svg = d3.select("#map").append("svg").attr("viewBox", "0 0 " + W + " " + H).attr("role", "img");
  svg.append("defs").append("clipPath").attr("id", "clip").append("rect").attr("width", W).attr("height", H);
  // the outer group clips to the frame; the inner group carries the zoom transform
  var g = svg.append("g").attr("clip-path", "url(#clip)").append("g");
  g.selectAll("path.ctx").data(shapes.filter(function (c) { return !c.iso3; }).map(feat)).join("path")
    .attr("class", "ctx").attr("d", path);
  var sel = g.selectAll("path.c").data(shapes.filter(function (c) { return c.iso3; }).map(feat)).join("path")
    .attr("class", "c").attr("d", path).attr("data-iso", function (d) { return d.properties.iso3; });
  // the highlight is drawn by one overlay path on top; country paths never move, so the DOM order
  // (and the keyboard Tab order) stays as built
  var hl = g.append("path").attr("class", "hl").attr("aria-hidden", "true").style("display", "none");
  var tip = document.getElementById("tip"), readout = document.getElementById("readout");
  var cur = null, filter = null;

  // Zoom: one transform per map view, so each map keeps its own zoom when you switch tabs.
  var zoomOf = {}, KMAX = 8;
  var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var zoom = d3.zoom().scaleExtent([1, KMAX]).translateExtent([[0, 0], [W, H]])
    .filter(function (ev) {
      // wheel: at full view the page scrolls; Ctrl + wheel (a trackpad pinch arrives as one) zooms in;
      // once zoomed in, the plain wheel zooms
      if (ev.type === "wheel") return ev.ctrlKey || (zoomOf[cur] ? zoomOf[cur].k > 1 : false);
      // touch: two fingers pinch at any zoom; one finger moves the map only once it is zoomed in,
      // so a one-finger drag at full view still scrolls the page
      if (ev.touches) return ev.touches.length > 1 || (zoomOf[cur] ? zoomOf[cur].k > 1 : false);
      return !ev.ctrlKey && !ev.button;
    })
    .on("zoom", function (ev) {
      g.attr("transform", ev.transform);
      if (cur) zoomOf[cur] = ev.transform;
      if (ev.sourceEvent) tip.hidden = true;
      zoomUi(ev.transform.k);
    });
  function zoomUi(k) {
    svg.style("touch-action", k > 1 ? "none" : "pan-x pan-y");
    document.getElementById("zoom-in").disabled = k >= KMAX - 1e-6;
    document.getElementById("zoom-out").disabled = k <= 1 + 1e-6;
    document.getElementById("zoom-reset").disabled = k <= 1 + 1e-6 && !(zoomOf[cur] && (zoomOf[cur].x || zoomOf[cur].y));
  }
  function moved() { return svg.transition().duration(still ? 0 : 250); }
  svg.call(zoom);
  document.getElementById("zoom-in").addEventListener("click", function () { moved().call(zoom.scaleBy, 1.6); });
  document.getElementById("zoom-out").addEventListener("click", function () { moved().call(zoom.scaleBy, 1 / 1.6); });
  document.getElementById("zoom-reset").addEventListener("click", function () { moved().call(zoom.transform, d3.zoomIdentity); });

  function colourOf(v, iso) {
    if (!(iso in v.colour)) return null;
    var k = v.colour[iso];
    for (var i = 0; i < v.legend.length; i++) if (String(v.legend[i].key) === String(k)) return v.legend[i].colour;
    return null;
  }
  function paint() {
    var v = views[cur], members = null;
    if (filter !== null) v.filters.forEach(function (f) { if (f.key === filter) { members = {}; f.members.forEach(function (m) { members[m] = 1; }); } });
    sel.each(function (d) {
      var iso = d.properties.iso3, col = colourOf(v, iso), el = d3.select(this);
      el.style("fill", col || "var(--map-land)")
        .attr("data-coloured", col ? "1" : null)
        .classed("dim", !!members && !members[iso])
        .classed("has-tip", iso in v.tips)
        .attr("tabindex", iso in v.tips ? 0 : null)
        .attr("aria-label", iso in v.tips ? v.tips[iso] : null);
    });
  }
  function show(ev, d) {
    var v = views[cur], t = v.tips[d.properties.iso3] || d.properties.name;
    if (!t) return;
    tip.textContent = t; tip.hidden = false; readout.textContent = t;
    var box = document.getElementById("map").getBoundingClientRect();
    var x = (ev.clientX || box.left + box.width / 2) - box.left + 12, y = (ev.clientY || box.top + 20) - box.top + 12;
    tip.style.left = Math.min(x, box.width - tip.offsetWidth - 4) + "px"; tip.style.top = y + "px";
    d3.select(this).classed("hot", true);
    hl.attr("d", d3.select(this).attr("d")).style("display", null);
  }
  function hide() { tip.hidden = true; d3.select(this).classed("hot", false); hl.style("display", "none"); }
  sel.on("mousemove", show).on("mouseleave", hide).on("focus", show).on("blur", hide).on("click", show);

  function render(id) {
    cur = views[id] ? id : data.views[0].id; filter = null;
    var v = views[cur];
    svg.interrupt().call(zoom.transform, zoomOf[cur] || d3.zoomIdentity);
    document.getElementById("v-title").textContent = v.title;
    document.getElementById("v-sub").textContent = v.subtitle;
    document.getElementById("lg-title").textContent = v.legend_title || "Legend";
    var lg = document.getElementById("legend"); lg.textContent = "";
    v.legend.forEach(function (l) {
      var li = document.createElement("li"), sw = document.createElement("span"), tx = document.createElement("span");
      sw.className = "sw"; sw.style.background = l.colour; tx.textContent = l.text; li.append(sw, tx); lg.append(li);
    });
    var fb = document.getElementById("filters"); fb.textContent = "";
    document.getElementById("flt-box").hidden = !v.filters.length;
    var all = document.createElement("button"); all.type = "button"; all.id = "flt-all"; all.textContent = "All";
    all.setAttribute("aria-pressed", "true"); fb.append(all);
    v.filters.forEach(function (f, i) {
      var b = document.createElement("button"), dot = document.createElement("span"), tx = document.createElement("span");
      b.type = "button"; b.id = "flt-" + i; b.dataset.key = f.key; b.setAttribute("aria-pressed", "false");
      dot.className = "dot"; dot.style.background = f.colour; tx.textContent = f.text; b.append(dot, tx); fb.append(b);
    });
    fb.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () {
        filter = b.dataset.key === undefined ? null : b.dataset.key;
        fb.querySelectorAll("button").forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
        paint();
      });
    });
    document.querySelectorAll("#tabs a").forEach(function (a) {
      if (a.dataset.id === cur) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    var tb = document.querySelector("#table tbody"); tb.textContent = "";
    Object.keys(v.tips).sort(function (a, b) { return (names[a] || a).localeCompare(names[b] || b); }).forEach(function (iso) {
      var tr = document.createElement("tr"), a = document.createElement("td"), b = document.createElement("td");
      a.textContent = names[iso] || iso; b.textContent = v.tips[iso]; tr.append(a, b); tb.append(tr);
    });
    readout.textContent = "Point at or tap a country to read its values."; tip.hidden = true;
    paint();
  }
  var tabs = document.getElementById("tabs");
  data.views.forEach(function (v) {
    var a = document.createElement("a"); a.href = "#map-" + v.id.toLowerCase(); a.dataset.id = v.id;
    a.textContent = (data.tab_letters === false ? "" : "Map " + v.id + ": ") + v.name; tabs.append(a);
  });
  function route() { var m = /^#map-([a-z])$/.exec(location.hash), id = m ? m[1].toUpperCase() : "";
    render(data.views.some(function (v) { return v.id === id; }) ? id : data.views[0].id); }
  window.addEventListener("hashchange", route);
  route();
})();
</script>
"""


if __name__ == "__main__":
    sys.exit(main())
