"""Tests for publish_summary.py (SRHR map skill, phase e: the summary web map for donors and partners).
Every country code, name, stream key and organisation in these fixtures is invented, because this
repository is public.

Run:  python test_publish_summary.py
"""
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import publish_summary as ps  # noqa: E402
from publish_workbook import Stop  # noqa: E402


def row(iso, ind, value, display=None, year="2026", status="full member", unit=""):
    return {"iso3": iso, "member_status": status, "indicator_id": ind, "value": value,
            "value_display": value if display is None else display, "reference_year": year, "unit": unit,
            "ma_code": ""}


MEMBERS = [row("XAA", "ippf_membership", "MA", status="full member"),
           row("XBB", "ippf_membership", "MA", status="associate member"),
           row("XCC", "ippf_membership", "CP", status="Collaborative Partner"),
           row("XDD", "ippf_membership", "MA", status="withdrawn")]


def _who_file(d, text, name="who.csv", bom=False):
    p = Path(d) / name
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
    return p


def main():
    results = []

    def record(case, ok, detail=""):
        results.append(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {case}" + (f": {detail}" if not ok else ""))

    who = {"XAA", "XBB", "XCC", "XDD", "XEE"}

    # --- Task 2: the headline ---
    twice = MEMBERS + [row("XAA", "ippf_funding_streams", "1", "Stream A")]
    h = ps.headline(twice, who)
    record("headline_counts_countries_not_rows", h["n"] == 3 and h["m"] == 5, h)
    record("headline_excludes_withdrawn", "XDD" not in ps.computed.member_status_classes(MEMBERS) and h["n"] == 3, h)
    h2 = ps.headline(MEMBERS, {"XAA", "XBB"})
    record("headline_outside_listed", h2["outside"] == ["XCC"], h2)
    record("headline_template_has_no_digits", re.search(r"\d", ps.HEADLINE) is None
           and re.search(r"\d", ps.DEFINITION) is None, ps.HEADLINE)
    record("headline_fills", ps.HEADLINE.format(n=3, m=5).endswith("work in 3 of the 5 countries of the WHO "
                                                                    "European Region"), ps.HEADLINE)

    with tempfile.TemporaryDirectory() as d:
        try:
            ps.load_who(_who_file(d, "iso3,country\n"))
            record("load_who_refuses_empty", False, "no Stop")
        except Stop as e:
            record("load_who_refuses_empty", e.code == 1, e.code)
        try:
            ps.load_who(_who_file(d, "code,country\nXAA,Aland\n", "nocol.csv"))
            record("load_who_refuses_no_iso3_column", False, "no Stop")
        except Stop as e:
            record("load_who_refuses_no_iso3_column", e.code == 1, e.code)
        try:
            ps.load_who(Path(d) / "missing.csv")
            record("load_who_refuses_missing_file", False, "no Stop")
        except Stop as e:
            record("load_who_refuses_missing_file", e.code == 1, e.code)
        clean = ps.load_who(_who_file(d, "iso3,country\nXAA,Aland\nXBB,Bland\n", "clean.csv"))
        excel = ps.load_who(_who_file(d, "iso3,country\r\nxaa,Aland\r\n XBB ,Bland\r\n,\r\n\r\n", "excel.csv", bom=True))
        record("load_who_excel_variant", clean == excel == {"XAA", "XBB"}, (clean, excel))

    # --- Task 2: region notes ---
    master = [{"iso3": "XAA", "country": "Aland"}, {"iso3": "XBB", "country": "Bland"},
              {"iso3": "XKK", "country": "Kland"}]
    notes = ps.region_notes(master, {"XAA", "XBB", "XZZ"}, drawn={"XAA"}, counted={"XAA", "XBB"})
    joined = "\n".join(notes)
    record("region_notes_master_not_in_who", any("XKK" in n and "not on the WHO" in n for n in notes), notes)
    record("region_notes_who_not_in_master", any("XZZ" in n and "not in the master" in n for n in notes), notes)
    record("region_notes_name_undrawn_member", any("XBB" in n and "geometry" in n for n in notes)
           and "XAA" not in joined.split("geometry")[-1], notes)
    record("region_notes_silent_when_aligned",
           ps.region_notes(master[:2], {"XAA", "XBB"}, drawn={"XAA", "XBB"}, counted={"XAA"}) == [], "")

    print(f"{sum(results)}/{len(results)} cases ok")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
