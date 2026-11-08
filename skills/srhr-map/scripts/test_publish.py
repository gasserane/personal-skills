"""Planted tests for publish.py (SRHR map skill, phase d, the publish command).

An invented map root in a temporary folder: register, config, master list, sources, fake decks and an
invented topology (no network). Countries, codes and streams are made up. Run:
    python test_publish.py
"""
import csv
import html
import io
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import publish  # noqa: E402
import publish_workbook as pw  # noqa: E402
import test_publish_webmap as twm  # noqa: E402
import test_register_deck_check as trc  # noqa: E402

FAILS = []
TMP = Path(tempfile.mkdtemp(prefix="srhr_pub_"))
ED = "2031"


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ': ' + str(detail)[:400]}")
    if not cond:
        FAILS.append(name)


def write_csv(path, fields, rows):
    """Plain UTF-8, no BOM: the real map files have none, and register_deck_check reads them as such."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return path


def make_root(root: Path):
    for d in ("map_register", "config", "intelligence_tool", "publish/_geometry", "decks"):
        (root / d).mkdir(parents=True, exist_ok=True)
    rows = [twm.full(r) for r in trc.REG]
    for i, r in enumerate(rows):
        r["source_id"] = "src_a"
        if i % 2 == 0:
            r["ticked_by"], r["tick_date"] = "Reviewer One", "2031-01-02"
    write_csv(root / "map_register" / "map_register_2030.csv", list(rows[0]), rows[:3])
    write_csv(root / "map_register" / f"map_register_{ED}.csv", list(rows[0]), rows)
    write_csv(root / "config" / "streams.csv", ["key", "label", "group", "colour", "ledger_names"],
                  [{"key": k, "label": v, "group": "g", "colour": "", "ledger_names": ""} for k, v in trc.CROSS])
    write_csv(root / "intelligence_tool" / "master_countries.csv", ["country", "iso3", "m49"],
                  [{"country": n, "iso3": i, "m49": twm.M49[i]} for n, i in trc.NAMES.items()])
    write_csv(root / "config" / "ma_codes.csv", ["ma_code", "iso3", "org_name"],
              [{"ma_code": "777", "iso3": "ONE", "org_name": "Org Invented One"}])
    write_csv(root / "config" / "who_europe.csv", ["iso3", "country"],
              [{"iso3": i, "country": n} for n, i in trc.NAMES.items()])
    write_csv(root / "config" / "summary_page.csv", ["key", "value"],
              [{"key": "contact", "value": "x@example.org"}, {"key": "author_unit", "value": "Unit"},
               {"key": "disclosure", "value": "Text."}])
    write_csv(root / "config" / "context_names.csv", ["geometry_name", "shown_name"],
              [{"geometry_name": "Context-land", "shown_name": "Context Land Renamed"}])
    write_csv(root / "intelligence_tool" / "source_register.csv", ["source_id", "source", "publisher", "url"],
                  [{"source_id": "src_a", "source": "Source A", "publisher": "Agency A", "url": ""}])
    (root / "publish" / "_geometry" / "countries-50m.json").write_text(json.dumps(twm.TOPO), encoding="utf-8")
    (root / "publish" / "_geometry" / "d3-7.9.0.min.js").write_text(twm.FAKE_D3, encoding="utf-8")
    twm.pwm.D3_SRI = twm.sri(twm.FAKE_D3.encode("utf-8"))  # the cache check accepts the invented library
    twm.pwm.GEOMETRY_SHA256 = hashlib.sha256(
        (root / "publish" / "_geometry" / "countries-50m.json").read_bytes()).hexdigest()  # and the invented topology
    for m, tips in trc.TIPS.items():
        sps = "".join(f'<p:sp><p:nvSpPr><p:cNvPr id="{i + 2}" name="Country: {html.escape(c)}">'
                      f'<a:hlinkHover r:id="" tooltip="{html.escape(t)}"/></p:cNvPr></p:nvSpPr></p:sp>'
                      for i, (c, t) in enumerate(tips.items()))
        with zipfile.ZipFile(root / "decks" / f"Map {m} - invented.pptx", "w") as z:
            z.writestr("ppt/slides/slide1.xml", f"<p:sld><p:cSld><p:spTree>{sps}</p:spTree></p:cSld></p:sld>")
    return root


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = publish.main(list(argv))
        except SystemExit as e:
            code = e.code
    return code, out.getvalue() + err.getvalue()


def main():
    root = make_root(TMP / "root")
    base = ["--map-root", str(root), "--decks", str(root / "decks")]
    pub = root / "publish" / ED

    # --- path rules ---
    if os.name == "nt":
        code, log = run("check", "--map-root", "/c/srhr/map", "--decks", str(root / "decks"))
        check("refuses_git_bash_path", code == 1 and "Windows path" in log, (code, log))
    code, log = run("workbook", "--map-root", str(TMP / "nowhere"))
    check("refuses_missing_root", code == 1 and "not found" in log, (code, log))

    # --- plan: read-only, writes a run folder, clean on an agreeing register ---
    code, log = run("plan", *base)
    runs = sorted(pub.glob("run_*"))
    check("plan_exit_0", code == 0, log)
    check("plan_writes_run_folder", len(runs) == 1 and (runs[0] / "shape_inventory.csv").exists()
          and (runs[0] / "swap_plan.csv").exists(), [p.name for p in pub.glob("*")])
    check("plan_edition_is_latest_register", f"edition {ED}" in log, log)
    check("plan_reports_swap_rows", "0 swap row(s)" in log, log)

    # --- swap: needs a plan; without --apply it opens no deck ---
    code, log = run("swap", *base)
    check("swap_needs_plan", code == 1 and "--plan" in log, (code, log))
    if runs:
        code, log = run("swap", *base, "--plan", str(runs[0] / "swap_plan.csv"))
        check("swap_dry_run_opens_nothing", code == 0 and "nothing to swap" in log, (code, log))

    # --- builders ---
    for sub, target in (("workbook", pub / f"map_data_{ED}.xlsx"),
                        ("dataset", pub / f"powerbi_dataset_{ED}.csv"),
                        ("webmap", pub / f"webmap_{ED}.html"),
                        ("summary", pub / f"webmap_summary_{ED}.html")):
        code, log = run(sub, *base)
        check(f"{sub}_exit_0", code == 0 and target.exists(), (code, log))
    code, log = run("webmap", *base)
    check("builder_refuses_existing", code == 2 and "never overwritten" in log, (code, log))
    # PROMPT 7 names (Ane 2026-11-09): grey context names come from config/context_names.csv, on both pages
    for nm, f in (("webmap", pub / f"webmap_{ED}.html"), ("summary", pub / f"webmap_summary_{ED}.html")):
        txt = f.read_text(encoding="utf-8") if f.exists() else ""
        check(f"{nm}_context_name_from_config",
              '"name":"Context Land Renamed"' in txt and '"name":"Context-land"' not in txt, nm)

    # --- check agrees ---
    code, log = run("check", *base)
    check("check_exit_0_when_all_agree", code == 0, log)
    for part in ("decks", "workbook", "dataset", "webmap", "summary"):
        check(f"check_reports_{part}", f"ok   {part}" in log, log)
    code, log = run("summary", "--map-root", str(root))
    check("summary_needs_no_decks", code == 2 and "never overwritten" in log, (code, log))

    # --- check fails on a hand-edited headline in the kept summary page ---
    sm = pub / f"webmap_summary_{ED}.html"
    s_text = sm.read_text(encoding="utf-8")
    sm.write_text(s_text.replace("work in 2 of the 3", "work in 9 of the 3", 1), encoding="utf-8")
    code, log = run("check", *base)
    check("check_summary_flags_stale_headline", "work in 2 of the 3" in s_text and code == 1
          and "FAIL summary" in log and "headline" in log, log)
    sm.write_text(s_text.replace('"headline":{"n":2', '"headline":{"n":9', 1), encoding="utf-8")
    code, log = run("check", *base)
    check("check_summary_flags_stale_headline_data", '"headline":{"n":2' in s_text and code == 1
          and "FAIL summary" in log, log)
    sm.write_text(s_text.replace("Point at or tap", "Stream two: point at or tap", 1), encoding="utf-8")
    code, log = run("check", *base)
    check("check_summary_reruns_scan", code == 1 and "FAIL summary" in log and "Stream two" in log, log)
    # review minor 5: view names, extra view ids, tab_letters, footer text, outside list, a stale tip
    s_data = json.loads(re.search(r'id="map-data">(.*?)</script>', s_text, re.S).group(1))
    stale = json.loads(json.dumps(s_data))
    first = sorted(stale["views"][0]["tips"])[0]
    stale["views"][0]["tips"][first] += " (old)"
    extra = json.loads(json.dumps(s_data))
    extra["views"].append(dict(extra["views"][0], id="Z"))
    for case, edited, want in (
            ("check_summary_flags_view_name", s_text.replace('"name":"Members and partners"', '"name":"Members"', 1),
             "name"),
            ("check_summary_flags_extra_view_id", s_text.replace(json.dumps(s_data["views"], separators=(",", ":")),
                                                                 json.dumps(extra["views"], separators=(",", ":")), 1),
             "Z"),
            ("check_summary_flags_tab_letters", s_text.replace('"tab_letters":false', '"tab_letters":true', 1),
             "tab_letters"),
            ("check_summary_flags_footer_text", s_text.replace("Prepared by Unit.", "Prepared by Old Unit.", 1),
             "footer"),
            ("check_summary_flags_stale_tip", s_text.replace(json.dumps(s_data["views"], separators=(",", ":")),
                                                             json.dumps(stale["views"], separators=(",", ":")), 1),
             "tips")):
        sm.write_text(edited, encoding="utf-8")
        code, log = run("check", *base)
        check(case, edited != s_text and code == 1 and "FAIL summary" in log and want in log.split("FAIL summary")[-1],
              (edited != s_text, code, log[-400:]))
    sm.write_text(s_text, encoding="utf-8")
    who_path = root / "config" / "who_europe.csv"
    who_keep = who_path.read_bytes()
    who_path.write_text("iso3,country\nONE,Country One\nGON,Country Gone\nXQX,Country Invented\n", encoding="utf-8")
    code, log = run("check", *base)
    check("check_summary_flags_outside_list", code == 1 and "FAIL summary" in log and "TWO" in log
          and "WHO European Region" in log, log[-400:])
    who_path.write_bytes(who_keep)
    sm.write_text(s_text, encoding="utf-8")

    # --- check fails on a planted change in an output ---
    data = pub / f"powerbi_dataset_{ED}.csv"
    keep = data.read_bytes()
    with open(data, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    rows[0]["value"] = rows[0]["value"] + "9"
    with open(data, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    code, log = run("check", *base)
    check("check_fails_on_planted_dataset_change", code == 1 and "FAIL dataset" in log, log)
    data.write_bytes(keep)
    wm = pub / f"webmap_{ED}.html"
    text = wm.read_text(encoding="utf-8")
    wm.write_text(text.replace('"colour":{"ONE":', '"colour":{"XXX":', 1), encoding="utf-8")
    code, log = run("check", *base)
    check("check_fails_on_planted_webmap_change", code == 1 and "FAIL webmap" in log, log)
    wm.write_text(text, encoding="utf-8")
    code, log = run("check", *base)
    check("check_green_again_after_restore", code == 0, log)
    # PROMPT 7 names: a page holding an old grey name fails check (each page), and so does a missing config file
    for nm, f in (("webmap", wm), ("summary", sm)):
        t = f.read_text(encoding="utf-8")
        f.write_text(t.replace('"name":"Context Land Renamed"', '"name":"Context-land"', 1), encoding="utf-8")
        code, log = run("check", *base)
        check(f"check_flags_stale_context_name_{nm}", code == 1 and f"FAIL {nm}" in log
              and "grey" in log.split(f"FAIL {nm}")[-1], log[-400:])
        f.write_text(t, encoding="utf-8")
    cn = root / "config" / "context_names.csv"
    cn_keep = cn.read_bytes()
    cn.unlink()
    code, log = run("check", *base)
    check("check_stops_without_context_names", code == 1 and "context_names.csv" in log, log[-400:])
    wm.rename(wm.with_name(wm.name + ".keep"))
    code, log = run("webmap", *base)
    check("webmap_stops_without_context_names", code == 1 and "context_names.csv" in log and not wm.exists(),
          (code, log[-300:]))
    sm.rename(sm.with_name(sm.name + ".keep"))
    code, log = run("summary", "--map-root", str(root))
    check("summary_stops_without_context_names", code == 1 and "context_names.csv" in log and not sm.exists(),
          (code, log[-300:]))
    wm.with_name(wm.name + ".keep").rename(wm)
    sm.with_name(sm.name + ".keep").rename(sm)
    cn.write_bytes(cn_keep)
    code, log = run("check", *base)
    check("check_green_after_context_names_restored", code == 0, log)

    # --- check sees stale values: change one register value (same rows, same ticks, same coloured set),
    #     rebuild only the dataset; the kept workbook and web map must still fail (final review I-1) ---
    regp = root / "map_register" / f"map_register_{ED}.csv"
    reg_keep = regp.read_bytes()
    with open(regp, encoding="utf-8", newline="") as f:
        rr = list(csv.DictReader(f))
    hit = next(r for r in rr if r["indicator_id"] == "ecdc_hiv_diagnosis_rate" and r["value"].strip())
    hit["value"] = hit["value_display"] = str(float(hit["value"]) + 30)
    write_csv(regp, list(rr[0]), rr)
    for n in (f"powerbi_dataset_{ED}.csv", f"powerbi_dataset_{ED}.xlsx"):
        (pub / n).rename(pub / (n + ".old"))
    code, log = run("dataset", *base)
    code, log = run("check", *base)
    check("check_fails_stale_workbook_value", code == 1 and "FAIL workbook" in log, log)
    check("check_fails_stale_webmap_value", code == 1 and "FAIL webmap" in log, log)
    check("check_dataset_ok_after_rebuild", "ok   dataset" in log, log)
    regp.write_bytes(reg_keep)
    for n in (f"powerbi_dataset_{ED}.csv", f"powerbi_dataset_{ED}.xlsx"):
        (pub / n).unlink()
        (pub / (n + ".old")).rename(pub / n)
    # the dataset .xlsx is checked against the register too, not only the csv
    from openpyxl import load_workbook
    xp = pub / f"powerbi_dataset_{ED}.xlsx"
    x_keep = xp.read_bytes()
    wb = load_workbook(xp)
    wb["Data"]["G2"] = str(wb["Data"]["G2"].value) + "9"
    wb.save(xp)
    code, log = run("check", *base)
    check("check_fails_on_planted_dataset_xlsx_change", code == 1 and "FAIL dataset" in log, log)
    xp.write_bytes(x_keep)
    # a hand edit of a web map tooltip
    text = wm.read_text(encoding="utf-8")
    m_ = re.search(r'"tips":\{"[A-Z]{3}":"', text)
    wm.write_text(text[:m_.end()] + "EDITED " + text[m_.end():], encoding="utf-8")
    code, log = run("check", *base)
    check("check_fails_on_edited_webmap_tip", code == 1 and "FAIL webmap" in log, log)
    wm.write_text(text, encoding="utf-8")
    code, log = run("check", *base)
    check("check_green_after_restoring_all", code == 0, log)

    # --- check fails when an output is missing ---
    root2 = make_root(TMP / "root2")
    code, log = run("check", "--map-root", str(root2), "--decks", str(root2 / "decks"))
    check("check_fails_on_missing_outputs", code == 1 and "missing" in log, log)

    # --- all: chains the steps; a second run keeps what exists ---
    root3 = make_root(TMP / "root3")
    b3 = ["--map-root", str(root3), "--decks", str(root3 / "decks")]
    code, log = run("all", *b3)
    p3 = root3 / "publish" / ED
    check("all_exit_0", code == 0, log)
    check("all_writes_every_output", all((p3 / n).exists() for n in (
        f"map_data_{ED}.xlsx", f"powerbi_dataset_{ED}.csv", f"powerbi_dataset_{ED}.xlsx", f"webmap_{ED}.html",
        f"webmap_summary_{ED}.html")),
        [p.name for p in p3.glob("*")])
    code, log = run("all", *b3)
    check("all_second_run_keeps_outputs", code == 0 and "kept" in log, log)

    shutil.rmtree(TMP, ignore_errors=True)
    print(f"{'FAILED ' + str(len(FAILS)) if FAILS else 'all ok'}")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
