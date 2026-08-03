"""Thin command-line driver over ``ane_package.officeops``, plus the workflow
logic that is not Office surgery.

The line this file holds, because Wave 2 settled it and Wave 3 should not
relitigate it: **anything that opens an Office file belongs in officeops**, and
this script calls it. Diffing two lists of strings, spotting an autocorrect flip
and rewriting a .py generator are not Office operations, so they live here and
are tested here. A skill that grows its own Office plumbing is how two
implementations of the same fix end up disagreeing.

Usage:
    python office_repair.py scan     BOOK [--com] [--json]
    python office_repair.py repair   BOOK --edits EDITS.json [--no-strict] [--no-backup]
    python office_repair.py verify   BOOK [--baseline BACKUP] [--expect-tables]
    python office_repair.py diff     EDITED --against GENERATED [--json]
    python office_repair.py archive  GENERATOR.py --canonical ARTEFACT

EDITS.json is a list of {"sheet": ..., "cell": ..., "old": ..., "new": ...}.
``old`` is the value the cell must already hold; the edit is skipped otherwise.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

# --- generated from ane_package.officeops.bootstrap.BOOTSTRAP_SNIPPET ---------
# This script runs from the personal-skills clone, outside the work folder, so
# it has to find ane_package before it can import it.


def _bootstrap_ane_package() -> None:
    try:
        import ane_package  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    candidates = []
    env_root = os.environ.get("WORK_FOLDER_ROOT")
    if env_root:
        candidates.append(Path(env_root))
    candidates.extend(Path(__file__).resolve().parents)
    candidates.append(Path.home() / "OneDrive" / "5 ANE CLAUDE work folder")

    for candidate in candidates:
        if (candidate / "ane_package" / "reporting" / "brand.py").is_file():
            sys.path.insert(0, str(candidate))
            return

    raise ModuleNotFoundError(
        "ane_package not found. Set WORK_FOLDER_ROOT to the work folder, or run "
        "this script from inside it."
    )


_bootstrap_ane_package()
# -----------------------------------------------------------------------------

from ane_package.officeops import (  # noqa: E402
    Checks,
    VerificationError,
    assert_inventory_unchanged,
    extract_text,
    table_row_counts,
    workbook_inventory,
)
from ane_package.officeops import excelcom  # noqa: E402


# ==========================================================================
# canonical mode: comparing two versions of the same artefact
# ==========================================================================

# A change list is only useful if it separates what Ane meant to do from what
# Word did to her while she was doing it. These patterns are the second kind.

_URL_WITH_SPACE = re.compile(r"https?://\S*\s\S")
_SMART = {"‘": "'", "’": "'", "“": '"', "”": '"',
          "–": "-", "—": "-"}


def _strip_accents(text: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFD", text)
        if not unicodedata.combining(char)
    )


def diff_blocks(before: list[str], after: list[str]) -> list[dict]:
    """The change list between two versions, as replace / insert / delete ops.

    Compared on text alone rather than on (location, text) pairs. A redesign
    renumbers every block after the first insertion, and pairing on location
    would report the whole document as changed. Genuinely moved text still shows
    as a delete plus an insert — that is a real change and worth seeing.
    """
    matcher = difflib.SequenceMatcher(a=before, b=after, autojunk=False)
    changes: list[dict] = []
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            continue
        changes.append(
            {
                "op": op,
                "before": before[i1:i2],
                "after": after[j1:j2],
                "at": j1 + 1,
            }
        )
    return changes


def _replaced_pairs(changes: list[dict]) -> list[tuple[str, str, int]]:
    """Line up the old and new text inside each ``replace`` op.

    ``SequenceMatcher`` collapses a run of consecutive changed blocks into one
    ``replace`` carrying several lines on each side, so reading only the
    one-in-one-out ops finds nothing the moment two edits sit next to each other
    — which is most real documents. Equal-length runs pair by position; an
    uneven run pairs each old line with its closest new line, and lines with no
    close match are dropped rather than forced, because a forced pair produces a
    confident flag about two unrelated sentences.
    """
    pairs: list[tuple[str, str, int]] = []
    for change in changes:
        if change["op"] != "replace":
            continue
        olds, news = change["before"], change["after"]
        start = change["at"]
        if len(olds) == len(news):
            pairs.extend((old, new, start + offset)
                         for offset, (old, new) in enumerate(zip(olds, news)))
            continue
        for offset, old in enumerate(olds):
            best = max(
                news,
                key=lambda candidate: difflib.SequenceMatcher(
                    a=old, b=candidate, autojunk=False).ratio(),
                default=None,
            )
            if best is not None:
                pairs.append((old, best, start + offset))
    return pairs


def suspect_artefacts(changes: list[dict], before: list[str],
                      after: list[str]) -> list[dict]:
    """Changes that look like Office did them rather than Ane.

    None of these is a verdict. Each one is a question worth putting in front of
    her, because the cost of the two mistakes is asymmetric: propagating an
    autocorrect flip into the canonical version makes the error permanent and
    invisible, while asking about a deliberate edit costs one line of reply.
    """
    flags: list[dict] = []

    for old, new, at in _replaced_pairs(changes):
        ratio = difflib.SequenceMatcher(a=old, b=new, autojunk=False).ratio()
        if ratio < 0.9 or old == new:
            continue
        change = {"at": at}

        if _strip_accents(old) == new and old != new:
            flags.append({
                "kind": "accents dropped",
                "at": change["at"], "before": old, "after": new,
                "why": "the diacritics are gone and nothing else changed — a "
                       "keyboard or autocorrect artefact, not an edit",
            })
            continue

        normalised_old = "".join(_SMART.get(char, char) for char in old)
        normalised_new = "".join(_SMART.get(char, char) for char in new)
        if normalised_old == normalised_new:
            flags.append({
                "kind": "punctuation autocorrected",
                "at": change["at"], "before": old, "after": new,
                "why": "only quotes or dashes changed shape — Word's autocorrect",
            })
            continue

        if _URL_WITH_SPACE.search(new) and not _URL_WITH_SPACE.search(old):
            flags.append({
                "kind": "space inside a hyperlink",
                "at": change["at"], "before": old, "after": new,
                "why": "a space landed inside a URL, which breaks the link "
                       "while leaving the text looking right",
            })
            continue

        flags.append({
            "kind": "near-identical rewording",
            "at": change["at"], "before": old, "after": new,
            "why": f"{ratio:.0%} identical — check this was deliberate rather "
                   "than a stray keystroke",
        })

    # The 2026-07-22 red flag: a redesigned deck whose body text vanished and
    # left a title-only layer. It reads as a successful extraction, so it has to
    # be caught structurally rather than per change.
    if before and len(after) * 2 < len(before):
        flags.append({
            "kind": "most of the text is gone",
            "at": 0, "before": f"{len(before)} blocks", "after": f"{len(after)} blocks",
            "why": "the edited file has less than half the text blocks of the "
                   "generated one. Either a redesign dropped the body layer, or "
                   "the extraction missed content — check before treating this "
                   "as canonical",
        })

    return flags


# ==========================================================================
# canonical mode: retiring the generator
# ==========================================================================

ARCHIVE_MARKER = "# === ARCHIVED GENERATOR"

_GUARD_TEMPLATE = '''{marker} — canonical source is the hand-edited file ===
#
# {canonical}
#
# Ane hand-edited that file after this script last wrote it. Re-running this
# generator would overwrite formatting-level changes that exist nowhere else:
# chat shows what the system produced, disk shows what she then did to it.
# Folding her edits back into the generator was considered and rejected — it
# loses formatting silently, which is the failure the edit-preservation
# protocol exists to stop.
#
# This guard is code rather than a comment because a comment does not stop
# anyone. Running the script refuses. Running it with --force lets the body
# execute but restores the canonical file byte-for-byte if it changes, so
# regenerated output has to be written under a different name.

_CANONICAL_SOURCE = r"{canonical}"


def _refuse_to_overwrite_canonical() -> None:
    import atexit
    import sys
    from pathlib import Path

    canonical = Path(_CANONICAL_SOURCE)
    if "--force" not in sys.argv:
        print(
            "ARCHIVED: this generator is stale.\\n"
            f"  Canonical source: {{canonical}}\\n"
            "  Edit that file in place (python-docx / openpyxl / python-pptx /\\n"
            "  Office COM), or re-run with --force to regenerate into a\\n"
            "  separate '(regenerated v1)' file for reference only.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    if canonical.is_file():
        original = canonical.read_bytes()

        def _restore() -> None:
            if canonical.is_file() and canonical.read_bytes() != original:
                canonical.write_bytes(original)
                print(
                    f"RESTORED {{canonical}} — this generator wrote over the "
                    "canonical file and the guard put it back. Write regenerated "
                    "output to a '(regenerated v1)' name instead.",
                    file=sys.stderr,
                )

        atexit.register(_restore)


if __name__ == "__main__":
    _refuse_to_overwrite_canonical()
else:  # pragma: no cover - importing is allowed, running is not
    import sys as _sys

    print(
        f"WARNING: {{__name__}} is an ARCHIVED generator; "
        f"{{_CANONICAL_SOURCE!r}} is canonical.",
        file=_sys.stderr,
    )

# === end archive guard ===

'''


def archive_generator(script: Path, canonical: Path) -> str:
    """Prepend a hard refusal to a generator whose output Ane now owns.

    Idempotent: a second run reports and changes nothing, because the usual way
    this gets called twice is a session that does not remember the first.
    """
    source = script.read_text(encoding="utf-8")
    if ARCHIVE_MARKER in source:
        return "already archived"

    guard = _GUARD_TEMPLATE.format(
        marker=ARCHIVE_MARKER,
        canonical=str(canonical).replace("\\", "\\\\"),
    )
    # Straight to the top. A shebang or an encoding line would want to stay
    # first, so they are carried over rather than buried under the banner.
    lines = source.splitlines(keepends=True)
    head = ""
    while lines and (lines[0].startswith("#!") or "coding" in lines[0][:30]):
        head += lines.pop(0)
    script.write_text(head + guard + "".join(lines), encoding="utf-8")
    return "archived"


# ==========================================================================
# commands
# ==========================================================================

def cmd_scan(args: argparse.Namespace) -> int:
    book = Path(args.workbook)
    report: dict = {
        "workbook": str(book),
        "structure": excelcom.scan_workbook(book),
        "errors": excelcom.scan_errors(book),
        "validations": excelcom.scan_validations(book),
        "tables": {name: {"covered": covered, "populated": populated}
                   for name, (covered, populated) in table_row_counts(book).items()},
        "inventory": workbook_inventory(book),
    }
    if args.com:
        report["circular"] = excelcom.find_circular_references(book)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    inventory = report["inventory"]
    print(f"{book.name}")
    print(f"  sheets      : {', '.join(inventory['sheets'])}")
    print(f"  features    : {inventory['tables']} tables, {inventory['charts']} charts, "
          f"{inventory['slicers']} slicers, {inventory['pivot_tables']} pivot tables")
    print(f"  named ranges: {len(inventory['defined_names'])}")

    for name, counts in report["tables"].items():
        gap = "" if counts["covered"] >= counts["populated"] else \
            "  <-- rows fall OUTSIDE the table"
        print(f"  table {name}: ref covers {counts['covered']}, "
              f"{counts['populated']} hold data{gap}")

    errors = report["errors"]
    print(f"\ncached errors: {len(errors)}")
    for item in errors[:25]:
        because = f"  <- {item['formula']}" if item["formula"] else ""
        print(f"  {item['sheet']}!{item['cell']}  {item['error']}{because}")
    if len(errors) > 25:
        print(f"  ... and {len(errors) - 25} more (use --json for all)")
    if not errors:
        print("  none cached. A workbook never opened in Excel caches nothing, "
              "so run with --com to ask Excel directly.")

    fragmented = [rule for rule in report["validations"] if rule["fragmented"]]
    print(f"\ndata validation: {len(report['validations'])} rules, "
          f"{len(fragmented)} fragmented")
    for rule in fragmented:
        print(f"  {rule['sheet']}: {rule['areas']} areas "
              f"({rule['single_row_areas']} single-row) — {rule['sqref'][:60]}")

    if args.com:
        circular = report["circular"]
        print(f"\ncircular references: {len(circular)}")
        for item in circular:
            print(f"  {item.get('sheet')}!{item.get('address')}")

    return 0


def cmd_repair(args: argparse.Namespace) -> int:
    book = Path(args.workbook)
    edits = json.loads(Path(args.edits).read_text(encoding="utf-8"))
    if not isinstance(edits, list):
        print("edits file must be a list of {sheet, cell, old, new}", file=sys.stderr)
        return 2

    before = workbook_inventory(book)
    outcome = excelcom.apply_cell_edits(
        book, edits, strict=not args.no_strict, backup=not args.no_backup
    )

    for item in outcome["applied"]:
        print(f"  applied  {item['sheet']}!{item['cell']}")
    for item in outcome["skipped"]:
        print(f"  SKIPPED  {item['sheet']}!{item['cell']}: expected "
              f"{item['expected']!r}, found {item['found']!r}")

    print(f"\n{len(outcome['applied'])} applied, {len(outcome['skipped'])} skipped")

    # The whole point of a repair is that nothing else moved.
    try:
        assert_inventory_unchanged(book, before)
        print("features intact against the pre-repair inventory")
    except VerificationError as exc:
        print(f"\n{exc}", file=sys.stderr)
        return 1

    if outcome["skipped"]:
        print("\nA skipped cell did not hold the value the payload expected. That "
              "is a stale payload or a wrong address, not a no-op — re-scan "
              "before re-running.", file=sys.stderr)
        return 1
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    book = Path(args.workbook)
    checks = Checks(title=f"office-repair: {book.name}")

    if args.baseline:
        checks.expect("features intact against the baseline",
                      assert_inventory_unchanged, book, Path(args.baseline))
    else:
        inventory = workbook_inventory(book)
        checks.check(bool(inventory["sheets"]),
                     f"workbook opens and reports its sheets ({inventory['sheets']})")

    counts = table_row_counts(book)
    for name, (covered, populated) in counts.items():
        checks.check(covered >= populated,
                     f"table {name}: ref covers {covered} row(s), {populated} hold data")

    errors = excelcom.scan_errors(book)
    checks.check(not errors,
                 f"no cached error values ({len(errors)} found)")
    return checks.report()


def cmd_diff(args: argparse.Namespace) -> int:
    edited, generated = Path(args.edited), Path(args.against)
    before, after = extract_text(generated), extract_text(edited)
    changes = diff_blocks(before, after)
    flags = suspect_artefacts(changes, before, after)

    if args.json:
        print(json.dumps({"changes": changes, "suspect": flags},
                         indent=2, ensure_ascii=False))
        return 0

    print(f"{generated.name} -> {edited.name}")
    print(f"  {len(before)} blocks -> {len(after)} blocks, {len(changes)} change(s)\n")
    for change in changes:
        if change["op"] == "delete":
            for text in change["before"]:
                print(f"  - [{change['at']}] {text}")
        elif change["op"] == "insert":
            for text in change["after"]:
                print(f"  + [{change['at']}] {text}")
        else:
            for text in change["before"]:
                print(f"  - [{change['at']}] {text}")
            for text in change["after"]:
                print(f"  + [{change['at']}] {text}")
        print()

    if flags:
        print(f"{len(flags)} change(s) look like Office rather than Ane — confirm "
              f"each before treating the file as canonical:\n")
        for flag in flags:
            print(f"  [{flag['at']}] {flag['kind']}")
            print(f"      before: {flag['before']}")
            print(f"      after : {flag['after']}")
            print(f"      why   : {flag['why']}\n")
    else:
        print("nothing looks like an Office artefact.")
    return 0


def cmd_archive(args: argparse.Namespace) -> int:
    script, canonical = Path(args.generator), Path(args.canonical)
    if not script.is_file():
        print(f"no such generator: {script}", file=sys.stderr)
        return 2
    if not canonical.is_file():
        # Guarding against a path that does not exist would write a refusal
        # pointing at nothing, which is worse than no guard.
        print(f"canonical file does not exist: {canonical}", file=sys.stderr)
        return 2

    outcome = archive_generator(script, canonical)
    if outcome == "already archived":
        print(f"{script.name} already carries the archive guard; nothing changed.")
        return 0
    print(f"{script.name} archived. It now refuses to run without --force, and "
          f"under --force it restores {canonical.name} if the run touches it.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subs = parser.add_subparsers(dest="command", required=True)

    scan = subs.add_parser("scan", help="read-only diagnosis of a workbook")
    scan.add_argument("workbook")
    scan.add_argument("--com", action="store_true",
                      help="also ask Excel for circular references (opens Excel read-only)")
    scan.add_argument("--json", action="store_true")
    scan.set_defaults(func=cmd_scan)

    repair = subs.add_parser("repair", help="apply guarded per-cell edits via COM")
    repair.add_argument("workbook")
    repair.add_argument("--edits", required=True)
    repair.add_argument("--no-strict", action="store_true",
                        help="write what matched instead of discarding the run")
    repair.add_argument("--no-backup", action="store_true")
    repair.set_defaults(func=cmd_repair)

    verify = subs.add_parser("verify", help="assert on the written workbook")
    verify.add_argument("workbook")
    verify.add_argument("--baseline", help="the backup taken before the repair")
    verify.set_defaults(func=cmd_verify)

    diff = subs.add_parser("diff", help="what changed between generated and hand-edited")
    diff.add_argument("edited")
    diff.add_argument("--against", required=True)
    diff.add_argument("--json", action="store_true")
    diff.set_defaults(func=cmd_diff)

    archive = subs.add_parser("archive", help="retire a generator behind a hard refusal")
    archive.add_argument("generator")
    archive.add_argument("--canonical", required=True)
    archive.set_defaults(func=cmd_archive)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
