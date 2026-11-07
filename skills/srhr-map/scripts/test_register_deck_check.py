"""Tests for register_deck_check.py (SRHR map skill, phase b). Synthetic register and tips only;
country and stream names are made up, because this repository is public.

Run:  python test_register_deck_check.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import register_deck_check as rc  # noqa: E402

NAMES = {"Country One": "ONE", "Country Two": "TWO", "Country Gone": "GON"}
CROSS = [("K1", "Stream one, part 1"), ("K2", "Stream two"), ("K3", "Stream three")]


def r(iso3, indicator, value, display, year, status="full member"):
    return {"iso3": iso3, "indicator_id": indicator, "value": value, "value_display": display,
            "reference_year": str(year), "member_status": status}


REG = [
    r("ONE", "ippf_membership", "MA with core grant", "MA with core grant", 2026),
    r("TWO", "ippf_membership", "Collaborative Partner", "Collaborative Partner", 2026, "Collaborative Partner"),
    r("GON", "ippf_membership", "MA without core grant", "MA without core grant", 2026, "withdrawn"),
    r("ONE", "ippf_grant_streams_count", "4", "4 (a, b, c, d)", 2026),
    r("TWO", "ippf_grant_streams_count", "1", "1 (a)", 2026, "Collaborative Partner"),
    r("GON", "ippf_grant_streams_count", "0", "0 (none)", 2026, "withdrawn"),
    r("ONE", "ippf_funding_streams", "2", "K3, K1", 2026),
    r("ONE", "ippf_funding_streams_partner", "K2", "K2 with Country Two (row 4)", 2026),
    r("TWO", "ippf_funding_streams", "0", "none", 2026, "Collaborative Partner"),
    r("GON", "ippf_funding_streams", "0", "none", 2026, "withdrawn"),
    r("ONE", "ecdc_hiv_diagnosis_rate", "3.3", "3.3", 2015),
    r("ONE", "ecdc_hiv_diagnosis_rate", "4.4", "4.4", 2024),
    r("ONE", "ippf_bp_hiv_focus", "high", "high", 2026),
    r("ONE", "ippf_hiv_services", "1035", "1,035 (2024: 1,261)", 2025),
    r("TWO", "ippf_bp_hiv_focus", "not assessed", "not assessed", 2026, "Collaborative Partner"),
    r("TWO", "ippf_hiv_services", "", "no service data (2024: no service data)", 2025, "Collaborative Partner"),
    r("GON", "ecdc_hiv_diagnosis_rate", "9.3", "9.3", 2015, "withdrawn"),
    r("GON", "ecdc_hiv_diagnosis_rate", "6.6", "6.6", 2024, "withdrawn"),
]
TIPS = {
    "A": {"Country One": "Country One: MA with core grant", "Country Two": "Country Two: Collaborative Partner"},
    "B": {"Country One": "Country One: 4 grant streams in 2026", "Country Two": "Country Two: 1 grant stream in 2026"},
    "C": {"Country One": "Country One: full member. Grants Jan to Aug 2026: Stream one, part 1, Stream three. "
                         "Partner country on a joint Stream two grant led by Country Two.",
          "Country Two": "Country Two: Collaborative Partner. No grant stream Jan to Aug 2026."},
    "D": {"Country One": "Country One: 2024 rate 4.4 per 100,000; trend +33% since 2015; plan focus: high; "
                         "HIV services 2025: 1,035",
          "Country Two": "Country Two: 2024 rate: no data; trend: no data; plan focus: not assessed; "
                         "HIV services 2025: no service data",
          "Country Gone": "Country Gone: 2024 rate 6.6 per 100,000; trend -29% since 2015. The MA withdrew "
                          "from the federation in 2026: no plan focus, no HIV services shown."},
}


def run(m, reg=REG, tips=None):
    return rc.compare(m, reg, (tips or TIPS)[m], NAMES, CROSS)


def main():
    results = []

    def record(case, ok, detail=""):
        results.append(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {case}: {detail}")

    for m in "ABCD":
        got = run(m)
        record(f"clean_agrees_{m}", not got, f"problems {got}")

    reg = [dict(x, value="5", value_display="5 (a, b, c, d, e)") if (x["iso3"], x["indicator_id"]) ==
           ("ONE", "ippf_grant_streams_count") else x for x in REG]
    got = run("B", reg)
    record("planted_value", len(got) == 1 and "Country One" in got[0] and "map B" in got[0], f"problems {got}")

    tips = dict(TIPS, A={"Country One": TIPS["A"]["Country One"]})
    got = run("A", tips=tips)
    record("country_missing_on_deck", len(got) == 1 and "Country Two" in got[0], f"problems {got}")

    tips = dict(TIPS, A=dict(TIPS["A"], **{"Country Gone": "Country Gone: MA without core grant"}))
    got = run("A", tips=tips)
    record("withdrawn_shown_on_membership_map", len(got) == 1 and "withdrawn" in got[0], f"problems {got}")

    reg = [dict(x, value_display="moderate", value="moderate") if (x["iso3"], x["indicator_id"]) ==
           ("ONE", "ippf_bp_hiv_focus") else x for x in REG]
    got = run("D", reg)
    record("focus_compared_regardless_of_tick", len(got) == 1 and "focus" in got[0], f"problems {got}")

    reg = [dict(x, value="3.0", value_display="3.0") if (x["iso3"], x["indicator_id"], x["reference_year"]) ==
           ("ONE", "ecdc_hiv_diagnosis_rate", "2015") else x for x in REG]
    got = run("D", reg)
    record("trend_recomputed_from_register", len(got) == 1 and "trend" in got[0], f"problems {got}")

    reg = [dict(x, value_display="K1, K2") if (x["iso3"], x["indicator_id"]) == ("ONE", "ippf_funding_streams")
           else x for x in REG]
    got = run("C", reg)
    record("stream_list_with_commas_in_labels", len(got) == 1 and "streams" in got[0], f"problems {got}")

    reg = [x for x in REG if x["indicator_id"] != "ippf_funding_streams_partner"]
    got = run("C", reg)
    record("partner_dot_missing_in_register", len(got) == 1 and "partner" in got[0], f"problems {got}")

    reg = [dict(x, member_status="associate member") if (x["iso3"], x["indicator_id"]) == ("ONE", "ippf_funding_streams")
           else x for x in REG]
    got = run("C", reg)
    record("member_status_compared", len(got) == 1 and "status" in got[0], f"problems {got}")

    print(f"{sum(results)}/{len(results)} cases ok")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
