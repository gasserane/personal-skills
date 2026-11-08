"""The publish command (SRHR map skill, phase d): one entry point for every publish step.

    python publish.py <step> --map-root <SRHR map data folder> [--decks <deck folder>] [--edition <year>]

Steps (each runs alone; `all` chains them in this order):
  plan      read-only: shape inventory of the decks + swap plan, in publish/<edition>/run_<time>/
  swap      the deck swap from a plan (--plan <swap_plan.csv>); writes to the decks only with --apply
  workbook  publish/<edition>/map_data_<edition>.xlsx
  dataset   publish/<edition>/powerbi_dataset_<edition>.csv and .xlsx
  webmap    publish/<edition>/webmap_<edition>.html (geometry cached once in publish/_geometry/)
  check     every output against the register: decks (register_deck_check), workbook rows and
            confirmations, dataset values, web map colours. Exit 0 only when all agree.
  all       plan, then swap only when the plan is empty or --apply is given, then the three builders
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
import publish_webmap  # noqa: E402
import publish_workbook  # noqa: E402
import register_deck_check as rdc  # noqa: E402

STEPS = ("plan", "swap", "workbook", "dataset", "webmap", "check", "all")
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
        self.decks = decks
        self.workbook = self.out / f"map_data_{edition}.xlsx"
        self.dataset = self.out / f"powerbi_dataset_{edition}.csv"
        self.webmap = self.out / f"webmap_{edition}.html"


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
    rc = publish_webmap.main(["--register", str(p.register), "--crosswalk", str(p.crosswalk), "--master", str(p.master),
                              "--decks", str(p.decks), "--geometry", str(p.geometry), "--out", str(p.webmap),
                              "--edition", p.edition])
    if rc:
        raise Stop(rc, "stop: web map step")


# --- check ------------------------------------------------------------------------------------------

def _key(r):
    return (r["iso3"], r["indicator_id"], r["reference_year"], r["value"])


def check_workbook(p, reg):
    from openpyxl import load_workbook
    ws = load_workbook(p.workbook, read_only=True)["Values"]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    col = publish_workbook.VALUE_COLUMNS.index("Confirmed")
    unticked = sum(1 for r in reg if not r["ticked_by"].strip())
    shown = sum(1 for r in rows if r[col] == publish_workbook.NOT_CONFIRMED)
    probs = []
    if len(rows) != len(reg):
        probs.append(f"{len(rows)} value rows, the register holds {len(reg)}")
    if shown != unticked:
        probs.append(f"{shown} rows marked not yet confirmed, the register has {unticked} unticked")
    return probs


def check_dataset(p, reg):
    rows = _csv(p.dataset)
    probs = []
    if len(rows) != len(reg):
        probs.append(f"{len(rows)} rows, the register holds {len(reg)}")
    if sorted(map(_key, rows)) != sorted(map(_key, reg)):
        diff = sorted(set(map(_key, rows)) ^ set(map(_key, reg)))[:3]
        probs.append(f"values differ from the register, e.g. {diff}")
    return probs


def check_webmap(p, reg, crosswalk):
    text = p.webmap.read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="map-data">(.*?)</script>', text, re.S)
    if not m:
        return ["no embedded map data"]
    import json
    views = {v["id"]: v for v in json.loads(m.group(1).replace("<\\/", "</"))["views"]}
    want = {m_: set(computed.country_classes(m_, reg, crosswalk)) for m_ in "AB"}
    want["C"] = {r["iso3"] for r in reg if r["indicator_id"] == "ippf_funding_streams" and r["member_status"] != "withdrawn"}
    rates = [r for r in reg if r["indicator_id"] == rdc.D_INDICATORS[0] and r["value"].strip()]
    year = max((r["reference_year"] for r in rates), default="")
    want["D"] = {r["iso3"] for r in rates if r["reference_year"] == year}
    probs = []
    for k in "ABCD":
        got = set(views.get(k, {}).get("colour", {}))
        if got != want[k]:
            probs.append(f"map {k} colours {len(got)} countries, the register {len(want[k])} "
                         f"(differ: {sorted(got ^ want[k])[:4]})")
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
                           ("webmap", p.webmap, lambda: check_webmap(p, reg, crosswalk))):
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
                             ("webmap", p.webmap, step_webmap)):
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
            {"workbook": step_workbook, "dataset": step_dataset, "webmap": step_webmap, "check": step_check}[a.step](p)
    except (Stop, publish_workbook.Stop) as e:
        print(str(e), file=sys.stderr)
        return e.code
    return 0


if __name__ == "__main__":
    sys.exit(main())
