"""Turn a commented Word document into a decision-ready extract.

Thin by design. Every Office operation below is one call into
``ane_package.officeops``; this file adds document-order grouping, heading
context, date-slip flagging and printing, and nothing else. Those four are pure
logic over objects officeops already returned — no zip, no XML, no COM — which
is why they live here rather than in the module. A capability that has to open
the file belongs in officeops, with its own test.

Why the mode exists at all: on 2026-07-24 twelve decisions sat in
``word/comments.xml`` of an implementation plan and were pulled out by hand.
Every step was improvised, and the two things that went wrong then are the two
things this script exists to prevent.

    1. A comment read without its anchor is often meaningless. "Stef to discuss
       with Manuelle" only parses against the Follow-up-funding bullet it hangs
       on. So the anchor is never optional here, and neither is the heading the
       anchor sits under.
    2. Dates spoken into a comment slip. One reading "14-15 July" meant
       September. The script cannot know which is right, so it flags every date
       for confirmation rather than quietly carrying one into a note that then
       gets sent.

Usage:
    python read_marginalia.py DOC [--out FILE] [--json] [--open-only]

DOC is a .docx. Output is markdown on stdout unless ``--out`` is given.
``--json`` emits the same content as a machine-readable object instead.
``--open-only`` drops comments Word marks resolved.
"""

from __future__ import annotations

import argparse
import json
import os
import re
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


def _speak_utf8() -> None:
    """Print the document's own words without dying on the console encoding.

    A Windows console is cp1252 by default and this script prints text people
    wrote: Chișinău, curly quotes, French names. Left alone it raises
    UnicodeEncodeError on the first accented word. Wave 3 shipped exactly that
    bug past 32 passing unit tests, because an in-process call never touches the
    console encoding.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


_speak_utf8()

from ane_package.officeops import review_blocks  # noqa: E402

ENGLISH_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# English, French, Spanish and Romanian, because Ane reviews in all four and a
# date guard that only reads English fails silently on exactly the documents
# where a second language makes a slip more likely, not less. Every pattern
# below requires a number beside the month, so the Romanian adverb "mai" ("more")
# does not match while "14 mai" does.
MONTHS = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
    # French
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5,
    "juin": 6, "juillet": 7, "août": 8, "aout": 8, "septembre": 9,
    "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12,
    # Spanish
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
    # Romanian
    "ianuarie": 1, "februarie": 2, "martie": 3, "aprilie": 4, "iunie": 6,
    "iulie": 7, "septembrie": 9, "octombrie": 10, "noiembrie": 11, "decembrie": 12,
}
_MONTH_WORDS = "|".join(sorted(MONTHS, key=len, reverse=True))

# Ordered widest-first so "14-15 July" is captured whole rather than as "14"
# plus a stray month. Each pattern names the group that carries the month, when
# it has one, because the backdating check needs it and nothing else does.
DATE_PATTERNS = [
    (re.compile(rf"\b\d{{1,2}}\s*[-–—/]\s*\d{{1,2}}\s+({_MONTH_WORDS})\b", re.I), 1),
    (re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+({_MONTH_WORDS})\b", re.I), 1),
    (re.compile(rf"\b({_MONTH_WORDS})\s+\d{{1,2}}(?:st|nd|rd|th)?\b", re.I), 1),
    (re.compile(rf"\b(?:end|start|beginning|mid|middle)[\s-]+(?:of\s+)?({_MONTH_WORDS})\b", re.I), 1),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), None),
    (re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b"), None),
    (re.compile(rf"\b({_MONTH_WORDS})\s+\d{{4}}\b", re.I), 1),
    (re.compile(r"\bQ[1-4]\b"), None),
]


def date_mentions(text: str, comment_date: str) -> list[dict]:
    """Every date-shaped phrase in a comment, with a reason to look twice.

    Two levels of suspicion. Any date at all is worth confirming, because a
    comment is dictated fast and nobody proofreads a margin balloon. But a date
    naming a month EARLIER than the comment itself is the specific 2026-07-24
    shape: a forward-looking action ("book the workshop for 14-15 July")
    written in late July, where the speaker meant the next occurrence and said
    the wrong month. That one gets called out by name.

    Deliberately not resolved into a real date. Guessing the year on "14-15
    July" is how the wrong date reaches a note that then gets sent; the job here
    is to make Ane look, not to decide for her.
    """
    comment_month = _month_of(comment_date)
    found: list[dict] = []
    claimed: list[tuple[int, int]] = []

    for pattern, month_group in DATE_PATTERNS:
        for match in pattern.finditer(text):
            span = match.span()
            if any(span[0] < end and start < span[1] for start, end in claimed):
                continue  # already inside a wider match
            claimed.append(span)
            named = None
            if month_group is not None:
                named = MONTHS.get(match.group(month_group).lower())
            backdated = bool(
                named and comment_month and named < comment_month
            )
            found.append({
                "phrase": match.group(0),
                "backdated": backdated,
                "note": (
                    f"names {_month_name(named)}, earlier than the comment itself "
                    f"({_month_name(comment_month)}) — the 2026-07-24 slip had this shape"
                    if backdated else "confirm before it goes into the note"
                ),
            })
    return sorted(found, key=lambda item: not item["backdated"])


def _month_of(stamp: str) -> int | None:
    match = re.match(r"(\d{4})-(\d{2})", stamp or "")
    return int(match.group(2)) if match else None


def _month_name(number: int | None) -> str:
    """Always name the month in English, whatever language it was written in.

    The flag is read by whoever is building the note, not by the commenter, and
    a mixed-language warning line is harder to scan than a consistent one.
    """
    if not number or not 1 <= number <= 12:
        return "an unknown month"
    return ENGLISH_MONTHS[number - 1]


def _heading_level(style: str) -> int:
    match = re.search(r"(\d+)$", style or "")
    if match:
        return int(match.group(1))
    return 0 if (style or "").lower() == "title" else 1


def collect(path: Path, open_only: bool = False) -> dict:
    """Comments in document order, each carrying where in the document it sits.

    ``read_comments`` alone returns them in comments.xml order, which is roughly
    the order they were written, not the order they will be discussed.
    ``review_blocks`` gives document order and the heading structure around it,
    and a note built section by section is the one a reader can check against
    the document afterwards.

    One line opens the document; everything after it is ``assemble``, which is
    pure logic over objects and therefore testable without a .docx.
    """
    return assemble(review_blocks(path), path, open_only=open_only)


def assemble(blocks, path, open_only: bool = False) -> dict:
    """Group blocks into threads under their headings. No file access."""
    heading_stack: list[tuple[int, str]] = []
    items: list[dict] = []
    replies: dict[str, list[dict]] = {}
    tracked_blocks = 0

    for block in blocks:
        if block.has_insertions or block.has_deletions:
            tracked_blocks += 1
        if block.is_heading and block.text.strip():
            level = _heading_level(block.style)
            heading_stack = [entry for entry in heading_stack if entry[0] < level]
            heading_stack.append((level, block.text.strip()))

        for comment in block.comments:
            if open_only and comment.resolved:
                continue
            record = {
                "id": comment.id,
                "author": comment.author,
                "date": comment.date,
                "text": comment.text,
                "anchor": comment.anchor or block.text,
                "block": block.index,
                "section": " > ".join(name for _, name in heading_stack) or "(before any heading)",
                "in_table": block.in_table,
                "tracked_anchor": block.has_insertions or block.has_deletions,
                "resolved": comment.resolved,
                "is_reply": comment.is_reply,
                "parent_id": comment.parent_id,
                "dates": date_mentions(comment.text, comment.date),
                "replies": [],
            }
            if comment.is_reply:
                replies.setdefault(comment.parent_id or "", []).append(record)
            else:
                items.append(record)

    known = {item["id"] for item in items}
    for parent_id, thread in replies.items():
        for item in items:
            if item["id"] == parent_id:
                item["replies"] = thread
                break
        else:
            # A reply whose parent was filtered out or never existed still
            # carries a decision. Losing it silently is the failure mode.
            items.extend(entry for entry in thread if entry["id"] not in known)

    items.sort(key=lambda item: item["block"])
    return {
        "document": str(path),
        "comment_count": len(items) + sum(len(item["replies"]) for item in items),
        "thread_count": len(items),
        "authors": sorted({item["author"] for item in items if item["author"]}),
        "tracked_blocks": tracked_blocks,
        "comments": items,
    }


def render(data: dict) -> str:
    """Markdown grouped by section, because that is how the note gets built.

    Every heading below is a place a decision could hide. The counts are printed
    so a reader can tell at a glance whether the extract lost anything: twelve
    comments in Word and eleven here is a bug, and it should be visible without
    opening the document.
    """
    lines: list[str] = []
    name = Path(data["document"]).name
    lines.append(f"# Marginalia — {name}")
    lines.append("")
    authors = ", ".join(data["authors"]) or "no named author"
    lines.append(
        f"{data['comment_count']} comments in {data['thread_count']} threads, by {authors}."
    )
    if data["tracked_blocks"]:
        lines.append(
            f"{data['tracked_blocks']} paragraphs also carry tracked changes. Anchor text "
            "below shows those changes ACCEPTED, which is not what the commenter saw. "
            "Marked ±tracked where it applies."
        )
    lines.append("")
    lines.append(
        "Check this count against Word before writing the note. Then confirm every "
        "flagged date with Ane; none of them are corrected here on purpose."
    )
    lines.append("")

    current_section = None
    for item in data["comments"]:
        if item["section"] != current_section:
            current_section = item["section"]
            lines.append(f"## {current_section}")
            lines.append("")

        state = []
        if item["resolved"]:
            state.append("resolved")
        if item["in_table"]:
            state.append("in a table")
        if item["tracked_anchor"]:
            state.append("±tracked")
        suffix = f" [{', '.join(state)}]" if state else ""
        stamp = (item["date"] or "no date")[:10]
        lines.append(f"### [{item['id']}] {item['author'] or 'unknown'} — {stamp}{suffix}")
        lines.append(f"- **Anchor** (block {item['block']}): {_quote(item['anchor'])}")
        lines.append(f"- **Comment:** {item['text'].strip() or '(empty)'}")
        for reply in item["replies"]:
            reply_stamp = (reply["date"] or "no date")[:10]
            lines.append(
                f"  - **Reply** — {reply['author'] or 'unknown'}, {reply_stamp}: "
                f"{reply['text'].strip()}"
            )
        for mention in item["dates"] + [m for r in item["replies"] for m in r["dates"]]:
            lines.append(
                f"- ⚠️ Date to confirm: \"{mention['phrase']}\" — {mention['note']}"
            )
        lines.append("")

    flagged = [
        (item, mention)
        for item in data["comments"]
        for mention in item["dates"] + [m for r in item["replies"] for m in r["dates"]]
    ]
    if flagged:
        lines.append("## Dates to confirm before writing the note")
        lines.append("")
        lines.append("| Comment | Phrase | Why |")
        lines.append("|---|---|---|")
        for item, mention in sorted(flagged, key=lambda pair: not pair[1]["backdated"]):
            lines.append(
                f"| [{item['id']}] {item['author'] or 'unknown'} | {mention['phrase']} | "
                f"{mention['note']} |"
            )
        lines.append("")
    return "\n".join(lines)


def _quote(text: str) -> str:
    text = " ".join((text or "").split())
    if not text:
        return "_(no anchor text — Word drew the balloon with no range)_"
    if len(text) > 300:
        text = text[:300].rstrip() + " …"
    return f'"{text}"'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("doc", type=Path, help="the reviewed .docx")
    parser.add_argument("--out", type=Path, help="write here instead of stdout")
    parser.add_argument("--json", action="store_true", help="emit JSON, not markdown")
    parser.add_argument(
        "--open-only", action="store_true", help="drop comments Word marks resolved"
    )
    args = parser.parse_args(argv)

    if not args.doc.is_file():
        print(f"No such file: {args.doc}", file=sys.stderr)
        return 2
    if args.doc.suffix.lower() != ".docx":
        print(f"Expected a .docx, got {args.doc.suffix or 'no extension'}", file=sys.stderr)
        return 2

    data = collect(args.doc, open_only=args.open_only)
    if not data["comments"]:
        print(
            f"{args.doc.name} carries no comments. Wrong document, or the decisions "
            "were left as tracked changes rather than margin comments — try "
            "office-review-pass read.",
            file=sys.stderr,
        )
        return 1

    payload = json.dumps(data, indent=2, ensure_ascii=False) if args.json else render(data)
    if args.out:
        args.out.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote {args.out} — {data['comment_count']} comments, {data['thread_count']} threads")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
