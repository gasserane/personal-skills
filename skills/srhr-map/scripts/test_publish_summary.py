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

    # --- Task 3: the three summary views ---
    fund = [row("XAA", "ippf_funding_streams", "2", "Core Z1, Stream Q"),
            row("XBB", "ippf_funding_streams", "1", "Stream Q", status="associate member"),
            row("XCC", "ippf_funding_streams", "0", "none", status="Collaborative Partner"),
            row("XDD", "ippf_funding_streams", "1", "Stream Q", status="withdrawn")]
    rates = [row("XAA", "ecdc_hiv_diagnosis_rate", "4.4", year=ps.rdc.RATE_YEAR, unit="per 100 000 people"),
             row("XAA", "ecdc_hiv_diagnosis_rate", "77.7", year="2999", unit="per 100 000 people"),
             row("XDD", "ecdc_hiv_diagnosis_rate", "6.6", year=ps.rdc.RATE_YEAR, status="withdrawn",
                 unit="per 100 000 people")]
    mem_a = [dict(MEMBERS[0], value_display="MA with core grant")] + MEMBERS[1:]
    rows3 = mem_a + fund + rates
    master3 = [{"iso3": i, "country": n} for i, n in
               (("XAA", "Aland"), ("XBB", "Bland"), ("XCC", "Cland"), ("XDD", "Dland"))]
    views, frame = ps.summary_views(rows3, master3)
    vid = {v["id"]: v for v in views}
    record("views_order_A_F_D", [v["id"] for v in views] == ["A", "F", "D"], [v["id"] for v in views])
    keys = {"id", "name", "title", "subtitle", "legend_title", "legend", "filters", "colour", "tips"}
    record("views_have_page_keys", all(set(v) == keys for v in views), [sorted(v) for v in views])
    A, F, D = vid.get("A", {}), vid.get("F", {}), vid.get("D", {})
    a_text = ps.json.dumps(A)
    record("A_colours_by_member_status_not_value_display",
           A.get("colour") == {"XAA": "full member", "XBB": "associate member", "XCC": "Collaborative Partner"}
           and "core" not in a_text.lower(), A.get("colour"))
    record("A_hover_plain_words", A.get("tips", {}).get("XCC") == "Cland: IPPF collaborative partner"
           and A.get("tips", {}).get("XAA") == "Aland: IPPF member association", A.get("tips"))
    record("A_colours_from_palette_by_status", [lg["colour"] for lg in A.get("legend", [])]
           == ps.pw.PALETTE["A"][:3], A.get("legend"))
    f_counts = {lg["key"]: lg["count"] for lg in F.get("legend", [])}
    record("F_legend_counts_match_bands", f_counts == {"core": 1, "other": 1, "none": 1}, f_counts)
    record("F_hover_partner_word", F.get("tips", {}).get("XCC") == "Cland: IPPF partner, no IPPF grant in 2026"
           and F.get("tips", {}).get("XAA") == "Aland: receives the IPPF core grant in 2026", F.get("tips"))
    f_text = ps.json.dumps(F)
    record("F_no_stream_key_or_label_in_view", not any(t in f_text for t in ("Core Z1", "Stream Q")), f_text[:200])
    record("F_filters_by_band", [f["key"] for f in F.get("filters", [])] == ["core", "other", "none"]
           and not D.get("filters") and len(A.get("filters", [])) == 3, F.get("filters"))
    d_text = ps.json.dumps(D)
    record("D_uses_rate_year", "77.7" not in d_text and "2999" not in d_text
           and D.get("colour", {}).get("XAA") == ps.computed.d_class(4.4), D.get("colour"))
    record("D_hover_rate_text", D.get("tips", {}).get("XAA") ==
           f"Aland: 4.4 new HIV diagnoses per 100 000 people, {ps.rdc.RATE_YEAR}. Source: ECDC/WHO", D.get("tips"))
    record("D_missing_rate_hover", D.get("tips", {}).get("XBB") == f"Bland: no {ps.rdc.RATE_YEAR} data"
           and "XBB" not in D.get("colour", {}), D.get("tips"))
    record("frame_is_members", frame == {"XAA", "XBB", "XCC"}, frame)
    record("titles_from_templates", A.get("title") == "IPPF members and partners, 2026"
           and F.get("title") == "IPPF funding to members, 2026"
           and D.get("title") == f"New HIV diagnoses, {ps.rdc.RATE_YEAR}", [v.get("title") for v in views])
    import test_register_deck_check as trd
    nm = [{"iso3": i, "country": n} for n, i in trd.NAMES.items()]
    dv, _ = ps.summary_views(trd.REG, nm)
    deck = [t for tips in trd.TIPS.values() for t in tips.values()]
    hits = [t for v in dv for t in v["tips"].values() for s in deck if t == s or s in t]
    record("no_view_text_from_deck_tips", not hits and bool(dv[0]["tips"]), hits)

    print(f"{sum(results)}/{len(results)} cases ok")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
