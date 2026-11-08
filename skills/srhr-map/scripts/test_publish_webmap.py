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


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = pwm.main(argv)
        except SystemExit as e:
            code = e.code
    return code, out.getvalue() + err.getvalue()


def args(out):
    return ["--register", str(REG), "--crosswalk", str(CROSS), "--master", str(MASTER), "--decks", str(DECKS),
            "--geometry", str(GEO), "--out", str(out)]


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
    check("scripts_pinned_on_allowed_cdn", srcs and all(
        re.match(r"https" + r"://cdnjs\.cloudflare\.com/ajax/libs/[\w.-]+/\d+\.\d+\.\d+/", s) for s in srcs), srcs)
    check("no_local_path_in_page", not re.search(r"[A-Za-z]:\\\\", text))

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
