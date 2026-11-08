"""Planted tests for compare_register.py (SRHR map skill, phase c).

Invented countries and values only. Run:  python test_compare_register.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import compare_register as cr  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ': ' + detail}")
    if not cond:
        FAILS.append(name)


def row(iso3, ind, year, value, display=None, **kw):
    r = {"iso3": iso3, "indicator_id": ind, "reference_year": str(year), "value": str(value),
         "value_display": display if display is not None else str(value), "ticked_by": "", "_link": "file.csv"}
    r.update(kw)
    return r


SVC = "ippf_hiv_services"
COV = {SVC: {"year": "2025", "link": "file.csv"}}


def test_unchanged_is_not_a_change():
    base = [row("XAA", SVC, 2025, 10, "10 (2024: 9)")]
    new = [row("XAA", SVC, 2025, 10, "10")]
    check("same key, same value -> no change (display text ignored)", cr.compare(base, new, COV) == [],
          str(cr.compare(base, new, COV)))


def test_new_year_rows_grouped_in_one_line():
    base = [row(i, SVC, 2024, 100) for i in ("XAA", "XBB", "XCC")]
    new = [row("XAA", SVC, 2025, 110), row("XBB", SVC, 2025, 90), row("XCC", SVC, 2025, 120)]
    changes = cr.compare(base, new, COV)
    lines = cr.group_changes(changes)
    check("three new-year rows are 'new'", [c.kind for c in changes] == ["new"] * 3, str(changes))
    check("new rows of one indicator and year form ONE line", len(lines) == 1 and len(lines[0].change_ids) == 3,
          str(lines))


def test_big_change_gets_own_line():
    base = [row("XAA", SVC, 2024, 100), row("XBB", SVC, 2024, 100)]
    new = [row("XAA", SVC, 2025, 110), row("XBB", SVC, 2025, 400)]
    lines = cr.group_changes(cr.compare(base, new, COV))
    sizes = sorted(len(l.change_ids) for l in lines)
    check("a value moving more than 50% gets its own line", len(lines) == 2 and sizes == [1, 1], str(lines))


def test_revised_value():
    base = [row("XAA", SVC, 2025, 10)]
    changes = cr.compare(base, [row("XAA", SVC, 2025, 12)], COV)
    check("same key, different value -> one 'revised'", [c.kind for c in changes] == ["revised"]
          and changes[0].old["value"] == "10" and changes[0].new["value"] == "12", str(changes))


def test_funding_stream_set_compared():
    ind = "ippf_funding_streams"
    cov = {ind: {"year": "2026", "link": "l"}}
    base = [row("XAA", ind, 2026, 2, "Stream A, Stream B")]
    same = cr.compare(base, [row("XAA", ind, 2026, 2, "Stream B, Stream A")], cov)
    swap = cr.compare(base, [row("XAA", ind, 2026, 2, "Stream A, Stream C")], cov)
    check("stream set compared, order ignored", same == [] and [c.kind for c in swap] == ["revised"],
          f"{same} {swap}")


def test_missing_org_only_for_covered_source():
    base = [row("XAA", SVC, 2024, 5), row("XBB", SVC, 2024, 7), row("XAA", "rate_x", 2024, 1.0)]
    new = [row("XAA", SVC, 2025, 6)]
    changes = cr.compare(base, new, COV)
    missing = [(c.iso3, c.indicator_id) for c in changes if c.kind == "missing"]
    check("a country absent from a covered indicator is 'missing'; uncovered indicators are not",
          missing == [(("XBB"), SVC)], str(changes))
    check("missing line links to the covered file", all(c.link == "file.csv" for c in changes if c.kind == "missing"),
          str(changes))


def test_focus_change_without_second_reader():
    ind = "ippf_bp_hiv_focus"
    cov = {ind: {"year": "2027", "link": "l"}}
    base = [row("XAA", ind, 2026, "high"), row("XBB", ind, 2026, "high")]
    new = [row("XAA", ind, 2027, "moderate", _second_reader=""), row("XBB", ind, 2027, "high", _second_reader="")]
    changes = cr.compare(base, new, cov)
    fc = [c for c in changes if c.kind == "focus_change"]
    check("a rating that differs from last plan year is a focus_change", [c.iso3 for c in fc] == ["XAA"], str(changes))
    check("no second reader -> guidance says so",
          fc and "needs a second reader before it can be ticked" in fc[0].guidance, str(fc))
    check("an unchanged rating in a new plan year is plain 'new'",
          [c.kind for c in changes if c.iso3 == "XBB"] == ["new"], str(changes))


def test_change_id_stable():
    base = [row("XAA", SVC, 2025, 10)]
    a = cr.compare(base, [row("XAA", SVC, 2025, 12)], COV)[0].change_id
    b = cr.compare(base, [row("XAA", SVC, 2025, 12)], COV)[0].change_id
    p1 = cr.compare([], [row("XAA", "ippf_funding_streams_partner", 2026, "Stream A")],
                    {"ippf_funding_streams_partner": {"year": "2026", "link": ""}})[0].change_id
    p2 = cr.compare([], [row("XAA", "ippf_funding_streams_partner", 2026, "Stream B")],
                    {"ippf_funding_streams_partner": {"year": "2026", "link": ""}})[0].change_id
    check("change_id is the same on two runs and 10 hex characters", a == b and len(a) == 10
          and all(ch in "0123456789abcdef" for ch in a), f"{a} {b}")
    check("partner rows of two streams get two ids", p1 != p2, f"{p1} {p2}")


def test_missing_needs_a_non_empty_old_value():
    """A country whose last-edition value is empty never had a value, so nothing went missing."""
    base = [row("XAA", SVC, 2024, ""), row("XBB", SVC, 2024, "  "), row("XCC", SVC, 2024, 4)]
    changes = cr.compare(base, [], COV)
    missing = sorted(c.iso3 for c in changes if c.kind == "missing")
    check("missing only where the last edition held a non-empty value", missing == ["XCC"], str(changes))


def test_unknown_codes_reach_the_country_line():
    """I2: a country with an unticked code gets its own Must-check line naming that code."""
    base = [row(f"X{c}A", "ippf_hiv_services", 2024, 100) for c in "ABC"]
    new = [row(f"X{c}A", "ippf_hiv_services", 2025, 105) for c in "ABC"]
    cov = {"ippf_hiv_services": {"year": "2025", "link": "f.csv", "unknown_codes": {"XBA": ["901B"]}}}
    changes = cr.compare(base, new, cov)
    xb = next(c for c in changes if c.iso3 == "XBA")
    check("I2: the change carries the unknown code in its guidance", "901B" in xb.guidance and
          "ma_codes.csv" in xb.guidance, xb.guidance)
    lines = cr.group_changes(changes)
    own = [l for l in lines if l.change_ids == [xb.change_id]]
    check("I2: that change is its own Must-check line, not folded into a group",
          own and own[0].sheet == "Must check", str(lines))
    cov2 = {"ippf_hiv_services": {"year": "2025", "link": "f.csv", "unknown_codes": {"XZZ": ["777"]}}}
    miss = [c for c in cr.compare(base + [row("XZZ", "ippf_hiv_services", 2024, 9)], new, cov2) if c.iso3 == "XZZ"]
    check("I2: a missing country with an unknown code says so", miss and "777" in miss[0].guidance, str(miss))


def test_must_check_capped_and_snapshot_optional():
    base = [row(f"X{i:02d}", SVC, 2025, 10) for i in range(40)]
    new = [row(f"X{i:02d}", SVC, 2025, 11 + i) for i in range(40)]
    new.append(row("XZZ", "rate_x", 2025, 3.0, ticked_by="snapshot ba_tick"))
    cov = dict(COV, rate_x={"year": "2025", "link": "s"})
    lines = cr.group_changes(cr.compare(base, new, cov))
    must = [l for l in lines if l.sheet == "Must check"]
    snap = [l for l in lines if any(cid for cid in l.change_ids) and "rate_x" in l.title]
    check("at most 30 lines on Must check, the rest Optional", len(must) == cr.MAX_MUST and len(lines) == 41,
          f"{len(must)} of {len(lines)}")
    check("snapshot rows sit on Optional", snap and all(l.sheet == "Optional" for l in snap), str(snap))


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:
                check(name, False, f"{type(e).__name__}: {e}")
    print(f"\n{'PASS' if not FAILS else 'FAIL'}: {len(FAILS)} failing check(s)")
    sys.exit(1 if FAILS else 0)
