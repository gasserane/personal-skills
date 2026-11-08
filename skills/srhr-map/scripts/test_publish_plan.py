"""Tests for publish_plan.py (SRHR map skill, phase d). The register and the shape inventory are
built in the test; every name and key is invented, because this repository is public.

The fixture deck agrees with the fixture register, so an unchanged register must plan nothing.

Run:  python test_publish_plan.py
"""
import csv
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import publish_plan as pp  # noqa: E402

CROSSWALK = [("K1", "Stream A"), ("K2", "Stream B")]
DOT = "●  "


def row(iso, ind, value, display=None, year="2026", status="full member"):
    return {"iso3": iso, "member_status": status, "indicator_id": ind, "value": value,
            "value_display": value if display is None else display, "reference_year": year}


def register():
    return [
        row("XA1", "ippf_membership", "Class P"), row("YB2", "ippf_membership", "Class Q"),
        row("XA1", "ippf_grant_streams_count", "4"), row("YB2", "ippf_grant_streams_count", "2"),
        row("XA1", "ippf_funding_streams", "1", "K1"), row("YB2", "ippf_funding_streams", "2", "K1, K2"),
        row("XA1", "ippf_funding_streams_partner", "K2", "K2 with Yoland (row 9)"),
        row("XA1", "ecdc_hiv_diagnosis_rate", "2.0", year="2015"),
        row("XA1", "ecdc_hiv_diagnosis_rate", "3.0", year="2024"),
        row("XA1", "ippf_bp_hiv_focus", "high"), row("XA1", "ippf_hiv_services", "12", "12 (note)"),
        row("YB2", "ecdc_hiv_diagnosis_rate", "4.0", year="2015"),
        row("YB2", "ecdc_hiv_diagnosis_rate", "2.0", year="2024"),
        row("YB2", "ippf_bp_hiv_focus", "not assessed"), row("YB2", "ippf_hiv_services", "0"),
    ]


def inv(deck, shape, kind, key, field, current, slide="slide1.xml"):
    return {"deck": deck, "slide": slide, "shape_name": shape, "kind": kind, "iso3_or_key": key,
            "indicator": "", "field": field, "current": current, "in_group": "no"}


TIPS = {
    "A": {"XA1": "Xaland: Class P", "YB2": "Yoland: Class Q"},
    "B": {"XA1": "Xaland: 4 grant streams in 2026", "YB2": "Yoland: 2 grant streams in 2026"},
    "C": {"XA1": "Xaland: full member. Grants Jan to Aug 2026: Stream A. "
                 "Partner country on a joint Stream B grant led by Yoland.",
          "YB2": "Yoland: full member. Grants Jan to Aug 2026: Stream A, Stream B."},
    "D": {"XA1": "Xaland: 2024 rate 3.0 per 100,000; trend +50% since 2015; plan focus: high; HIV services 2025: 12",
          "YB2": "Yoland: 2024 rate 2.0 per 100,000; trend -50% since 2015; plan focus: not assessed; "
                 "HIV services 2025: 0"},
}
NAME = {"XA1": "Xaland", "YB2": "Yoland"}


def inventory():
    rows = []
    for deck, tips in TIPS.items():
        for iso, tip in tips.items():
            rows.append(inv(deck, f"Country: {NAME[iso]}", "tip", iso, "screentip", tip))
            rows.append(inv(deck, f"Country: {NAME[iso]}", "fill", iso, "fill", "00313C"))
    rows += [
        inv("A", "Layer: not Class Q | Xaland", "layer_member", "XA1", "presence", "Class Q"),
        inv("A", "Layer: not Class P | Yoland", "layer_member", "YB2", "presence", "Class P"),
        inv("A", "Filter button: p", "legend_count", "p", "text", "Class P (1)"),
        inv("A", "Filter button: q", "legend_count", "q", "text", "Class Q (1)"),
        inv("A", "Title 1", "title", "Title 1", "text", "Members"),
        inv("B", "Label: Xaland", "label", "XA1", "text", "4"),
        inv("B", "Label: Yoland", "label", "YB2", "text", "2"),
        inv("B", "Layer: not 2 grant streams | Xaland", "layer_member", "XA1", "presence", "2 grant streams"),
        inv("B", "Layer: not 4+ grant streams | Yoland", "layer_member", "YB2", "presence", "4+ grant streams"),
        inv("B", "Filter button: s2", "legend_count", "s2", "text", "2 grant streams (1)"),
        inv("B", "Filter button: s4", "legend_count", "s4", "text", "4+ grant streams (1)"),
        inv("C", "Badge: Xaland", "badge", "XA1", "text", "1"),
        inv("C", "Badge: Yoland", "badge", "YB2", "text", "2"),
        # a partner (half dot) country is NOT greyed in that stream's layer (as on the real deck);
        # a country holding neither stream would sit in both "not" layers
        inv("C", "Layer: not Stream B | Zcland", "layer_member", "ZC3", "presence", "Stream B"),
        inv("C", "Dot: Xaland | K1", "dot", "XA1", "presence", "K1"),
        inv("C", "Dot: Xaland | K2 (half)", "dot", "XA1", "presence", "K2 (half)"),
        inv("C", "Dot: Xaland | K2 (half fill)", "dot", "XA1", "presence", "K2 (half fill)"),
        inv("C", "Dot: Yoland | K1", "dot", "YB2", "presence", "K1"),
        inv("C", "Dot: Yoland | K2", "dot", "YB2", "presence", "K2"),
        inv("C", "Matrix dot: Xaland | K1", "matrix_dot", "XA1", "presence", "K1", "slide3.xml"),
        inv("C", "Matrix dot: Xaland | K2 (half)", "matrix_dot", "XA1", "presence", "K2 (half)", "slide3.xml"),
        inv("C", "Matrix dot: Yoland | K1", "matrix_dot", "YB2", "presence", "K1", "slide3.xml"),
        inv("C", "Matrix dot: Yoland | K2", "matrix_dot", "YB2", "presence", "K2", "slide3.xml"),
        inv("C", "Matrix total: Xaland", "matrix_total", "XA1", "text", "1", "slide3.xml"),
        inv("C", "Matrix total: Yoland", "matrix_total", "YB2", "text", "2", "slide3.xml"),
        inv("C", "Filter button: K1", "legend_count", "K1", "text", f"{DOT}Stream A (2)"),
        inv("C", "Filter button: K2", "legend_count", "K2", "text", f"{DOT}Stream B (1 + 1 half)"),
        inv("C", "Legend text: full member", "legend_count", "full member", "text", "Full member (2)"),
        inv("D", "Rate label: Xaland", "rate_label", "XA1", "text", "3.0"),
        inv("D", "Focus symbol: Xaland #1", "focus", "XA1", "presence", "yes"),
        inv("D", "Chart dot: Yoland", "chart", "YB2", "geometry", ""),
    ]
    return rows


def set_value(rows, iso, ind, value, display=None, year=None):
    out = []
    for r in rows:
        if r["iso3"] == iso and r["indicator_id"] == ind and (year is None or r["reference_year"] == year):
            r = dict(r, value=value, value_display=value if display is None else display)
        out.append(r)
    return out


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    results = []

    def record(case, ok, detail=""):
        results.append(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {case}" + (f": {detail}" if not ok else ""))

    # --- unchanged register: nothing to swap, no structure line ---
    swaps, structure, _ = pp.plan(register(), inventory(), CROSSWALK)
    record("unchanged_register_zero_rows", swaps == [] and structure == [], (swaps, structure))

    # --- one planted value change: exactly one swap row, the span replaced inside the tip ---
    reg = set_value(register(), "YB2", "ecdc_hiv_diagnosis_rate", "2.2", year="2024")
    swaps, structure, _ = pp.plan(reg, inventory(), CROSSWALK)
    want = TIPS["D"]["YB2"].replace("rate 2.0", "rate 2.2").replace("-50%", "-45%")
    record("planted_change_one_swap_row", len(swaps) == 1 and structure == [], (swaps, structure))
    record("planted_change_swap_values", swaps and (swaps[0]["deck"], swaps[0]["shape_name"], swaps[0]["field"],
                                                    swaps[0]["old"], swaps[0]["new"])
           == ("D", "Country: Yoland", "screentip", TIPS["D"]["YB2"], want), swaps)

    # --- a within-class change swaps tip and label, no structure (4+ stays 4+) ---
    reg = set_value(register(), "XA1", "ippf_grant_streams_count", "5")
    swaps, structure, _ = pp.plan(reg, inventory(), CROSSWALK)
    got = sorted((s["kind"], s["new"]) for s in swaps)
    record("within_class_tip_and_label", got == [("label", "5"), ("tip", "Xaland: 5 grant streams in 2026")]
           and structure == [], (got, structure))

    # --- a rate label follows the 2024 rate ---
    reg = set_value(register(), "XA1", "ecdc_hiv_diagnosis_rate", "3.3", year="2024")
    swaps, structure, _ = pp.plan(reg, inventory(), CROSSWALK)
    record("rate_label_swapped", ("rate_label", "3.3") in [(s["kind"], s["new"]) for s in swaps], swaps)

    # --- a class change is structure (phase e), and the legend count still follows it ---
    reg = set_value(register(), "YB2", "ippf_grant_streams_count", "3")
    swaps, structure, _ = pp.plan(reg, inventory(), CROSSWALK)
    record("class_change_is_structure", any("YB2" in s for s in structure), structure)
    legend = [s for s in swaps if s["kind"] == "legend_count"]
    record("legend_count_follows_class_change", [(s["old"], s["new"]) for s in legend]
           == [("2 grant streams (1)", "2 grant streams (0)")], legend)

    reg = set_value(register(), "XA1", "ippf_membership", "Class Q")
    _, structure, _ = pp.plan(reg, inventory(), CROSSWALK)
    record("membership_change_is_structure", any("XA1" in s for s in structure), structure)

    reg = set_value(register(), "XA1", "ippf_funding_streams", "2", "K1, K2")
    _, structure, _ = pp.plan(reg, inventory(), CROSSWALK)
    record("stream_change_is_structure", any("XA1" in s for s in structure), structure)

    reg = set_value(register(), "YB2", "ippf_bp_hiv_focus", "high")
    _, structure, _ = pp.plan(reg, inventory(), CROSSWALK)
    record("focus_change_is_structure", any("YB2" in s for s in structure), structure)

    # --- a new invented country in the register: structure line, never a new shape ---
    reg = register() + [row("ZC3", "ecdc_hiv_diagnosis_rate", "1.0", year="2024")]
    swaps, structure, _ = pp.plan(reg, inventory(), CROSSWALK)
    record("new_country_is_structure", any("ZC3" in s for s in structure)
           and not any(s["shape_name"].endswith("Zcland") for s in swaps), structure)

    # --- a shape with no register row is structure too ---
    reg = [r for r in register() if not (r["iso3"] == "YB2" and r["indicator_id"] == "ippf_membership")]
    _, structure, _ = pp.plan(reg, inventory(), CROSSWALK)
    record("shape_without_register_row_is_structure", any("YB2" in s and "map A" in s for s in structure), structure)

    # --- review counts: titles always, plus review shapes of a changed country ---
    reg = set_value(register(), "YB2", "ecdc_hiv_diagnosis_rate", "2.2", year="2024")
    _, _, review = pp.plan(reg, inventory(), CROSSWALK)
    record("review_counts", review.get(("A", "title")) == 1 and review.get(("D", "chart")) == 1, review)

    # --- CLI: exit 0 on a clean plan, exit 2 on structure; swap CSV written, never overwritten ---
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        write_csv(t / "inv.csv", inventory())
        write_csv(t / "cw.csv", [{"key": k, "label": v} for k, v in CROSSWALK])
        write_csv(t / "reg.csv", set_value(register(), "XA1", "ippf_grant_streams_count", "5"))
        write_csv(t / "bad.csv", register() + [row("ZC3", "ecdc_hiv_diagnosis_rate", "1.0", year="2024")])
        args = ["--inventory", str(t / "inv.csv"), "--crosswalk", str(t / "cw.csv")]
        code = pp.main(["--register", str(t / "reg.csv"), "--out", str(t / "plan.csv")] + args)
        with open(t / "plan.csv", encoding="utf-8", newline="") as f:
            written = list(csv.DictReader(f))
        record("cli_exit_0_and_csv", code == 0 and len(written) == 2
               and list(written[0]) == pp.COLUMNS, (code, written))
        record("cli_refuses_overwrite", pp.main(["--register", str(t / "reg.csv"), "--out", str(t / "plan.csv")]
                                                + args) == 1)
        record("cli_exit_2_on_structure", pp.main(["--register", str(t / "bad.csv")] + args) == 2)

    print(f"{sum(results)}/{len(results)} cases ok")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
