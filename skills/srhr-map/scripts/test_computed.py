"""Tests for computed.py (SRHR map skill, phase d). Every name and key is invented, because this
repository is public.

Run:  python test_computed.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import computed as cp  # noqa: E402

CROSSWALK = [("K1", "Stream A"), ("K2", "Stream B (x)")]


def row(iso, ind, value, display=None, year="2026", status="full member"):
    return {"iso3": iso, "member_status": status, "indicator_id": ind, "value": value,
            "value_display": value if display is None else display, "reference_year": year}


def main():
    results = []

    def record(case, ok, detail=""):
        results.append(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {case}" + (f": {detail}" if not ok else ""))

    # --- map B classes: 0..3 by count, then one top class ---
    record("b_class_singular", cp.b_class(1) == "1 grant stream", cp.b_class(1))
    record("b_class_plural", cp.b_class(3) == "3 grant streams", cp.b_class(3))
    record("b_class_top", cp.b_class(6) == "4+ grant streams", cp.b_class(6))

    # --- legend counts = register rows per class; withdrawn rows never count ---
    b = [row("XA1", "ippf_grant_streams_count", "2"), row("YB2", "ippf_grant_streams_count", "2"),
         row("ZC3", "ippf_grant_streams_count", "2", status="withdrawn")]
    got = cp.class_counts("B", b, CROSSWALK)
    record("legend_count_per_class", got == {"2 grant streams": (2, 0)}, got)
    b_moved = [dict(r, value="3", value_display="3") if r["iso3"] == "YB2" else r for r in b]
    got = cp.class_counts("B", b_moved, CROSSWALK)
    record("legend_count_follows_class_change", got == {"2 grant streams": (1, 0), "3 grant streams": (1, 0)}, got)

    a = [row("XA1", "ippf_membership", "Class P"), row("YB2", "ippf_membership", "Class P"),
         row("ZC3", "ippf_membership", "Class Q")]
    got = cp.class_counts("A", a, CROSSWALK)
    record("legend_count_map_a", got == {"Class P": (2, 0), "Class Q": (1, 0)}, got)

    c = [row("XA1", "ippf_funding_streams", "1", "K1"), row("YB2", "ippf_funding_streams", "2", "K1, K2"),
         row("ZC3", "ippf_funding_streams", "0", "none", status="associate member"),
         row("XA1", "ippf_funding_streams_partner", "K2", "K2 with Yoland (row 9)")]
    got = cp.class_counts("C", c, CROSSWALK)
    want = {"K1": (2, 0), "K2": (1, 1), "full member": (2, 0), "associate member": (1, 0)}
    record("legend_count_map_c_half_and_status", got == want, got)

    got = cp.country_classes("C", c, CROSSWALK)
    record("country_classes_c_held_labels", got == {"XA1": {"Stream A"}, "YB2": {"Stream A", "Stream B (x)"},
                                                     "ZC3": set()}, got)

    # --- legend text: only the trailing count changes; a label with brackets survives ---
    record("legend_text_plain", cp.legend_text("Class P (13)", 12) == "Class P (12)")
    record("legend_text_half", cp.legend_text("●  Stream A (16 + 5 half)", 17, 4)
           == "●  Stream A (17 + 4 half)")
    record("legend_text_half_gone", cp.legend_text("●  Stream A (8 + 1 half)", 8, 0) == "●  Stream A (8)")
    record("legend_text_bracketed_label", cp.legend_text("●  Stream B (x) (2)", 3) == "●  Stream B (x) (3)")
    record("legend_label", cp.legend_label("●  Stream B (x) (2)") == "Stream B (x)")
    try:
        cp.legend_text("Class P", 1)
        record("legend_text_without_count_raises", False, "no error")
    except ValueError:
        record("legend_text_without_count_raises", True)

    # --- trend computed from the 2015 and 2024 rates ---
    d = [row("XA1", "ecdc_hiv_diagnosis_rate", "2.0", year="2015"), row("XA1", "ecdc_hiv_diagnosis_rate", "3.0",
                                                                     year="2024")]
    record("trend_from_rates", cp.trend(d, "XA1") == "+50%", cp.trend(d, "XA1"))
    record("trend_no_data", cp.trend(d, "YB2") == "no data", cp.trend(d, "YB2"))

    # --- title templates carry no typed number ---
    record("render_fills_values", cp.render("{n} members in {year}", n=36, year=2027) == "36 members in 2027")
    try:
        cp.render("Members in 2026: {n}", n=36)
        record("render_template_with_digit_raises", False, "no error")
    except ValueError:
        record("render_template_with_digit_raises", True)

    print(f"{sum(results)}/{len(results)} cases ok")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
