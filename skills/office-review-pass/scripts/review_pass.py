"""Thin command-line driver over ``ane_package.officeops``.

Deliberately thin. Every Office operation below is one call into officeops; this
file adds argument parsing, JSON loading and printing, and nothing else. When a
mode needs a capability officeops does not have, the addition belongs in
officeops with its own test — not here. A skill that grows its own Office
plumbing is how two implementations of the same fix end up disagreeing.

Usage:
    python review_pass.py read      DOC [--out FILE] [--no-resolved]
    python review_pass.py annotate  DOC --comments COMMENTS.json [--author NAME] [--no-backup]
    python review_pass.py track     DOC --edits EDITS.json [--author NAME] [--out FILE]
    python review_pass.py revisions DOC
    python review_pass.py revise    DOC --edits EDITS.json [--headers] [--no-backup]
    python review_pass.py verify    DOC [--expect-branded]

EDITS.json is either {"old text": "new text", ...} or
[{"old": "...", "new": "..."}, ...]. Order is preserved in the list form.
COMMENTS.json is either {"anchor words": "comment text", ...} or
[{"match": "...", "text": "...", "author": "...", "initials": "..."}, ...];
author and initials are optional per item and default to --author.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
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
    CommentRequest,
    TrackedEditor,
    VerificationError,
    add_comments_in_place,
    assert_branded,
    assert_header_footer_present,
    docx_word_count,
    read_comments,
    read_revisions,
    render_review,
    stranded_hyperlinks,
)


def _load_edits(path: Path) -> list[tuple[str, str]]:
    """Accept both shapes, because both are natural to write by hand."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return [(str(old), str(new)) for old, new in data.items()]
    pairs = []
    for index, item in enumerate(data):
        if "old" not in item:
            raise ValueError(f"edit {index}: no 'old' key")
        pairs.append((str(item["old"]), str(item.get("new", ""))))
    return pairs


def _load_comment_requests(path: Path, default_author: str) -> list[CommentRequest]:
    """Both shapes, mirroring ``_load_edits``: a dict maps anchor to comment text."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [{"match": match, "text": text} for match, text in data.items()]
    requests = []
    for index, item in enumerate(data):
        if "match" not in item or "text" not in item:
            raise ValueError(f"comment {index}: needs both 'match' and 'text' keys")
        requests.append(CommentRequest(
            match=str(item["match"]),
            text=str(item["text"]),
            author=str(item.get("author", default_author)),
            initials=str(item.get("initials", "")),
        ))
    return requests


def cmd_read(args: argparse.Namespace) -> int:
    text = render_review(args.document, include_resolved=not args.no_resolved)
    if not args.out:
        print(text)
        return 0
    Path(args.out).write_text(text, encoding="utf-8")
    # The rendering already states its own counts on line 3; reprinting them from
    # a second walk is how the two go out of step.
    summary = text.splitlines()[2]
    print(f"wrote {args.out}: {summary}")
    return 0


def cmd_annotate(args: argparse.Namespace) -> int:
    source = Path(args.document)
    requests = _load_comment_requests(Path(args.comments), args.author)

    # The five-word floor is review discipline, not a library rule: a short
    # anchor that happens to be unique today stops being unique on the next
    # edit round, and the comment lands on the wrong paragraph.
    short = [r.match for r in requests if len(r.match.split()) < 5]
    if short:
        print(f"{len(short)} anchor(s) shorter than five words — lengthen them "
              f"before writing:", file=sys.stderr)
        for match in short:
            print(f"  - {match!r}", file=sys.stderr)
        return 2

    pre = len(read_comments(source))
    words_before = docx_word_count(source)
    try:
        backup = add_comments_in_place(source, requests, backup=not args.no_backup)
    except (ValueError, VerificationError) as exc:
        print(f"no comments written — {exc}", file=sys.stderr)
        return 1

    # Counts computed from the written file, never from the request list.
    after = len(read_comments(source))
    words_after = docx_word_count(source)
    for request in requests:
        print(f"  + [{request.author}] {request.text[:70]}")
    print(f"wrote {source.name}: {after} comment(s) on the written file "
          f"({pre} pre-existing preserved, {after - pre} new); "
          f"word count {words_after} (was {words_before})")
    if backup:
        print(f"backup: {backup.name}")
    return 0


def cmd_track(args: argparse.Namespace) -> int:
    from docx import Document

    source = Path(args.document)
    out = Path(args.out) if args.out else source.with_name(source.stem + "_TRACKED.docx")
    if out.resolve() == source.resolve():
        print("refusing to track changes in place; pass a different --out", file=sys.stderr)
        return 2

    document = Document(str(source))
    editor = TrackedEditor(document, author=args.author)
    counts = {old: editor.replace(old, new) for old, new in _load_edits(args.edits)}
    document.save(str(out))

    # A zero means the search string was wrong. Saying so here, loudly, is the
    # difference between a review round that lands and one that silently does not.
    missed = [old for old, made in counts.items() if made == 0]
    for old, made in counts.items():
        print(f"  {made:>3}  {old[:70]}")
    print(f"wrote {out}: {len(read_revisions(out))} revisions by {args.author}")
    if missed:
        print(f"\n{len(missed)} search string(s) matched NOTHING — check them before "
              f"sending:", file=sys.stderr)
        for old in missed:
            print(f"  - {old!r}", file=sys.stderr)
        return 1
    return 0


def cmd_revisions(args: argparse.Namespace) -> int:
    revisions = read_revisions(args.document)
    for revision in revisions:
        mark = "+" if revision.kind == "insertion" else "-"
        print(f"{mark} [{revision.author}, {revision.date}] {revision.text}")
    print(f"\n{len(revisions)} revisions in {Path(args.document).name}")
    return 0


def cmd_revise(args: argparse.Namespace) -> int:
    from ane_package.officeops import wordcom

    if not wordcom.word_available():
        print("Word COM is not available here — revise mode needs Windows with Word "
              "installed and the file closed in Word.", file=sys.stderr)
        return 2

    pairs = dict(_load_edits(args.edits))
    counts = wordcom.find_replace(
        args.document, pairs,
        include_headers=args.headers,
        backup=not args.no_backup,
    )
    for old, made in counts.items():
        print(f"  {made:>3}  {old[:70]}")
    missed = [old for old, made in counts.items() if made == 0]
    if missed:
        print(f"\n{len(missed)} search string(s) matched NOTHING. Word reports these "
              f"counts, so this is a wrong search string, not a no-op:", file=sys.stderr)
        for old in missed:
            print(f"  - {old!r}", file=sys.stderr)
        return 1
    print("\nPDF: export by hand from Word (File > Save As > PDF). "
          "ExportAsFixedFormat hangs on these documents.")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    document = Path(args.document)
    checks = Checks(title=f"office-review-pass: {document.name}")
    if args.expect_branded:
        checks.expect("branding intact (header, footer, logo)", assert_branded, document)
    else:
        checks.expect("header and footer parts present",
                      assert_header_footer_present, document)
    stranded = stranded_hyperlinks(document)
    checks.check(not stranded, f"no stranded hyperlink relationships ({stranded})")
    words = docx_word_count(document)
    checks.check(words > 0, f"word count computed from the written file ({words})")
    return checks.report()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subs = parser.add_subparsers(dest="command", required=True)

    read = subs.add_parser("read", help="render the body with comments at their anchors")
    read.add_argument("document")
    read.add_argument("--out", help="write to a file instead of stdout")
    read.add_argument("--no-resolved", action="store_true",
                      help="drop comments Word marks done")
    read.set_defaults(func=cmd_read)

    annotate = subs.add_parser(
        "annotate", help="insert review findings as margin comments into the working copy")
    annotate.add_argument("document")
    annotate.add_argument("--comments", required=True)
    annotate.add_argument("--author", default="Ane Gasser",
                          help="author shown on comments without their own")
    annotate.add_argument("--no-backup", action="store_true")
    annotate.set_defaults(func=cmd_annotate)

    track = subs.add_parser("track", help="apply edits as real Word tracked changes")
    track.add_argument("document")
    track.add_argument("--edits", required=True)
    track.add_argument("--author", default="Ane Gasser")
    track.add_argument("--out")
    track.set_defaults(func=cmd_track)

    revisions = subs.add_parser("revisions", help="list the tracked changes in a document")
    revisions.add_argument("document")
    revisions.set_defaults(func=cmd_revisions)

    revise = subs.add_parser("revise", help="formatting-preserving find and replace via Word")
    revise.add_argument("document")
    revise.add_argument("--edits", required=True)
    revise.add_argument("--headers", action="store_true",
                        help="also replace inside headers and footers")
    revise.add_argument("--no-backup", action="store_true")
    revise.set_defaults(func=cmd_revise)

    verify = subs.add_parser("verify", help="assert on the written file")
    verify.add_argument("document")
    verify.add_argument("--expect-branded", action="store_true",
                        help="also require the logo (IPPF-branded deliverables)")
    verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
