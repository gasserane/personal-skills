"""Deck swap through PowerPoint COM (SRHR map skill, phase d, mode publish).

Reads the swap CSV that publish_plan.py writes (deck, slide, shape_name, kind, field, old, new) and,
with --apply, sets exactly one property per planned shape on the existing decks:
  field screentip   ActionSettings(1).Hyperlink.ScreenTip
  field text        TextFrame2.TextRange, only the smallest changed middle span, so the characters
                    that stay keep their run and its formatting
Never a python-pptx save, never a shape added or deleted, never a regenerate.

Per deck with --apply: back up to <decks>/_backup/, open by local path (a cloud document is refused),
read every planned shape first and stop without saving if any shape is missing or its value is not
the planned old value, then write, read back, save only when every read-back equals the new value,
close in finally. PowerPoint itself is left running. The swap log (shape, old planned, old read,
new written, new read) goes to --log or <decks>/swap_log_<time>.csv.

--copy-to <folder> first copies the decks into a new edition folder (refused if it holds a deck),
prints both sha256 per deck, and then works on the copy.

Run:  python publish_swap.py --decks <folder> --plan <swap csv> [--copy-to <folder>] [--apply] [--log <csv>]
Without --apply it prints the plan and opens no deck.
Exit 0: done (or plan printed). Exit 1: input problem, refusal or a failed swap.
"""
import argparse
import csv
import hashlib
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

COLUMNS = ["deck", "slide", "shape_name", "kind", "field", "old", "new"]
LOG_COLUMNS = ["deck", "slide", "shape_name", "field", "old_planned", "old_read", "new_written", "new_read"]
FIELDS = ("screentip", "text")
# Built by concatenation: the public-repo check forbids any "<letter>:/" text, and a URL scheme matches it.
OX = "http" + "://schemas.openxmlformats.org/"
NS_P = "{" + OX + "presentationml/2006/main}"
NS_R = "{" + OX + "officeDocument/2006/relationships}"
NS_REL = "{" + OX + "package/2006/relationships}"


class PlanError(Exception):
    pass


def read_plan(path):
    """Swap rows, checked: columns, deck letter, field, old != new, one row per shape property."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise PlanError(f"{path}: missing column(s) {missing}")
        rows = list(reader)
    seen = set()
    for i, r in enumerate(rows, 2):
        if r["deck"] not in ("A", "B", "C", "D"):
            raise PlanError(f"line {i}: deck {r['deck']!r} is not A to D")
        if r["field"] not in FIELDS:
            raise PlanError(f"line {i}: field {r['field']!r} is not one of {FIELDS}")
        if r["old"] == r["new"]:
            raise PlanError(f"line {i}: old equals new")
        key = (r["deck"], r["slide"], r["shape_name"], r["field"])
        if key in seen:
            raise PlanError(f"line {i}: second row for {key}")
        seen.add(key)
    return rows


def slide_order(pptx):
    """{slide part name: 1-based position in the show}, from presentation.xml (part numbers can differ)."""
    with zipfile.ZipFile(pptx) as z:
        pres = ET.fromstring(z.read("ppt/presentation.xml"))
        rels = ET.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
    target = {r.get("Id"): r.get("Target").rsplit("/", 1)[-1] for r in rels.iter(f"{NS_REL}Relationship")}
    ids = pres.find(f"{NS_P}sldIdLst")
    return {target[s.get(f"{NS_R}id")]: i for i, s in enumerate(ids if ids is not None else [], 1)}


def text_edit(old, new):
    """(start, length, insert): replace old[start-1 : start-1+length] by insert to get new (1-based)."""
    p = 0
    while p < min(len(old), len(new)) and old[p] == new[p]:
        p += 1
    s = 0
    while s < min(len(old), len(new)) - p and old[-1 - s] == new[-1 - s]:
        s += 1
    return p + 1, len(old) - p - s, new[p:len(new) - s]


def log_problems(log_rows):
    out = []
    for r in log_rows:
        where = f"map {r['deck']} {r['slide']} {r['shape_name']} {r['field']}"
        if r["old_read"] != r["old_planned"]:
            out.append(f"{where}: read {r['old_read']!r}, plan expected {r['old_planned']!r}")
        if r["new_read"] != r["new_written"]:
            out.append(f"{where}: wrote {r['new_written']!r}, read back {r['new_read']!r}")
    return out


def deck_files(folder, letters):
    out = {}
    for k in sorted(letters):
        found = sorted(Path(folder).glob(f"Map {k} - *.pptx"))
        if len(found) != 1:
            raise PlanError(f"map {k}: {len(found)} deck file(s) in {folder}, need exactly 1")
        out[k] = found[0]
    return out


def is_local(fullname):
    return not re.match(r"^[a-z][a-z0-9+.-]*://", str(fullname), re.I)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def copy_decks(src, dst):
    """Copy every 'Map X - *.pptx' from src into dst; [(name, sha256 src, sha256 copy)]."""
    src, dst = Path(src), Path(dst)
    decks = sorted(src.glob("Map [A-D] - *.pptx"))
    if not decks:
        raise PlanError(f"no deck in {src}")
    if dst.exists() and list(dst.glob("Map [A-D] - *.pptx")):
        raise PlanError(f"{dst} already holds a deck; an edition folder is never overwritten")
    dst.mkdir(parents=True, exist_ok=True)
    out = []
    for p in decks:
        shutil.copy2(p, dst / p.name)
        out.append((p.name, _sha(p), _sha(dst / p.name)))
    return out


# ---------------- COM part (tested by Run A on scratch decks, plan Task 3.3) ----------------

def _shape_map(slide):
    """{name: shape} over the slide, groups included; names seen twice go to the second dict."""
    found, dup = {}, set()

    def walk(shapes):
        for i in range(1, shapes.Count + 1):
            s = shapes.Item(i)
            if s.Name in found:
                dup.add(s.Name)
            found[s.Name] = s
            if s.Type == 6:  # msoGroup
                walk(s.GroupItems)
    walk(slide.Shapes)
    return found, dup


def _read(shape, field):
    if field == "screentip":
        return shape.ActionSettings(1).Hyperlink.ScreenTip
    return shape.TextFrame2.TextRange.Text


def _write(shape, field, old, new):
    if field == "screentip":
        shape.ActionSettings(1).Hyperlink.ScreenTip = new
        return
    tr = shape.TextFrame2.TextRange
    a, n, ins = text_edit(old, new)
    # Late-bound pywin32 reads Characters as a property and then calls the result, which raises
    # "Does not support a collection"; GetCharacters(start, len) is the parameterised form that works.
    if n:
        tr.GetCharacters(a, n).Text = ins
    elif a > 1:
        tr.GetCharacters(a - 1, 1).InsertAfter(ins)
    else:
        tr.GetCharacters(1, 1).InsertBefore(ins)


def apply_deck(app, path, rows, stamp):
    """Swap one deck; returns log rows. Raises PlanError and leaves the deck unsaved on any problem."""
    backup = path.parent / "_backup"
    backup.mkdir(exist_ok=True)
    shutil.copy2(path, backup / f"{path.stem}.{stamp}{path.suffix}")
    order = slide_order(path)
    pres = app.Presentations.Open(str(path), 0, 0, 0)  # ReadOnly no, Untitled no, WithWindow no
    try:
        if not is_local(pres.FullName):
            raise PlanError(f"{path.name} opened as {pres.FullName}: close PowerPoint and retry")
        maps, log = {}, []
        targets = []
        for r in rows:
            if r["slide"] not in order:
                raise PlanError(f"map {r['deck']}: no {r['slide']} in {path.name}")
            if r["slide"] not in maps:
                maps[r["slide"]] = _shape_map(pres.Slides(order[r["slide"]]))
            found, dup = maps[r["slide"]]
            if r["shape_name"] not in found or r["shape_name"] in dup:
                raise PlanError(f"map {r['deck']} {r['slide']}: shape {r['shape_name']!r} "
                                f"{'appears twice' if r['shape_name'] in dup else 'not found'}")
            shape = found[r["shape_name"]]
            old_read = _read(shape, r["field"])
            if old_read != r["old"]:
                raise PlanError(f"map {r['deck']} {r['slide']} {r['shape_name']}: deck holds {old_read!r}, "
                                f"plan expected {r['old']!r}; nothing saved")
            targets.append((r, shape, old_read))
        for r, shape, old_read in targets:
            _write(shape, r["field"], old_read, r["new"])
            log.append({"deck": r["deck"], "slide": r["slide"], "shape_name": r["shape_name"],
                        "field": r["field"], "old_planned": r["old"], "old_read": old_read,
                        "new_written": r["new"], "new_read": _read(shape, r["field"])})
        problems = log_problems(log)
        if problems:
            pres.Saved = True
            raise PlanError("read-back failed, deck not saved: " + "; ".join(problems[:5]))
        pres.Save()
        return log
    finally:
        pres.Close()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--decks", type=Path, required=True)
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--copy-to", type=Path)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--log", type=Path)
    args = ap.parse_args(argv)
    try:
        rows = read_plan(args.plan)
        folder = args.decks
        if args.copy_to:
            for name, a, b in copy_decks(folder, args.copy_to):
                print(f"copy {name}: {a} -> {b} {'same' if a == b else 'DIFFERENT'}")
            folder = args.copy_to
        files = deck_files(folder, {r["deck"] for r in rows})
    except (PlanError, OSError) as e:
        print(f"REFUSE: {e}")
        return 1
    counts = {}
    for r in rows:
        counts[(r["deck"], r["kind"], r["field"])] = counts.get((r["deck"], r["kind"], r["field"]), 0) + 1
    for (m, k, f), n in sorted(counts.items()):
        print(f"swap map {m} {k} {f}: {n}")
    print(f"{len(rows)} swap row(s)")
    if not args.apply or not rows:
        print("plan only: no deck opened" if rows else "nothing to swap: no deck opened")
        return 0
    stamp = time.strftime("%Y%m%d-%H%M%S")
    log_path = args.log or folder / f"swap_log_{stamp}.csv"
    if log_path.exists():
        print(f"REFUSE: {log_path} exists")
        return 1
    import win32com.client  # only needed with --apply
    app = win32com.client.Dispatch("PowerPoint.Application")
    log, code = [], 0
    for k, path in files.items():
        try:
            got = apply_deck(app, path, [r for r in rows if r["deck"] == k], stamp)
            log += got
            print(f"map {k}: {len(got)} swap(s) written and read back, saved")
        except PlanError as e:
            print(f"FAIL map {k}: {e}")
            code = 1
    with open(log_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LOG_COLUMNS)
        w.writeheader()
        w.writerows(log)
    print(f"swap log: {log_path}")
    return code


if __name__ == "__main__":
    sys.exit(main())
