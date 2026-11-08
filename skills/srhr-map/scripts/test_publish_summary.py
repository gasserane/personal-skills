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
    f_cols = {lg["key"]: lg["colour"] for lg in F.get("legend", [])}
    record("F_colours_dream_crystal_pear_tint", f_cols == {"core": "#00313C", "other": "#71C5E8", "none": "#D5DE7C"}
           and [f["colour"] for f in F.get("filters", [])] == ["#00313C", "#71C5E8", "#D5DE7C"], f_cols)
    land = re.search(r"--map-land:\s*(#[0-9A-Fa-f]{6})", ps.pw.PAGE).group(1).upper()
    record("F_no_band_is_context_grey", land not in {c.upper() for c in f_cols.values()}
           and "#BFC8CB" not in f_cols.values(), (land, f_cols))
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

    # --- Task 4: header, footer and the page config ---
    cfg = {"contact": "a&b<c>'d@example.org", "author_unit": "Unit & <Dept> 'X'", "disclosure": "Disclosed <i>here</i>."}
    hd = ps.header_html({"n": 3, "m": 5, "outside": []}, "2031 <b>", "2031-01-02")
    ft = ps.footer_html(cfg)
    record("summary_header_escapes", "<b>" not in hd and "&lt;b&gt;" in hd and "work in 3 of the 5" in hd
           and "service coverage" in hd and "Edition 2031 &lt;b&gt;, made on 2031-01-02" in hd, hd)
    record("summary_footer_escapes", "<Dept>" not in ft and "&lt;Dept&gt;" in ft and "<i>" not in ft
           and "'d@" not in ft and "Prepared by Unit &amp; &lt;Dept&gt; &#x27;X&#x27;." in ft, ft)
    record("footer_has_mailto", 'href="mailto:a&amp;b&lt;c&gt;&#x27;d@example.org"' in ft
           and "For more information:" in ft, ft)
    record("footer_has_sources_line", "IPPF membership and grant records; ECDC/WHO HIV surveillance; "
                                      "WHO European Region member list" in ft, ft)
    from html.parser import HTMLParser

    class Tags(HTMLParser):
        def __init__(self):
            super().__init__()
            self.seen = []

        def handle_starttag(self, tag, attrs):
            self.seen.append(tag)
    tg = Tags()
    tg.feed(hd + ft)
    record("summary_header_footer_parse_to_own_tags", set(tg.seen) <= {"h1", "p", "a"}, tg.seen)
    with tempfile.TemporaryDirectory() as d:
        good = Path(d) / "page.csv"
        good.write_bytes(b"\xef\xbb\xbfkey,value\r\ncontact,x@example.org\r\nauthor_unit,Unit\r\ndisclosure,Text.\r\n")
        record("page_cfg_loads", ps.load_page_cfg(good) == {"contact": "x@example.org", "author_unit": "Unit",
                                                            "disclosure": "Text."}, ps.load_page_cfg(good))
        for missing in ("contact", "author_unit", "disclosure"):
            p = Path(d) / f"no_{missing}.csv"
            body = {"contact": "x@example.org", "author_unit": "Unit", "disclosure": "Text."}
            body[missing] = ""
            p.write_text("key,value\n" + "".join(f"{k},{v}\n" for k, v in body.items()), encoding="utf-8")
            try:
                ps.load_page_cfg(p)
                record(f"page_cfg_refuses_missing_{missing}", False, "no Stop")
            except Stop as e:
                record(f"page_cfg_refuses_missing_{missing}", e.code == 1, e.code)

    # --- Task 5: forbidden-text scan ---
    with tempfile.TemporaryDirectory() as d:
        streams = Path(d) / "streams.csv"
        streams.write_text("key,label,group,colour,ledger_names\nCore Z1,Stream Q,g,#000000,Ledger One;Ledger Two|"
                           "Ledger Three\nKW,Word,g,,\n", encoding="utf-8")
        codes = Path(d) / "ma_codes.csv"
        codes.write_text("ma_code,iso3,org_name,ticked_by,tick_date,suggestion_basis\n123,XAA,Org Kappa,t,d,b\n",
                         encoding="utf-8")
        terms = ps.forbidden_terms(streams, codes)
        record("terms_from_both_files", terms == {"Core Z1", "Stream Q", "Ledger One", "Ledger Two", "Ledger Three",
                                                  "KW", "Word", "123", "Org Kappa"}, sorted(terms))
        empty = Path(d) / "empty.csv"
        empty.write_text("ma_code,iso3,org_name\n", encoding="utf-8")
        for case, args in (("terms_refuse_empty_file", (streams, empty)), ("terms_refuse_empty_streams", (empty, codes)),
                           ("terms_refuse_missing_file", (Path(d) / "gone.csv", codes))):
            try:
                ps.forbidden_terms(*args)
                record(case, False, "no Stop")
            except Stop as e:
                record(case, e.code == 1, e.code)
        allow = Path(d) / "allow.csv"
        allow.write_text("term,ticked_by,date\nWord,Ane,2031-01-02\nStream Q,,\n", encoding="utf-8")
        record("allow_needs_tick", ps.load_allow(allow) == {"Word"}, ps.load_allow(allow))
        record("allow_missing_file_is_empty", ps.load_allow(Path(d) / "none.csv") == set(), "")

    def fixture_page(views):
        data = {"edition": "2031", "made_on": "2031-01-02", "views": views,
                "countries": [{"iso3": "XAA", "name": "Aland", "paths": [[[[123, 45], [124.5, 46], [123, 45]]]]}]}
        return ps.pw.page(data, "/* d3 block: Stream Q Org Kappa 123 */", ps.header_html(h, "2031", "2031-01-02"),
                          ps.footer_html({"contact": "x@example.org", "author_unit": "Unit", "disclosure": "Text."}),
                          title="IPPF across Europe, 2031")

    clean_views, _ = ps.summary_views(rows3, master3)
    clean = fixture_page(clean_views)
    strs = ps.page_strings(clean)
    record("page_strings_has_visible_and_json_text", any("work in 3 of the 5" in s for s in strs)
           and "Aland: IPPF member association" in strs and not any("d3 block" in s for s in strs)
           and not any("{" in s and "}" in s for s in strs), strs[:6])
    record("scan_clean_page_passes", ps.scan(strs, terms, set()) == [], ps.scan(strs, terms, set()))
    planted = ps.json.loads(ps.json.dumps(clean_views))
    planted[1]["tips"]["XAA"] = "Aland: receives Stream Q in 2026"
    hits = ps.scan(ps.page_strings(fixture_page(planted)), terms, set())
    record("scan_planted_term_fails", [t for t, _ in hits] == ["Stream Q"], hits)
    planted2 = ps.json.loads(ps.json.dumps(clean_views))
    planted2[0]["legend"][0]["label"] = "Org 123 office"
    hits2 = ps.scan(ps.page_strings(fixture_page(planted2)), terms, set())
    record("scan_planted_ma_code_in_json_fails", [t for t, _ in hits2] == ["123"], hits2)
    record("scan_ignores_coordinates", "123" in clean and not ps.scan(ps.page_strings(clean), {"123"}, set()), "")
    record("scan_whole_word", ps.scan(["Stream AB here"], {"Stream A"}, set()) == []
           and ps.scan(["a Stream A."], {"Stream A"}, set()) == [("Stream A", "a Stream A.")]
           and ps.scan(["a Keyword"], {"Key"}, set()) == [], "")
    record("scan_case_sensitive", ps.scan(["the word here"], {"Word"}, set()) == [], "")
    record("scan_allow_clears_only_ticked", ps.scan(["Word and Stream Q"], {"Word", "Stream Q"}, {"Word"})
           == [("Stream Q", "Word and Stream Q")], "")

    # --- Task 6: the partner note and build_summary / main ---
    pr = mem_a + [row("XAA", "ippf_funding_streams", "0", "none"),
                  row("XAA", "ippf_funding_streams_partner", "Stream Q")]
    record("partner_band_changes_named", ps.partner_band_changes(pr) == ["XAA"]
           and ps.partner_band_changes(rows3) == [], ps.partner_band_changes(pr))

    import io
    from contextlib import redirect_stderr, redirect_stdout
    import test_publish_webmap as twm  # invented register, topology and pinned fake d3

    def cli(argv):
        o, e = io.StringIO(), io.StringIO()
        with redirect_stdout(o), redirect_stderr(e):
            code = ps.main(argv)
        return code, o.getvalue() + e.getvalue()

    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        codes6 = d / "ma_codes.csv"
        codes6.write_text("ma_code,iso3,org_name\n777,ONE,Org Invented One\n", encoding="utf-8")
        who6 = _who_file(d, "iso3,country\nONE,Country One\nTWO,Country Two\nGON,Country Gone\nZZZ,Zland\n", "who6.csv")
        cfg6 = d / "page.csv"
        cfg6.write_text("key,value\ncontact,x@example.org\nauthor_unit,Unit\ndisclosure,Text.\n", encoding="utf-8")

        def argv6(out, who=who6, cfg=cfg6):
            return ["--register", str(twm.REG), "--ma-codes", str(codes6), "--crosswalk", str(twm.CROSS),
                    "--master", str(twm.MASTER), "--who", str(who), "--page-config", str(cfg),
                    "--geometry", str(twm.GEO), "--d3", str(twm.D3), "--out", str(out)]

        out = d / "pub" / "webmap_summary_2031.html"
        code, log = cli(argv6(out))
        record("build_writes_page", code == 0 and out.exists(), log)
        record("build_prints_headline_and_views", "headline: 2 of 4" in log and "A: 2 coloured, 2 tooltips" in log, log)
        text = out.read_text(encoding="utf-8") if out.exists() else ""
        data = ps.json.loads(re.search(r'id="map-data">(.*?)</script>', text, re.S).group(1)) if text else {}
        record("build_embeds_headline", data.get("headline") == {"n": 2, "m": 4}, data.get("headline"))
        record("build_page_has_no_deck_or_stream_text", text and not ps.scan(ps.page_strings(text),
               ps.forbidden_terms(twm.CROSS, codes6), set()) and "Country One: MA with core grant" not in text, "")
        record("build_notes_region", "not on the WHO" in log and "NOC" in log and "ZZZ" in log, log)

        code, log = cli(argv6(out))
        record("build_never_overwrites", code == 2, (code, log))

        who_small = _who_file(d, "iso3,country\nONE,Country One\n", "who_small.csv")
        out2 = d / "pub" / "outside.html"
        code, log = cli(argv6(out2, who=who_small))
        record("build_refuses_outside_member", code == 1 and not out2.exists() and "TWO" in log, (code, log))

        bad_cfg = d / "bad_page.csv"
        bad_cfg.write_text("key,value\ncontact,x@example.org\nauthor_unit,Stream two team\ndisclosure,Text.\n",
                           encoding="utf-8")
        out3 = d / "pub" / "scan_hit.html"
        code, log = cli(argv6(out3, cfg=bad_cfg))
        record("build_refuses_scan_hit_before_write", code == 1 and not out3.exists() and "Stream two" in log,
               (code, log))

    print(f"{sum(results)}/{len(results)} cases ok")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
