"""The publish command (SRHR map skill, phase d): one entry point for every publish step.

    python publish.py <step> --map-root <SRHR map data folder> [--decks <deck folder>] [--edition <year>]

Steps (each runs alone; `all` chains them in this order):
  plan      read-only: shape inventory of the decks + swap plan, in publish/<edition>/run_<time>/
  swap      the deck swap from a plan (--plan <swap_plan.csv>); writes to the decks only with --apply
  workbook  publish/<edition>/map_data_<edition>.xlsx
  dataset   publish/<edition>/powerbi_dataset_<edition>.csv and .xlsx
  webmap    publish/<edition>/webmap_<edition>.html (geometry cached once in publish/_geometry/)
  summary   publish/<edition>/webmap_summary_<edition>.html, the page for donors and partners (phase e):
            headline and three maps, no stream or member association names; needs no decks. Reads
            config/who_europe.csv, config/summary_page.csv, config/ma_codes.csv and, when present,
            config/summary_scan_allow.csv
  check     every output against the register: decks (register_deck_check), every workbook
            cell and link, every dataset cell (csv and xlsx), every web map colour, tooltip, legend,
            filter and title, and the summary page (views, headline, forbidden-text scan). Exit 0 only
            when all agree.
  all       plan, then swap only when the plan is empty or --apply is given, then the four builders
            (an output that exists is kept, never rebuilt), then check

Paths come from the map root: map_register/map_register_<edition>.csv (default edition: the latest
register file), config/streams.csv, intelligence_tool/master_countries.csv and source_register.csv.
`--map-root` (or SRHR_MAP_ROOT) and `--decks` take Windows paths with a drive letter on Windows.
Exit codes: 0 done, 1 input problem or a check failed, 2 a target exists or the plan holds a structure
change (phase e), 3 swaps are planned and wait for --apply.
"""
import argparse
import csv
import os
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import computed  # noqa: E402
import deck_shapes  # noqa: E402
import publish_dataset  # noqa: E402
import publish_plan  # noqa: E402
import publish_summary  # noqa: E402
import publish_webmap  # noqa: E402
import publish_workbook  # noqa: E402
import register_deck_check as rdc  # noqa: E402

STEPS = ("plan", "swap", "workbook", "dataset", "webmap", "summary", "check", "all")
NEEDS_DECKS = ("plan", "swap", "webmap", "check", "all")


class Stop(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def _path(raw, what):
    if not raw:
        raise Stop(1, f"stop: give {what}")
    if os.name == "nt" and re.match(r"^/[A-Za-z]/", raw):
        raise Stop(1, f"stop: {what} {raw!r} is a Git Bash path; give the Windows path with a drive letter")
    p = Path(raw)
    if not p.exists():
        raise Stop(1, f"stop: {what} {raw!r} not found")
    return p


class Paths:
    def __init__(self, root, decks, edition):
        self.root = root
        regs = sorted(root.glob("map_register/map_register_*.csv"))
        if edition is None:
            eds = [m.group(1) for p in regs if (m := re.fullmatch(r"map_register_(\d{4})\.csv", p.name))]
            if not eds:
                raise Stop(1, "stop: no map_register_<year>.csv in map_register/")
            edition = max(eds)
        self.edition = edition
        self.register = root / "map_register" / f"map_register_{edition}.csv"
        if not self.register.exists():
            raise Stop(1, f"stop: {self.register.name} not found in map_register/")
        self.crosswalk = root / "config" / "streams.csv"
        self.master = root / "intelligence_tool" / "master_countries.csv"
        self.sources = root / "intelligence_tool" / "source_register.csv"
        self.out = root / "publish" / edition
        self.geometry = root / "publish" / "_geometry" / "countries-50m.json"
        self.d3 = root / "publish" / "_geometry" / "d3-7.9.0.min.js"
        self.decks = decks
        self.workbook = self.out / f"map_data_{edition}.xlsx"
        self.dataset = self.out / f"powerbi_dataset_{edition}.csv"
        self.webmap = self.out / f"webmap_{edition}.html"
        self.summary = self.out / f"webmap_summary_{edition}.html"
        self.ma_codes = root / "config" / "ma_codes.csv"
        self.who = root / "config" / "who_europe.csv"
        self.page_cfg = root / "config" / "summary_page.csv"
        self.allow = root / "config" / "summary_scan_allow.csv"


def _csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# --- steps ------------------------------------------------------------------------------------------

def step_plan(p):
    stem = f"run_{datetime.now():%Y%m%d-%H%M%S}"
    run, i = p.out / stem, 1
    while run.exists():  # two runs in one second get -2, -3: a run folder is never reused
        i += 1
        run = p.out / f"{stem}-{i}"
    run.mkdir(parents=True)
    inv, plan = run / "shape_inventory.csv", run / "swap_plan.csv"
    print(f"edition {p.edition}: plan in {run}")
    rc = deck_shapes.main(["--decks", str(p.decks), "--master", str(p.master), "--out", str(inv)])
    if rc:
        raise Stop(1, "stop: the deck inventory failed (see the lines above)")
    rc = publish_plan.main(["--register", str(p.register), "--inventory", str(inv), "--crosswalk", str(p.crosswalk),
                            "--out", str(plan)])
    if rc == 2:
        raise Stop(2, "stop: the plan holds structure changes: the decks need a rebuild (phase e), not a swap")
    if rc:
        raise Stop(1, "stop: the plan failed (see the lines above)")
    return plan


def step_swap(p, plan, apply=False, copy_to=None):
    if not plan:
        raise Stop(1, "stop: give --plan <run folder>/swap_plan.csv (run the plan step first)")
    import publish_swap  # needs PowerPoint COM only when it runs
    argv = ["--decks", str(p.decks), "--plan", str(plan)] + (["--apply"] if apply else []) + \
           (["--copy-to", str(copy_to)] if copy_to else [])
    if publish_swap.main(argv):
        raise Stop(1, "stop: the swap failed or refused (see the lines above)")


def step_workbook(p):
    rc = publish_workbook.main(["--register", str(p.register), "--sources", str(p.sources), "--master", str(p.master),
                                "--out", str(p.workbook), "--edition", p.edition])
    if rc:
        raise Stop(rc, "stop: workbook step")


def step_dataset(p):
    rc = publish_dataset.main(["--register", str(p.register), "--sources", str(p.sources), "--master", str(p.master),
                               "--out-dir", str(p.out), "--edition", p.edition])
    if rc:
        raise Stop(rc, "stop: dataset step")


def step_webmap(p):
    if not p.webmap.exists():
        publish_webmap.fetch_geometry(p.geometry)
        publish_webmap.fetch_d3(p.d3)
    rc = publish_webmap.main(["--register", str(p.register), "--crosswalk", str(p.crosswalk), "--master", str(p.master),
                              "--decks", str(p.decks), "--geometry", str(p.geometry), "--out", str(p.webmap), "--d3", str(p.d3),
                              "--edition", p.edition])
    if rc:
        raise Stop(rc, "stop: web map step")


def step_summary(p):
    if not p.summary.exists():
        publish_webmap.fetch_geometry(p.geometry)
        publish_webmap.fetch_d3(p.d3)
    rc = publish_summary.main(["--register", str(p.register), "--ma-codes", str(p.ma_codes), "--crosswalk",
                               str(p.crosswalk), "--master", str(p.master), "--who", str(p.who), "--page-config",
                               str(p.page_cfg), "--geometry", str(p.geometry), "--d3", str(p.d3),
                               "--out", str(p.summary), "--edition", p.edition, "--allow", str(p.allow)])
    if rc:
        raise Stop(rc, "stop: summary step")


# --- check ------------------------------------------------------------------------------------------

def _diff(where, got, want, limit=3):
    """Problem lines for cell-by-cell differences between two lists of rows (lists of strings)."""
    out = []
    if len(got) != len(want):
        out.append(f"{where}: {len(got)} rows, the register gives {len(want)}")
    bad = [(i, g, w) for i, (g, w) in enumerate(zip(got, want), start=2) if g != w]
    for i, g, w in bad[:limit]:
        cols = [c for c, (x, y) in enumerate(zip(g, w)) if x != y] or ["row length"]
        out.append(f"{where} row {i}: column(s) {cols} hold {[g[c] for c in cols if isinstance(c, int)]}, "
                   f"the register gives {[w[c] for c in cols if isinstance(c, int)]}")
    if len(bad) > limit:
        out.append(f"{where}: {len(bad) - limit} more row(s) differ")
    return out


def _inputs(p):
    rows, sources, countries, _ = publish_workbook.load_inputs(p.register, p.sources, p.master, p.edition)
    return rows, sources, countries


def check_workbook(p, reg):
    """Every Values cell, every link target and the table range, against the rows the register gives now."""
    from openpyxl import load_workbook
    rows, sources, countries = _inputs(p)
    want_rows = publish_workbook.value_rows(rows, sources, countries)
    ws = load_workbook(p.workbook)["Values"]
    cols = publish_workbook.VALUE_COLUMNS
    link = cols.index("Source link")
    probs = []
    head = [c.value for c in ws[1]][:len(cols)]
    if head != cols:
        probs.append(f"Values columns {head}, expected {cols}")
    got, links = [], []
    for r in ws.iter_rows(min_row=2):
        got.append(["" if c.value is None else str(c.value) for c in r[:len(cols)]])
        links.append(r[link].hyperlink.target if r[link].hyperlink else "")
    want = [[(publish_workbook.OPEN_LINK if v["_url"] else publish_workbook.NO_LINK) if h == "Source link"
             else str(v[h]) for h in cols] for v in want_rows]
    probs += _diff("Values", got, want)
    if links != [v["_url"] for v in want_rows][:len(links)] or len(links) != len(want_rows):
        probs.append("source links differ from the source register")
    ref = ws.tables["MapValues"].ref if "MapValues" in ws.tables else None
    if ref != f"A1:{chr(64 + len(cols))}{len(want_rows) + 1}":
        probs.append(f"table range {ref}, the register needs A1:{chr(64 + len(cols))}{len(want_rows) + 1}")
    return probs


def check_dataset(p, reg):
    """The csv and the xlsx, column order and every cell, against the rows the register gives now."""
    from openpyxl import load_workbook
    rows, sources, countries = _inputs(p)
    cols = publish_dataset.DATASET_COLUMNS
    want_rows = publish_dataset.dataset_rows(rows, sources, countries, p.edition)
    want = [[publish_dataset._csv_cell(r[h]) for h in cols] for r in want_rows]
    with open(p.dataset, encoding="utf-8-sig", newline="") as f:
        got = list(csv.reader(f))
    probs = []
    if not got or got[0] != cols:
        probs.append(f"csv columns {got[0] if got else []}, expected {cols}")
    probs += _diff("csv", got[1:], want)
    xlsx = p.dataset.with_suffix(".xlsx")
    if not xlsx.exists():
        return probs + [f"{xlsx.name} missing"]
    wb = load_workbook(xlsx, read_only=True)
    try:  # a read-only workbook holds the file open on Windows until closed
        num = cols.index("value_number")
        xr = []
        for i, r in enumerate(wb[publish_dataset.DATA_SHEET].iter_rows(values_only=True)):
            cells = list(r[:len(cols)])
            if i and isinstance(cells[num], (int, float)):
                cells[num] = publish_dataset._csv_cell(float(cells[num]))
            xr.append(["" if c is None else str(c) for c in cells])
    finally:
        wb.close()
    if not xr or xr[0] != cols:
        probs.append(f"xlsx columns {xr[0] if xr else []}, expected {cols}")
    probs += _diff("xlsx", xr[1:], [[w[c] if c != num or not w[c] else publish_dataset._csv_cell(float(w[c]))
                                     for c in range(len(cols))] for w in want])
    return probs


def check_webmap(p, reg, crosswalk):
    """Each view's colours, tooltips, legend, filters and titles, against what the register and decks give now."""
    text = p.webmap.read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="map-data">(.*?)</script>', text, re.S)
    if not m:
        return ["no embedded map data"]
    import json
    got = {v["id"]: v for v in json.loads(m.group(1).replace("<\\/", "</"))["views"]}
    try:
        views, _ = publish_webmap.build_views(reg, p.crosswalk, _csv(p.master), p.decks)
    except publish_webmap.Stop as e:
        return [str(e)]
    probs = []
    for v in json.loads(json.dumps(views)):
        g = got.get(v["id"], {})
        for field in ("colour", "tips", "legend", "filters", "title", "subtitle", "legend_title"):
            if g.get(field) != v.get(field):
                gv, wv = g.get(field), v.get(field)
                if isinstance(wv, dict) and isinstance(gv, dict):
                    keys = sorted(k for k in set(gv) | set(wv) if gv.get(k) != wv.get(k))
                    probs.append(f"map {v['id']} {field} differ for {keys[:4]}")
                else:
                    probs.append(f"map {v['id']} {field} differ from the register")
    return probs


def check_summary(p, reg):
    """The kept summary page: views and headline re-derived from the register now, and the
    forbidden-text scan run again on the page as it is on disk."""
    import json
    text = p.summary.read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="map-data">(.*?)</script>', text, re.S)
    if not m:
        return ["no embedded map data"]
    got = json.loads(m.group(1))
    probs = []
    try:
        master = _csv(p.master)
        views, _ = publish_summary.summary_views(reg, master)
        head = publish_summary.headline(reg, publish_summary.load_who(p.who))
        terms = publish_summary.forbidden_terms(p.crosswalk, p.ma_codes)
        allowed = publish_summary.load_allow(p.allow)
        footer = publish_summary.footer_html(publish_summary.load_page_cfg(p.page_cfg))
    except publish_workbook.Stop as e:
        return [str(e)]
    if head["outside"]:
        probs.append("counted in the headline but missing from the WHO European Region list: "
                     + ", ".join(head["outside"]))
    gv = {v.get("id"): v for v in got.get("views", [])}
    extra = sorted(str(i) for i in set(gv) - {v["id"] for v in views})
    if extra:
        probs.append(f"summary page has view id(s) the register does not give: {', '.join(extra)}")
    for v in json.loads(json.dumps(views)):
        for field in ("name", "colour", "tips", "legend", "filters", "title", "subtitle", "legend_title"):
            if gv.get(v["id"], {}).get(field) != v.get(field):
                probs.append(f"summary map {v['id']} {field} differ from the register")
    if got.get("tab_letters") is not False:
        probs.append(f"tab_letters is {got.get('tab_letters')!r}; the summary page shows no map letters (false)")
    if footer not in text:
        probs.append("footer text differs from config/summary_page.csv")
    if got.get("headline") != {"n": head["n"], "m": head["m"]}:
        probs.append(f"headline data {got.get('headline')}, the register gives {head['n']} of {head['m']}")
    sentence = publish_summary.HEADLINE.format(n=head["n"], m=head["m"])
    if sentence not in publish_summary.page_strings(text):
        probs.append(f"headline text on the page is not '{sentence}'")
    for t, s in publish_summary.scan(publish_summary.page_strings(text), terms, allowed):
        probs.append(f"forbidden term {t!r} in {s[:80]!r}")
    return probs


def step_check(p):
    reg = _csv(p.register)
    crosswalk = [(r["key"], r["label"]) for r in _csv(p.crosswalk)]
    bad = 0
    rc = rdc.main(["--register", str(p.register), "--decks", str(p.decks), "--crosswalk", str(p.crosswalk),
                   "--master", str(p.master)])
    print(f"{'ok  ' if rc == 0 else 'FAIL'} decks: register_deck_check exit {rc}")
    bad += rc != 0
    for name, path, fn in (("workbook", p.workbook, lambda: check_workbook(p, reg)),
                           ("dataset", p.dataset, lambda: check_dataset(p, reg)),
                           ("webmap", p.webmap, lambda: check_webmap(p, reg, crosswalk)),
                           ("summary", p.summary, lambda: check_summary(p, reg))):
        if not path.exists():
            print(f"FAIL {name}: {path.name} missing in {path.parent}")
            bad += 1
            continue
        probs = fn()
        print(f"{'ok  ' if not probs else 'FAIL'} {name}: {path.name}" + "".join(f"\n     {x}" for x in probs))
        bad += bool(probs)
    print(f"check: {'every output agrees with the register' if not bad else f'{bad} output(s) disagree'}")
    if bad:
        raise Stop(1, "stop: check failed")


def step_all(p, apply=False):
    plan = step_plan(p)
    n = len(_csv(plan))
    if n and not apply:
        raise Stop(3, f"stop: {n} swap row(s) planned in {plan}. Read the plan, then run "
                      f"'publish.py swap --plan <that file> --apply', and run 'all' again")
    if n:
        step_swap(p, plan, apply=True)
    for name, target, fn in (("workbook", p.workbook, step_workbook), ("dataset", p.dataset, step_dataset),
                             ("webmap", p.webmap, step_webmap), ("summary", p.summary, step_summary)):
        if target.exists():
            print(f"kept {target.name}: it exists and is never rebuilt")
            continue
        fn(p)
    step_check(p)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("step", choices=STEPS)
    ap.add_argument("--map-root", default=os.environ.get("SRHR_MAP_ROOT"))
    ap.add_argument("--decks")
    ap.add_argument("--edition")
    ap.add_argument("--plan")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--copy-to")
    a = ap.parse_args(argv)
    try:
        root = _path(a.map_root, "the map root (--map-root or SRHR_MAP_ROOT)")
        decks = _path(a.decks, "the deck folder (--decks)") if a.step in NEEDS_DECKS else None
        p = Paths(root, decks, a.edition)
        if a.step == "plan":
            step_plan(p)
        elif a.step == "swap":
            step_swap(p, a.plan and _path(a.plan, "the swap plan (--plan)"), a.apply, a.copy_to)
        elif a.step == "all":
            step_all(p, a.apply)
        else:
            {"workbook": step_workbook, "dataset": step_dataset, "webmap": step_webmap, "summary": step_summary,
             "check": step_check}[a.step](p)
    except (Stop, publish_workbook.Stop) as e:
        print(str(e), file=sys.stderr)
        return e.code
    return 0


if __name__ == "__main__":
    sys.exit(main())
