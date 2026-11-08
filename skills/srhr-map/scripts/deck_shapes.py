"""Shape inventory for the map decks (SRHR map skill, phase d, mode publish).

Lists every shape on decks A to D that carries a value derived from the map register, one row per
(shape, field). The deck is read as a zip file and never opened in PowerPoint or saved.

Kinds, from the shape names the readability build gives (`Country: <name>`, `Layer: not <class> | <name>`):
  tip           ScreenTip on a country shape and on every copy of it (close-up, hover, layer, label,
                badge, dot, rate label, focus and services symbols); field screentip
  label         count label on map B; badge on map C; rate_label on map D; matrix_total on map C's
                matrix slide; field text
  layer_member  a grey copy inside a filter layer "not <class>": the country is NOT in <class>.
                Membership is structure: a value that moves a country to another class needs a shape
                added or removed, which phase (d) never does
  dot, matrix_dot   one stream dot per held stream (structure, as above)
  legend_count  a legend or filter-button text holding a count "(n)"; field text
  fill, focus, svc, chart, rate_bar, title, subtitle, printed_list, footer
                inventoried for review only; the planner does not swap them (editorial text or
                geometry)

Run:  python deck_shapes.py --decks <folder> --master <master_countries.csv> --out <inventory.csv>
"""
import argparse
import csv
import html
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import register_deck_check as rdc  # noqa: E402

COLUMNS = ["deck", "slide", "shape_name", "kind", "iso3_or_key", "indicator", "field", "current", "in_group"]
SP = re.compile(r"<p:sp\b[^>]*>.*?</p:sp>", re.S)
NAME = re.compile(r'<p:cNvPr\b[^>]*\bname="([^"]*)"')
TOOLTIP = re.compile(r'<a:hlink\w+\b[^>]*\btooltip="([^"]*)"')
TEXT = re.compile(r"<a:t>([^<]*)</a:t>")
FILL = re.compile(r"<p:spPr>.*?<a:solidFill><a:srgbClr val=\"(\w+)\"", re.S)
COUNT = re.compile(r"\(\d")
CU = " (close-up)"
# shape-name prefix -> kind of its text value (None: the shape carries only a tip)
TIP_CARRIERS = {"Country: ": "fill", "Close-up: ": "fill", "Hover: ": None, "Label: ": "label",
                "Badge: ": "badge", "Rate label: ": "rate_label", "Focus symbol: ": "focus",
                "Svc: Services circle: ": "svc"}
REVIEW_TEXT = {"Title 1": "title", "Subtitle": "subtitle", "Printed lists": "printed_list"}
D_TIP = ";".join(rdc.D_INDICATORS)


def deck_letter(pptx: Path) -> str:
    m = re.match(r"Map ([A-Z]) ", Path(pptx).name)
    return m.group(1) if m else "?"


def _group_spans(xml: str) -> list:
    spans, stack = [], []
    for m in re.finditer(r"<p:grpSp>|</p:grpSp>", xml):
        if m.group(0) == "<p:grpSp>":
            stack.append(m.start())
        elif stack:
            start = stack.pop()
            if not stack:
                spans.append((start, m.end()))
    return spans


def _country(rest: str) -> str:
    rest = rest[:-len(CU)] if rest.endswith(CU) else rest
    return re.sub(r" #\d+$", "", rest)


def _classify(name: str, text: str, tip, fill):
    """[(kind, country or key, field, current)] for one shape; [] when it carries no register value."""
    out = []
    for pre, text_kind in TIP_CARRIERS.items():
        if name.startswith(pre):
            c = _country(name[len(pre):])
            if tip is not None:
                out.append(("tip", c, "screentip", tip))
            if text_kind == "fill":
                out.append(("fill", c, "fill", fill or ""))
            elif text_kind in ("label", "badge", "rate_label"):
                out.append((text_kind, c, "text", text))
            elif text_kind:
                out.append((text_kind, c, "presence", "yes"))
            return out
    if name.startswith("Layer: ") and " | " in name:
        layer, c = name[len("Layer: "):].split(" | ", 1)
        c = _country(c)
        if tip is not None:
            out.append(("tip", c, "screentip", tip))
        if layer.startswith("not "):
            out.append(("layer_member", c, "presence", layer[len("not "):]))
        else:
            out.append(("fill", c, "fill", fill or ""))
        return out
    if name.startswith("Dot: ") and " | " in name:
        c, key = name[len("Dot: "):].split(" | ", 1)
        if tip is not None:
            out.append(("tip", c, "screentip", tip))
        out.append(("dot", c, "presence", _country(key)))
        return out
    if name.startswith("Matrix dot: ") and " | " in name:
        c, key = name[len("Matrix dot: "):].split(" | ", 1)
        return [("matrix_dot", c, "presence", key)]
    if name.startswith("Matrix total: "):
        return [("matrix_total", name[len("Matrix total: "):], "text", text)]
    for pre, kind in (("Chart dot: ", "chart"), ("Chart label: ", "chart"), ("Rate bar: ", "rate_bar")):
        if name.startswith(pre):
            return [(kind, name[len(pre):], "geometry", text)]
    if name in REVIEW_TEXT and text:
        return [(REVIEW_TEXT[name], name, "text", text)]
    if name.startswith("Footer") and text:
        return [("footer", name, "text", text)]
    if name.startswith(("Filter button", "Legend text: ", "Active ring: ")) and COUNT.search(text):
        return [("legend_count", name.split(": ", 1)[-1], "text", text)]
    return out


def inventory(pptx: Path, names: dict) -> list:
    """Rows (COLUMNS) for every register-derived shape on every slide of one deck."""
    m = deck_letter(pptx)
    rows = []
    with zipfile.ZipFile(pptx) as z:
        slides = sorted((n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                        key=lambda n: int(re.findall(r"\d+", n)[0]))
        for n in slides:
            xml = z.read(n).decode("utf-8")
            groups = _group_spans(xml)
            for s in SP.finditer(xml):
                block = s.group(0)
                nm = NAME.search(block)
                if not nm:
                    continue
                name = html.unescape(nm.group(1))
                tip = TOOLTIP.search(block)
                tip = html.unescape(tip.group(1)) if tip else None
                text = html.unescape("".join(TEXT.findall(block)))
                fill = FILL.search(block)
                in_group = any(a <= s.start() < b for a, b in groups)
                for kind, who, field, current in _classify(name, text, tip, fill.group(1) if fill else None):
                    if kind == "tip":
                        ind = D_TIP if m == "D" else rdc.MAP_INDICATOR.get(m, "")
                    elif kind == "rate_label":
                        ind = rdc.D_INDICATORS[0]
                    else:
                        ind = rdc.MAP_INDICATOR.get(m, "")
                    rows.append({"deck": m, "slide": n.rsplit("/", 1)[-1], "shape_name": name, "kind": kind,
                                 "iso3_or_key": names.get(who, who), "indicator": ind, "field": field,
                                 "current": current, "in_group": "yes" if in_group else "no"})
    return rows


def cross_check(pptx: Path, rows: list) -> list:
    """Country shapes register_deck_check reads that the inventory lacks (must be [])."""
    m = deck_letter(pptx)
    have = {(r["slide"], r["shape_name"]) for r in rows if r["kind"] == "tip"}
    return [f"{m} {slide} Country: {c}" for slide, tips in rdc.deck_tips(pptx) for c in sorted(tips)
            if (slide, f"Country: {c}") not in have]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--decks", type=Path, required=True)
    ap.add_argument("--master", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    names = {r["country"]: r["iso3"] for r in rdc._csv(args.master)}
    rows, missing = [], []
    for m in "ABCD":
        decks = sorted(args.decks.glob(rdc.deck_glob(m)))
        if len(decks) != 1:
            print(f"FAIL map {m}: expected one deck '{rdc.deck_glob(m)}', found {len(decks)}")
            return 1
        got = inventory(decks[0], names)
        missing += cross_check(decks[0], got)
        rows += got
    if args.out.exists():
        print(f"REFUSE: {args.out} exists")
        return 2
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    counts = {}
    for r in rows:
        counts[(r["deck"], r["kind"])] = counts.get((r["deck"], r["kind"]), 0) + 1
    for (m, k), v in sorted(counts.items()):
        print(f"map {m} {k}: {v}")
    print(f"{len(rows)} rows written; {len(missing)} country shape(s) missing against deck_tips")
    for x in missing:
        print(f"  MISSING {x}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
