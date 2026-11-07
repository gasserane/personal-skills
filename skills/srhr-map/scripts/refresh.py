"""Refresh the SRHR map register from new drop-in files (SRHR map skill, phase c, spec section 6 steps 2 to 7).

    python refresh.py list    --year 2025 [--topic HIV|funding] [--map-root DIR]
    python refresh.py check   --year 2025 [--topic ...] [--edition N]
    python refresh.py review  --year 2025 [--topic ...] [--edition N]
    python refresh.py apply   --year 2025 --workbook PATH [--edition N]
    python refresh.py approve --year 2025 --by NAME [--edition N]

--year is the reporting year of the new files; --edition (default year + 1) is the register edition
being built. The map root is the organisation's "SRHR map data" folder: --map-root, else the
SRHR_MAP_ROOT environment variable. Its layout is described in derive_rows.py.

list    names the files expected in drop_in/<year>/ and says which are there.
check   checks each file there against its contract; the first problem stops with one plain line.
review  check, then derive proposed rows, compare them with the last edition, save the run file
        (review/run_<edition>.json) and write review/review_<edition>_<timestamp>.xlsx.
apply   writes the answered workbook into map_register/map_register_<edition>.csv.
approve records the owner's approval once every change carries a person's tick.

Exit code 0 = done, 1 = stopped or refused (the reason is printed), 2 = the map root is unknown.
"""
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import apply_answers as aa  # noqa: E402
import compare_register as cr  # noqa: E402
import config_tables  # noqa: E402
import derive_rows as dr  # noqa: E402
import dropin_check as dc  # noqa: E402
import review_workbook as rw  # noqa: E402

NO_ROOT = ("Tell me where the SRHR map data folder is: pass --map-root <folder>, "
           "or set SRHR_MAP_ROOT to that folder.")

# (contract file, role, which year the file name and rows carry, topic, what it is for)
EXPECTED = [
    ("ippf_dhis2_annual.v1.json", "services", "reporting", "HIV", "service statistics: HIV service counts"),
    ("ippf_dhis2_annual.v1.json", "global_indicators", "reporting", None,
     "optional: used only to build config\\ma_codes.csv"),
    ("ippf_subgranting.v1.json", "ledger_projects", "edition", "funding",
     "grant ledger: funding streams per country (also needs its overview sheet)"),
    ("ippf_subgranting.v1.json", "ledger_overview", "edition", "funding", "grant ledger: grant streams held"),
    ("ippf_business_plan_focus.v1.json", "coding_sheet", "edition", "HIV", "business-plan focus coding sheet"),
]


def _spec(contract_file, role):
    c = dc.load_contract(dr.CONTRACTS / contract_file)
    return c, next(f for f in c["files"] if f["role"] == role)


def _expected(root, year, edition, topic):
    """Yield (contract, role, pattern, file year, found path or None, purpose)."""
    folder = root / "drop_in" / str(year)
    for cf, role, which, t, purpose in EXPECTED:
        if topic and t not in (topic, None):
            continue
        c, spec = _spec(cf, role)
        yr = year if which == "reporting" else edition
        pattern = spec["pattern"].format(year=yr)
        where = f"{dr.SUBFOLDER[cf]}\\{pattern}"
        yield c, role, where, yr, dr.find_dropin(folder, cf, pattern), purpose


def cmd_list(root, year, edition, topic):
    print(f"Files expected in drop_in\\{year} (reporting year {year}, register edition {edition}):")
    for c, role, pattern, yr, found, purpose in _expected(root, year, edition, topic):
        state = f"found: {found.name}" if found else "not found"
        print(f"  {pattern:<42} {c['contract_id']}/{role} ({purpose}) -> {state}")
    return 0


def cmd_check(root, year, edition, topic):
    print(f"Checking drop_in\\{year} against the contracts ...")
    seen = 0
    for c, role, pattern, yr, found, purpose in _expected(root, year, edition, topic):
        if found is None:
            print(f"  not found: {pattern} ({purpose}); that part is not refreshed")
            continue
        seen += 1
        problems = dc.check_file(c, role, found, yr)
        if problems:
            first = problems[0]
            if first.startswith(found.name + ":"):
                first = first[len(found.name) + 1:]
            first = first.removeprefix("header:").strip()
            print(f"Stopped: {found.name} does not match its contract: {first}. Fix the file and run check again.")
            return 1
        print(f"  ok: {found.name} ({c['contract_id']}/{role})")
    if not seen:
        print(f"Stopped: no drop-in file found in drop_in\\{year}. Put the files there and run check again.")
        return 1
    return 0


def cmd_review(root, year, edition, topic):
    if cmd_check(root, year, edition, topic):
        return 1
    last, why = aa._refusal(root, edition)
    if why:
        print(why.replace("Refused:", "Stopped:", 1))
        return 1
    baseline = aa._read(aa._edition_path(root, last))
    try:
        rows, problems, covered = dr.derive(root, year, topic, baseline, edition)
    except (dr.RefreshStop, config_tables.ConfigError) as e:
        print(f"Stopped: {e}")
        return 1
    changes = cr.compare(baseline, rows, covered)
    lines = cr.group_changes(changes)
    run = aa.save_run(root, edition, year, last, changes)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    book = rw.write_workbook(lines, changes, root / "review" / f"review_{edition}_{stamp}.xlsx", edition, year,
                             notes=problems)
    must = sum(1 for l in lines if l.sheet == "Must check")
    print(f"Compared with edition {last}: {len(changes)} change(s), {must} line(s) to check, "
          f"{len(lines) - must} optional.")
    for p in problems:
        print(f"  note: {p}")
    print(f"Saved {run.name}. Workbook to answer: {book}")
    return 0


def cmd_apply(root, edition, workbook):
    if not workbook:
        print("Refused: name the answered workbook with --workbook.")
        return 1
    res = aa.apply(root, edition, Path(workbook))
    fatal = [p for p in res.problems if p.startswith(("Refused", "Nothing written", "Write undone"))]
    for p in res.problems:
        print(p if p in fatal else f"  note: {p}")
    if fatal:
        return 1
    print(f"Wrote map_register_{edition}.csv: {res.written} change row(s), {res.ticked} ticked, "
          f"{res.unticked} still need a tick.")
    return 0


def cmd_approve(root, edition, by):
    try:
        out = aa.approve(root, edition, by)
    except aa.ApproveRefused as e:
        print(str(e))
        return 1
    print(f"Approved edition {edition}: {out.name}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["list", "check", "review", "apply", "approve"])
    ap.add_argument("--year", type=int, required=True, help="reporting year of the new drop-in files")
    ap.add_argument("--edition", type=int, help="register edition to build (default: year + 1)")
    ap.add_argument("--topic", choices=["HIV", "funding"], help="refresh one topic only (default: all)")
    ap.add_argument("--map-root", help="the SRHR map data folder (default: SRHR_MAP_ROOT)")
    ap.add_argument("--workbook", help="apply: the answered review workbook")
    ap.add_argument("--by", help="approve: the approver's name")
    a = ap.parse_args(argv)
    root = a.map_root or os.environ.get("SRHR_MAP_ROOT")
    if not root or not Path(root).is_dir():
        print(NO_ROOT if not root else f"{NO_ROOT} (not a folder: {root})")
        return 2
    root, edition = Path(root), a.edition or a.year + 1
    if a.command == "list":
        return cmd_list(root, a.year, edition, a.topic)
    if a.command == "check":
        return cmd_check(root, a.year, edition, a.topic)
    if a.command == "review":
        return cmd_review(root, a.year, edition, a.topic)
    if a.command == "apply":
        return cmd_apply(root, edition, a.workbook)
    return cmd_approve(root, edition, a.by)


if __name__ == "__main__":
    sys.exit(main())
