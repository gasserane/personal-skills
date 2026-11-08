"""Planted tests for publish.py (SRHR map skill, phase d, the publish command).

An invented map root in a temporary folder: register, config, master list, sources, fake decks and an
invented topology (no network). Countries, codes and streams are made up. Run:
    python test_publish.py
"""
import csv
import html
import io
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
    write_csv(root / "config" / "streams.csv", ["key", "label", "group", "colour"],
                  [{"key": k, "label": v, "group": "g", "colour": ""} for k, v in trc.CROSS])
    write_csv(root / "intelligence_tool" / "master_countries.csv", ["country", "iso3", "m49"],
                  [{"country": n, "iso3": i, "m49": twm.M49[i]} for n, i in trc.NAMES.items()])
    write_csv(root / "intelligence_tool" / "source_register.csv", ["source_id", "source", "publisher", "url"],
                  [{"source_id": "src_a", "source": "Source A", "publisher": "Agency A", "url": ""}])
    (root / "publish" / "_geometry" / "countries-50m.json").write_text(json.dumps(twm.TOPO), encoding="utf-8")
    (root / "publish" / "_geometry" / "d3-7.9.0.min.js").write_text(twm.FAKE_D3, encoding="utf-8")
    twm.pwm.D3_SRI = twm.sri(twm.FAKE_D3.encode("utf-8"))  # the cache check accepts the invented library
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
                        ("webmap", pub / f"webmap_{ED}.html")):
        code, log = run(sub, *base)
        check(f"{sub}_exit_0", code == 0 and target.exists(), (code, log))
    code, log = run("webmap", *base)
    check("builder_refuses_existing", code == 2 and "never overwritten" in log, (code, log))

    # --- check agrees ---
    code, log = run("check", *base)
    check("check_exit_0_when_all_agree", code == 0, log)
    for part in ("decks", "workbook", "dataset", "webmap"):
        check(f"check_reports_{part}", f"ok   {part}" in log, log)

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
        f"map_data_{ED}.xlsx", f"powerbi_dataset_{ED}.csv", f"powerbi_dataset_{ED}.xlsx", f"webmap_{ED}.html")),
        [p.name for p in p3.glob("*")])
    code, log = run("all", *b3)
    check("all_second_run_keeps_outputs", code == 0 and "kept" in log, log)

    shutil.rmtree(TMP, ignore_errors=True)
    print(f"{'FAILED ' + str(len(FAILS)) if FAILS else 'all ok'}")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
