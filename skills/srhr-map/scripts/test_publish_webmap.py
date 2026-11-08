"""Planted tests for publish_webmap.py (SRHR map skill, phase d, web map).

Invented countries (Country One / Two / Gone, codes ONE / TWO / GON), streams and an invented
topology only; the register and tips come from test_register_deck_check so the web map is tested
against the same fixture the deck check uses. Writes into a temporary folder. Run:
    python test_publish_webmap.py
"""
import csv
import html
import io
import json
import re
import sys
import tempfile
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import computed  # noqa: E402
import publish_plan as pp  # noqa: E402
import publish_webmap as pwm  # noqa: E402
import register_deck_check as rdc  # noqa: E402
import test_register_deck_check as trc  # noqa: E402

FAILS = []
TMP = Path(tempfile.mkdtemp(prefix="srhr_wm_"))
M49 = {"ONE": "901", "TWO": "902", "GON": "903"}
NAMES = trc.NAMES
ISO_NAME = {v: k for k, v in NAMES.items()}


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ': ' + str(detail)[:300]}")
    if not cond:
        FAILS.append(name)


def full(r):
    base = {"iso3": "", "ma_code": "", "member_status": "full member", "topic": "t", "indicator_id": "",
            "value": "", "value_display": "", "unit": "", "reference_year": "", "source_id": "s",
            "date_read": "", "machine_check": "pass", "ticked_by": "", "tick_date": "", "snapshot_tag": ""}
    base.update(r)
    if base["indicator_id"] == "ecdc_hiv_diagnosis_rate":
        base["unit"] = "per 100 000"
    return base


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return path


# Planted change: the register says Country One holds 5 grant streams; the deck tip still says 4.
REG_ROWS = [full(r) for r in trc.REG]
for r in REG_ROWS:
    if r["iso3"] == "ONE" and r["indicator_id"] == "ippf_grant_streams_count":
        r["value"], r["value_display"] = "5", "5 (a, b, c, d, e)"
REG = write_csv(TMP / "map_register_2031.csv", list(REG_ROWS[0]), REG_ROWS)
CROSS = write_csv(TMP / "streams.csv", ["key", "label", "group", "colour"],
                  [{"key": k, "label": v, "group": "g", "colour": c}
                   for (k, v), c in zip(trc.CROSS, ["112233", "445566", "778899"])])
MASTER = write_csv(TMP / "master_countries.csv", ["country", "iso3", "m49"],
                   [{"country": n, "iso3": i, "m49": M49[i]} for n, i in NAMES.items()]
                   + [{"country": "Country Nocode", "iso3": "NOC", "m49": ""}])
NAMES_ALL = dict(NAMES, **{"Country Nocode": "NOC"})

DECKS = TMP / "decks"
DECKS.mkdir()
EXTRA_A = '<script>alert(1)</script> & "quotes"'  # a tip must reach the page as text, never as markup


def deck(m, tips):
    sps = "".join(
        f'<p:sp><p:nvSpPr><p:cNvPr id="{i + 2}" name="Country: {html.escape(c)}">'
        f'<a:hlinkHover r:id="" tooltip="{html.escape(t)}"/></p:cNvPr>'
        f'</p:nvSpPr></p:sp>' for i, (c, t) in enumerate(tips.items()))
    with zipfile.ZipFile(DECKS / f"Map {m} - invented.pptx", "w") as z:
        z.writestr("ppt/slides/slide1.xml", f"<p:sld><p:cSld><p:spTree>{sps}</p:spTree></p:cSld></p:sld>")


DECK_TIPS = {m: dict(t) for m, t in trc.TIPS.items()}
DECK_TIPS["A"]["Country Nocode"] = "Country Nocode: " + EXTRA_A
for m, t in DECK_TIPS.items():
    deck(m, t)


def ring(x, y):
    return [[x, y], [1, 0], [0, 1], [-1, 0], [0, -1]]


# Invented topology (quantised, delta-encoded arcs as in world-atlas): one square per country,
# a context country (999) and one feature without an id, matched by name.
TOPO = {"type": "Topology", "transform": {"scale": [1, 1], "translate": [0, 40]},
        "objects": {"countries": {"type": "GeometryCollection", "geometries": [
            {"type": "Polygon", "id": "901", "arcs": [[0]], "properties": {"name": "One-land"}},
            {"type": "MultiPolygon", "id": "902", "arcs": [[[1]], [[2]]], "properties": {"name": "Two-land"}},
            {"type": "Polygon", "id": "903", "arcs": [[3]], "properties": {"name": "Gone-land"}},
            {"type": "Polygon", "id": "999", "arcs": [[4]], "properties": {"name": "Context-land"}},
            {"type": "Polygon", "arcs": [[5]], "properties": {"name": "Country Nocode"}},
        ]}},
        "arcs": [ring(10, 10), ring(12, 10), ring(14, 10), ring(16, 10), ring(18, 10), ring(20, 10)]}
GEO = TMP / "countries.json"
GEO.write_text(json.dumps(TOPO), encoding="utf-8")
FAKE_D3 = "/* fake d3 (ISC) */ window.fakeD3 = 1;"
D3 = TMP / "d3.min.js"
D3.write_text(FAKE_D3, encoding="utf-8")


def sri(data: bytes) -> str:
    import base64
    import hashlib
    return "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = pwm.main(argv)
        except SystemExit as e:
            code = e.code
    return code, out.getvalue() + err.getvalue()


def args(out):
    return ["--register", str(REG), "--crosswalk", str(CROSS), "--master", str(MASTER), "--d3", str(D3),
            "--decks", str(DECKS), "--geometry", str(GEO), "--out", str(out)]


def embedded(text):
    m = re.search(r'<script type="application/json" id="map-data">(.*?)</script>', text, re.S)
    return json.loads(m.group(1)) if m else None


def main():
    reg = pwm._read(REG)
    by = rdc._index(reg)
    crosswalk = [(k, v) for k, v in trc.CROSS]

    # --- build and embedded data ---
    out = TMP / "webmap_2031.html"
    code, log = run(args(out))
    check("build_exit_0", code == 0, log)
    text = out.read_text(encoding="utf-8") if out.exists() else ""
    data = embedded(text)
    check("data_embedded", data is not None, text[:200])
    data = data or {"views": [], "countries": []}
    check("edition_from_file_name", data.get("edition") == "2031", data.get("edition"))
    views = {v["id"]: v for v in data["views"]}
    check("one_view_per_map", sorted(views) == ["A", "B", "C", "D"], sorted(views))
    isos = {c["iso3"] for c in data["countries"]}
    check("every_country_embedded", {"ONE", "TWO", "GON", "NOC"} <= isos, isos)
    check("every_country_has_shape", all(c.get("paths") for c in data["countries"] if c["iso3"]),
          [c["iso3"] for c in data["countries"] if not c.get("paths")])
    check("context_shape_kept_without_code", any(not c["iso3"] for c in data["countries"]))
    check("name_fallback_when_no_m49",
          any(c["iso3"] == "NOC" and c.get("paths") for c in data["countries"]))

    # --- tooltips equal the deck tip template output ---
    for m in "ABCD":
        v = views.get(m, {"tips": {}})
        for name, tip in trc.TIPS[m].items():
            iso = NAMES[name]
            want = pp.new_tip(m, tip, by, iso, crosswalk) if iso in pp._in_register(m, by) else tip
            check(f"tip_{m}_{iso}_equals_new_tip", v["tips"].get(iso) == want, (v["tips"].get(iso), want))
    check("tip_B_planted_change_shown", views.get("B", {"tips": {}})["tips"].get("ONE")
          == "Country One: 5 grant streams in 2026", views.get("B", {}).get("tips"))
    check("tip_outside_register_verbatim", views.get("A", {"tips": {}})["tips"].get("NOC")
          == "Country Nocode: " + EXTRA_A)
    check("tip_never_raw_markup", "<script>alert(1)</script>" not in text)

    # --- colours, legends and filters from computed.py ---
    for m in "ABC":
        v = views.get(m, {"colour": {}, "legend": [], "filters": []})
        want_iso = set(computed.country_classes(m, reg, crosswalk)) if m != "C" else \
            {r["iso3"] for r in reg if r["indicator_id"] == "ippf_funding_streams" and r["member_status"] != "withdrawn"}
        check(f"coloured_{m}_equals_register", set(v["colour"]) == want_iso, (sorted(v["colour"]), sorted(want_iso)))
        check(f"withdrawn_not_coloured_{m}", "GON" not in v["colour"])
        check(f"withdrawn_in_no_filter_{m}", all("GON" not in f["members"] for f in v["filters"]))
    a = views.get("A", {"legend": [], "filters": []})
    counts = computed.class_counts("A", reg, crosswalk)
    check("legend_A_counts_computed", {(x["label"], x["count"]) for x in a["legend"]}
          == {(k, n) for k, (n, _) in counts.items()}, a["legend"])
    cc = computed.class_counts("C", reg, crosswalk)
    c = views.get("C", {"filters": []})
    fk = {f["key"]: f for f in c["filters"]}
    check("filters_C_are_streams", set(fk) == {k for k, _ in trc.CROSS if k in cc}, sorted(fk))
    check("filter_C_partner_counts_as_held", "ONE" in fk.get("K2", {"members": []})["members"], fk.get("K2"))
    check("filter_C_label_has_half", fk.get("K2", {}).get("text", "").endswith("(0 + 1 half)"), fk.get("K2"))
    check("filter_C_colour_from_crosswalk", fk.get("K1", {}).get("colour") == "#112233", fk.get("K1"))
    d = views.get("D", {"colour": {}, "filters": None})
    check("D_no_filters", d["filters"] == [], d["filters"])
    check("D_colours_rate_countries_incl_withdrawn", set(d["colour"]) == {"ONE", "GON"}, d["colour"])
    check("D_band_from_d_class", d["colour"].get("ONE") == computed.d_class(4.4), d["colour"])

    # --- titles: computed, no typed number in any template ---
    digits = [t for t in pwm.TEMPLATES.values() for s in t if re.search(r"\d", s)]
    check("no_digit_in_title_templates", not digits, digits)
    check("subtitle_A_counts_from_register", "1 Member Association" in views.get("A", {}).get("subtitle", ""),
          views.get("A", {}).get("subtitle"))
    try:
        computed.render("A title with 3 typed")
        check("render_refuses_digit", False)
    except ValueError:
        check("render_refuses_digit", True)

    # --- d_class bands ---
    check("d_class_bands", [computed.d_class(x) for x in (1.3, 3.0, 4.8, 5.5, 12.9, 20.2)]
          == [0, 1, 1, 2, 3, 4])

    # --- page contract ---
    check("page_has_title", re.search(r"<title>[^<\d]+</title>", text) is not None)
    check("page_dark_tokens", "prefers-color-scheme: dark" in text and ':root[data-theme="dark"]' in text)
    check("page_viewport_gutter", "max(16px, env(safe-area-inset-left, 0px))" in text)
    srcs = re.findall(r'<script[^>]+src="([^"]+)"', text)
    # d3 embedded (Session 5): the page runs offline and where the CDN is blocked
    check("no_external_scripts", srcs == [], srcs)
    check("d3_embedded_inline", FAKE_D3 in text, "")
    check("d3_before_map_script", 0 <= text.find(FAKE_D3) < text.find("d3.zoom()"), "")
    check("d3_sri_pinned_7_9_0", pwm.D3_SRI.startswith("sha512-vc58qvvB") and "/7.9.0/" in pwm.D3_URL, pwm.D3_SRI)
    bad = TMP / "d3_bad.min.js"
    bad.write_text("tampered", encoding="utf-8")
    try:
        pwm.fetch_d3(bad)
        refused = False
    except pwm.Stop:
        refused = True
    check("fetch_d3_refuses_wrong_hash", refused and bad.read_text(encoding="utf-8") == "tampered")
    keep = pwm.D3_SRI
    pwm.D3_SRI = sri(FAKE_D3.encode("utf-8"))
    try:
        pwm.fetch_d3(D3)
        accepted = True
    except pwm.Stop:
        accepted = False
    pwm.D3_SRI = keep
    check("fetch_d3_accepts_matching_cache", accepted)
    evil = TMP / "d3_evil.min.js"
    evil.write_text("var s = '</script><b>';", encoding="utf-8")
    eo = TMP / "webmap_evil.html"
    a = args(eo)
    a[a.index("--d3") + 1] = str(evil)
    code, log = run(a)
    check("refuses_library_closing_script", code == 1 and not eo.exists(), (code, log))
    check("no_local_path_in_page", not re.search(r"[A-Za-z]:\\\\", text))

    # --- zoom (Task 7 amendment, Session 5): buttons, wheel and pinch on every view ---
    script = text.split('id="map-data"', 1)[-1]
    for bid, label in (("zoom-in", "Zoom in"), ("zoom-out", "Zoom out"), ("zoom-reset", "Reset zoom")):
        m = re.search(r'<button[^>]*id="' + bid + r'"[^>]*>', text)
        check(f"zoom_button_{bid}", m is not None and 'type="button"' in m.group(0)
              and f'aria-label="{label}"' in m.group(0), m and m.group(0))
    check("zoom_buttons_inside_map_card", re.search(r'<div class="map" id="map">.*?id="zoom-in"', text, re.S) is not None)
    check("zoom_behaviour_bound", "d3.zoom()" in script and ".scaleExtent([1," in script
          and ".translateExtent(" in script and "svg.call(zoom)" in script, "")
    check("zoom_moves_the_map_group", re.search(r'g\.attr\("transform",\s*ev\.transform\)', script) is not None)
    check("zoom_reset_to_identity", "d3.zoomIdentity" in script)
    check("zoom_kept_per_view", "zoomOf[cur]" in script and re.search(r"zoomOf\[cur\]\s*=", script) is not None)
    check("zoom_restored_on_view_change", re.search(r"zoom\.transform,\s*zoomOf\[cur\]", script) is not None)
    check("zoom_wheel_not_filtered", "ev.type === \"wheel\"" in script)
    check("zoom_pinch_two_fingers", "touches.length" in script)
    check("zoom_strokes_do_not_scale", text.count("vector-effect: non-scaling-stroke") >= 2)
    check("hover_tap_handlers_kept",
          'sel.on("mousemove", show).on("mouseleave", hide).on("focus", show).on("blur", hide).on("click", show)'
          in script)

    # --- class colour follows the deck legend position, not the position among classes present ---
    def inv_rows(prefix, labels):
        return [{"kind": "legend_count", "shape_name": f"{prefix}{lab}", "current": f"{lab} (1)"} for lab in labels]
    b_deck = ["0 grant streams", "1 grant stream", "2 grant streams", "3 grant streams", "4+ grant streams"]
    gap_rows = [full({"iso3": "ONE", "indicator_id": "ippf_grant_streams_count", "value": "0", "reference_year": "2026"}),
                full({"iso3": "TWO", "indicator_id": "ippf_grant_streams_count", "value": "3", "reference_year": "2026"})]
    vb = pwm.view("B", gap_rows, crosswalk, {}, {}, inv_rows("Filter button: ", b_deck), NAMES)
    leg = {x["key"]: x["colour"] for x in vb["legend"]}
    check("colour_B_by_deck_position_with_gap", leg.get("3 grant streams") == pwm.PALETTE["B"][3], leg)
    c_deck = ["Full member", "Associate member", "Collaborative Partner"]
    assoc = [full({"iso3": "ONE", "indicator_id": "ippf_funding_streams", "member_status": "associate member",
                   "value_display": "", "reference_year": "2026"})]
    vc = pwm.view("C", assoc, crosswalk, {}, {}, inv_rows("Legend text: ", c_deck), NAMES)
    leg = {x["key"]: x["colour"] for x in vc["legend"]}
    check("colour_C_by_deck_position_with_gap", leg.get("associate member") == pwm.PALETTE["C"][1], leg)

    # --- session A minors (final review of phase d) ---
    risky = {"t": "a <!-- b </script> c <SCRIPT d"}
    try:
        s = pwm._json(risky)
        round_trip = json.loads(s) == risky
    except ValueError as e:
        s, round_trip = "", str(e)
    check("json_round_trips_comment_and_script", round_trip is True, round_trip)
    check("json_no_raw_open_angle", "<" not in s, s)

    # --- refusals ---
    code, log = run(args(out))
    check("refuses_existing_out", code == 2 and out.read_text(encoding="utf-8") == text, (code, log))
    bad = TMP / "decks_missing"
    bad.mkdir()
    code, log = run(args(TMP / "webmap_x.html")[:-4] + ["--decks", str(bad), "--geometry", str(GEO),
                                                        "--out", str(TMP / "webmap_x.html")])
    check("refuses_missing_deck", code == 1 and not (TMP / "webmap_x.html").exists(), (code, log))

    print(f"{'FAILED ' + str(len(FAILS)) if FAILS else 'all ok'}")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
