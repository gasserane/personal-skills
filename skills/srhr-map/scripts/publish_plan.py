"""Swap planner for the map decks (SRHR map skill, phase d, mode publish; read-only).

register + shape inventory (deck_shapes.py) + crosswalk -> swap list, one row per shape property
whose value must change: deck, slide, shape_name, kind, field, old, new.

What it swaps (within-class changes only):
  tip           span replacement inside the existing ScreenTip, using register_deck_check's regex
                groups, so every sentence variant on the deck is kept word for word
  label (B), badge and matrix_total (C), rate_label (D)    the text, from the register value
  legend_count  only the trailing "(n)" or "(n + k half)", from computed.class_counts

What it never swaps: a change that moves a country between filter classes (layer copies, stream
dots, matrix dots, membership fill), a change of D plan focus or services (their symbols), a tip
whose sentence form must change, a country on one side only. Each goes to a "structure change:
phase (e)" line and the plan exits 2, because the swap may not add or delete shapes.

Titles, subtitles, printed lists, footers, fills and the D chart, bar, focus and services shapes are
reported as review counts: titles always, the others for countries whose value changed.

Run:  python publish_plan.py --register <csv> --inventory <csv> --crosswalk <csv> [--out <swap csv>]
Exit 0: plan clean (possibly empty). Exit 2: structure lines. Exit 1: input problem.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import computed as cp  # noqa: E402
import register_deck_check as rdc  # noqa: E402

COLUMNS = ["deck", "slide", "shape_name", "kind", "field", "old", "new"]
TEXT_KINDS = {"label": ("ippf_grant_streams_count", None), "badge": ("ippf_funding_streams", None),
              "matrix_total": ("ippf_funding_streams", None), "rate_label": (rdc.D_INDICATORS[0], "2024")}
ALWAYS_REVIEW = ("title", "subtitle", "printed_list", "footer")
CHANGE_REVIEW = ("fill", "chart", "rate_bar", "focus", "svc")


class Structure(Exception):
    pass


def _spans(text, edits):
    """Apply [(start, end, new)] right to left."""
    for a, b, new in sorted(edits, reverse=True):
        text = text[:a] + new + text[b:]
    return text


def new_tip(m, tip, by, iso, crosswalk):
    """The tip with register values put into its value spans; Structure when that is not enough."""
    label, order = dict(crosswalk), {k: i for i, (k, _) in enumerate(crosswalk)}
    if m == "A":
        row = rdc._one(by, iso, "ippf_membership")
        head = tip.split(": ", 1)[0] if ": " in tip else None
        if head is None:
            raise Structure(f"cannot read tip {tip!r}")
        return f"{head}: {row['value_display']}"
    if m == "B":
        row = rdc._one(by, iso, "ippf_grant_streams_count")
        mm = rdc.B_TIP.search(tip)
        if not mm:
            raise Structure(f"cannot read tip {tip!r}")
        n = int(row["value"])
        return _spans(tip, [(*mm.span(), f": {n} grant stream{'' if n == 1 else 's'} in {row['reference_year']}")])
    if m == "C":
        row = rdc._one(by, iso, "ippf_funding_streams")
        mm = rdc.C_TIP.match(tip)
        if not mm:
            raise Structure(f"cannot read tip {tip!r}")
        keys = cp.stream_keys(row["value_display"])
        if any(k not in label for k in keys):
            raise Structure(f"streams {[k for k in keys if k not in label]} have no crosswalk label")
        want = ", ".join(label[k] for k in sorted(keys, key=order.get))
        if bool(want) != (mm.group(2) is not None):
            raise Structure("tip sentence form must change (streams present vs none)")
        reg_half = set()
        for h in by.get(iso, {}).get("ippf_funding_streams_partner", []):
            lead = re.match(r".+? with (.+?) \(row", h["value_display"])
            reg_half.add((label.get(h["value"], h["value"]), lead.group(1) if lead else ""))
        if set(rdc.C_PARTNER.findall(mm.group(3) or "")) != reg_half:
            raise Structure("partner (half dot) sentence must change")
        edits = [(*mm.span(1), row["member_status"])]
        if want:
            edits.append((*mm.span(2), want))
        return _spans(tip, edits)
    rate = rdc._one(by, iso, rdc.D_INDICATORS[0], 2024)
    mm = rdc.D_RATE.search(tip)
    if not mm:
        raise Structure(f"cannot read tip {tip!r}")
    edits = [(*mm.span(1), rate["value_display"] if rate else "no data"), (*mm.span(2), rdc._trend(by, iso))]
    status = by[iso][next(iter(by[iso]))][0]["member_status"]
    if status != "withdrawn":
        focus, services = rdc._one(by, iso, "ippf_bp_hiv_focus"), rdc._one(by, iso, "ippf_hiv_services")
        fm, sm = rdc.D_FOCUS.search(tip), rdc.D_SERVICES.search(tip)
        if (fm.group(1) if fm else None) != (focus["value_display"] if focus else None):
            raise Structure("plan focus changed (focus symbol)")
        if (sm.group(1) if sm else None) != (services["value_display"].split(" (")[0] if services else None):
            raise Structure("HIV services changed (services symbol)")
    return _spans(tip, edits)


def _in_register(m, by):
    if m in rdc.MAP_INDICATOR:
        ind = rdc.MAP_INDICATOR[m]
        return {iso for iso, rows in by.items() if ind in rows and rows[ind][0]["member_status"] != "withdrawn"}
    return {iso for iso, rows in by.items() if any(i in rows for i in rdc.D_INDICATORS)}


def _class_lines(m, deck_rows, register_rows, crosswalk):
    """Structure lines for countries whose filter class on the deck differs from the register."""
    lines = []
    classes = cp.country_classes(m, register_rows, crosswalk)
    layers = [r for r in deck_rows if r["kind"] == "layer_member"]
    names = {r["current"] for r in layers}
    if m == "C":  # a stream every country holds has no "not" copies: its filter button names the layer
        buttons = {r["iso3_or_key"] for r in deck_rows if r["kind"] == "legend_count"}
        names |= {v for k, v in crosswalk if k in buttons}
    layer_classes = dict(classes)
    if m == "C":  # a partner (half dot) country is not greyed in that stream's layer
        label = dict(crosswalk)
        for iso, keys in cp.partner_keys(register_rows).items():
            layer_classes[iso] = layer_classes.get(iso, set()) | {label.get(k, k) for k in keys}
    for slide in sorted({r["slide"] for r in layers}):
        on = {r["iso3_or_key"] for r in deck_rows if r["slide"] == slide and r["kind"] == "tip"}
        for iso in sorted(on & set(layer_classes)):
            got = {r["current"] for r in layers if r["slide"] == slide and r["iso3_or_key"] == iso}
            want = names - layer_classes[iso]
            if got != want or not layer_classes[iso] <= names:
                lines.append(f"map {m} {slide} {iso}: class {sorted(layer_classes[iso])} needs layer copies "
                             f"not {sorted(want)}, deck has not {sorted(got)}")
    if m == "C":
        full = {iso: {k for k, v in crosswalk if v in labels} for iso, labels in classes.items()}
        half = cp.partner_keys(register_rows)
        for kind in ("dot", "matrix_dot"):
            dots = [r for r in deck_rows if r["kind"] == kind]
            for slide in sorted({r["slide"] for r in dots}):
                on = {r["iso3_or_key"] for r in deck_rows if r["slide"] == slide and r["kind"] in ("tip", kind)}
                for iso in sorted(on & set(classes)):
                    mine = [r["current"] for r in dots if r["slide"] == slide and r["iso3_or_key"] == iso]
                    got_f = {c for c in mine if "(half" not in c}
                    got_h = {c.split(" (half")[0] for c in mine if "(half" in c}
                    if (got_f, got_h) != (full.get(iso, set()), half.get(iso, set())):
                        lines.append(f"map C {slide} {iso}: {kind}s full {sorted(got_f)} half {sorted(got_h)}, "
                                     f"register full {sorted(full.get(iso, set()))} "
                                     f"half {sorted(half.get(iso, set()))}")
    return lines


def plan(register_rows, inventory_rows, crosswalk):
    """(swaps, structure lines, review counts {(deck, kind): n})."""
    by = rdc._index(register_rows)
    swaps, structure, changed = [], [], set()

    def swap(r, new):
        if new != r["current"]:
            swaps.append({"deck": r["deck"], "slide": r["slide"], "shape_name": r["shape_name"], "kind": r["kind"],
                          "field": r["field"], "old": r["current"], "new": new})
            changed.add((r["deck"], r["iso3_or_key"]))

    for m in "ABCD":
        deck = [r for r in inventory_rows if r["deck"] == m]
        if not deck:
            continue
        in_reg = _in_register(m, by)
        tips = [r for r in deck if r["kind"] == "tip"]
        for slide in sorted({r["slide"] for r in tips}):
            on = {r["iso3_or_key"] for r in tips if r["slide"] == slide}
            structure += [f"map {m} {slide} {iso}: in the register, no shape on the deck" for iso in sorted(in_reg - on)]
            structure += [f"map {m} {slide} {iso}: shape on the deck, no register row" for iso in sorted(on - in_reg)]
        for r in tips:
            if r["iso3_or_key"] not in in_reg:
                continue
            try:
                swap(r, new_tip(m, r["current"], by, r["iso3_or_key"], crosswalk))
            except Structure as e:
                line = f"map {m} {r['slide']} {r['iso3_or_key']}: {e}"
                if line not in structure:
                    structure.append(line)
                changed.add((m, r["iso3_or_key"]))
        for r in deck:
            if r["kind"] in TEXT_KINDS and r["iso3_or_key"] in in_reg:
                ind, year = TEXT_KINDS[r["kind"]]
                row = rdc._one(by, r["iso3_or_key"], ind, year)
                if row:
                    swap(r, row["value_display"] if r["kind"] == "rate_label" else row["value"])
        class_lines = _class_lines(m, deck, register_rows, crosswalk)
        structure += class_lines
        changed |= {(m, line.split()[3].rstrip(":")) for line in class_lines}
        counts = cp.class_counts(m, register_rows, crosswalk)
        legends = [r for r in deck if r["kind"] == "legend_count"]
        shown = set()
        for r in legends:
            key = r["iso3_or_key"] if m == "C" else cp.legend_label(r["current"])
            shown.add(key)
            n, half = counts.get(key, (0, 0))
            swap(r, cp.legend_text(r["current"], n, half))
        if legends:
            structure += [f"map {m}: class {k!r} has members but no legend shape"
                          for k in sorted(counts) if k not in shown]

    review = {}
    for r in inventory_rows:
        if r["kind"] in ALWAYS_REVIEW or (r["kind"] in CHANGE_REVIEW and (r["deck"], r["iso3_or_key"]) in changed):
            review[(r["deck"], r["kind"])] = review.get((r["deck"], r["kind"]), 0) + 1
    return swaps, structure, review


def _csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--register", type=Path, required=True)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--crosswalk", type=Path, required=True)
    ap.add_argument("--out", type=Path, help="swap list CSV to write (refused if it exists)")
    args = ap.parse_args(argv)
    if args.out and args.out.exists():
        print(f"REFUSE: {args.out} exists")
        return 1
    crosswalk = [(r["key"], r["label"]) for r in _csv(args.crosswalk)]
    swaps, structure, review = plan(_csv(args.register), _csv(args.inventory), crosswalk)
    counts = {}
    for s in swaps:
        counts[(s["deck"], s["kind"])] = counts.get((s["deck"], s["kind"]), 0) + 1
    for (m, k), v in sorted(counts.items()):
        print(f"swap map {m} {k}: {v}")
    for line in structure:
        print(f"structure change: phase (e): {line}")
    for (m, k), v in sorted(review.items()):
        print(f"review (not swapped) map {m} {k}: {v}")
    print(f"{len(swaps)} swap row(s); {len(structure)} structure line(s)")
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(swaps)
    return 2 if structure else 0


if __name__ == "__main__":
    sys.exit(main())
