"""Review an image-based deck export: pull the slides, comment them, list the fixes.

Thin by design. Three functions open the document, and each is one call into
``ane_package.officeops``: ``collect`` extracts, ``write_comments`` anchors, and
``write_sheet`` emits the worklist. Everything else here is pure logic over
objects the module already returned — slide numbering, chrome detection, anchor
collision checks, comment merging — which is why it is testable without a
``.docx``. A capability that has to open a file belongs in officeops.

Why the mode exists: on 2026-06-26 twelve Articulate Storyline ``.docx`` exports
of the RBM Toolbox arrived for French review, and every translatable string was
rasterised inside a slide image. The body held only slide titles, so an ordinary
text review read a clean document and found nothing. The whole workflow was
improvised by hand. Three things about it are easy to get wrong, and this script
exists to get them right by construction.

    1. A Word comment cannot sit on text inside an image. It has to hang from
       that slide's title paragraph instead, and ``officeops.add_comments``
       matches paragraphs by text, so a repeated title silently breaks the
       anchor. Collisions are reported before anything is written, not after.
    2. Slide numbering comes from the document's own labels, which are in the
       language under review. "Diapositive 7" is slide 7. A parser that reads
       only "Slide" numbers every French deck from scratch and keys the whole
       corrections sheet wrong.
    3. Navigation chrome repeats on every slide and is not worth a reviewer's
       attention. It is marked and set aside, never silently dropped.

Usage:
    python extract_deck.py extract DOC --out-dir DIR [--en-offset N] [--json]
    python extract_deck.py comment DOC --findings FILE [--out FILE]
    python extract_deck.py sheet   DOC --findings FILE --out FILE [--title T]

DOC is the exported .docx. FINDINGS is the JSON written after reading the slide
images; see ``references/deck-export-mode.md`` for its shape.
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
    """Print the deck's own words without dying on the console encoding.

    A Windows console is cp1252 by default and this script prints French,
    Romanian and Russian slide titles. Left alone it raises UnicodeEncodeError
    on the first accented word. Wave 3 shipped exactly that bug past 32 passing
    unit tests, because an in-process call never touches the console encoding.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


_speak_utf8()

from ane_package.officeops import (  # noqa: E402
    CommentRequest,
    add_comments,
    looks_like_deck_export,
    slide_images,
)

# Every language localise supports, because the deck under review is by
# definition not in English. An English-only parser reads "Diapositive 7" as an
# unnumbered slide and keys the corrections sheet off the image ordinal instead,
# which drifts the moment one slide carries two images.
SLIDE_WORDS = (
    "slide", "diapositive", "diapositiva", "diapozitiv", "diapozitivul",
    "folie", "слайд",
)
LAYER_WORDS = ("layer", "calque", "capa", "strat", "nivel", "слой")

_SLIDE_NUMBER = re.compile(
    r"^\s*(?:" + "|".join(SLIDE_WORDS) + r")\s*[-–—:.]?\s*(\d{1,3})\b",
    re.IGNORECASE,
)
_LABEL_ONLY = re.compile(
    r"^\s*(?:" + "|".join(SLIDE_WORDS + LAYER_WORDS) + r")\s*[-–—:.]?\s*\d{0,3}\s*$",
    re.IGNORECASE,
)

# A digest on this many slides or more is furniture: a logo, a navigation bar,
# a progress track. Two slides sharing an image is a coincidence worth reading.
CHROME_REPEATS = 3

# Findings of these types describe something the reviewer could not resolve.
# They belong on the worklist, where they can be chased, and not in a comment
# balloon, where they read as a correction the translator can action.
SHEET_ONLY_TYPES = {"data gap", "query", "question"}

SHEET_COLUMNS = ["Slide", "EN page", "Type", "EN source", "Current", "Proposed",
                 "Why", "Severity"]


# --------------------------------------------------------------------------
# Pure logic — no file is opened below this line
# --------------------------------------------------------------------------

def slide_number(anchor: str) -> int | None:
    """The slide number the document itself claims, in any supported language."""
    match = _SLIDE_NUMBER.search(anchor or "")
    return int(match.group(1)) if match else None


def is_label_only(anchor: str) -> bool:
    """True when a paragraph is a bare slide or layer label, carrying no content."""
    return bool(_LABEL_ONLY.match(anchor or ""))


def find_chrome(images: list) -> set[str]:
    """Digests that repeat across enough slides to be navigation furniture."""
    counts: dict[str, int] = {}
    for image in images:
        counts[image.digest] = counts.get(image.digest, 0) + 1
    return {digest for digest, count in counts.items() if count >= CHROME_REPEATS}


def anchor_collisions(images: list) -> list[str]:
    """Anchor texts shared by more than one image.

    ``add_comments`` requires a match string that hits exactly one paragraph and
    raises otherwise. Reporting collisions up front turns a mid-write failure
    into a decision: re-key those findings to the sheet, or edit the deck.
    """
    counts: dict[str, int] = {}
    for image in images:
        anchor = (image.anchor or "").strip()
        if anchor:
            counts[anchor] = counts.get(anchor, 0) + 1
    return sorted(anchor for anchor, count in counts.items() if count > 1)


def assemble(images: list, check, en_offset: int | None = None) -> dict:
    """Turn officeops records into the reviewable slide manifest."""
    chrome = find_chrome(images)
    collisions = set(anchor_collisions(images))

    slides = []
    for image in images:
        anchor = (image.anchor or "").strip()
        number = slide_number(anchor)
        key = number if number is not None else image.index
        slides.append({
            "index": image.index,
            "slide": key,
            "numbered_by_document": number is not None,
            "anchor": anchor,
            "anchor_usable": bool(anchor) and anchor not in collisions,
            "label_only": is_label_only(anchor),
            "image": str(image.path) if image.path else None,
            "format": image.image_format,
            "size_kb": round(image.size / 1024, 1),
            "digest": image.digest[:12],
            "is_chrome": image.digest in chrome,
            "en_page": (key + en_offset) if en_offset is not None else None,
        })

    content = [slide for slide in slides if not slide["is_chrome"]]
    return {
        "is_deck_export": check.is_deck_export,
        "reason": check.reason,
        "main_part": check.main_part,
        "image_count": len(slides),
        "slide_count": len(content),
        "chrome_count": len(slides) - len(content),
        "anchor_collisions": sorted(collisions),
        "unnumbered": [s["index"] for s in content if not s["numbered_by_document"]],
        "slides": slides,
    }


def merge_findings(findings: list[dict]) -> dict[int, list[dict]]:
    """Group findings by slide, so one slide gets one balloon, not five.

    Word stacks separate comments on the same paragraph into an unreadable pile,
    and the anchor paragraph is shared by every finding on that slide.
    """
    grouped: dict[int, list[dict]] = {}
    for finding in findings:
        try:
            key = int(finding.get("slide"))
        except (TypeError, ValueError):
            continue
        grouped.setdefault(key, []).append(finding)
    return grouped


def comment_text(findings: list[dict]) -> str:
    """One balloon for one slide. English throughout, target language quoted.

    The rendering under review is quoted in guillemets so the translator can see
    exactly what changes; everything around it is English, because the comment
    is addressed to the reviewer, not to the deck.
    """
    lines = []
    for finding in findings:
        kind = str(finding.get("type") or "Correction").strip()
        why = str(finding.get("why") or "").strip()
        current = str(finding.get("current") or "").strip()
        proposed = str(finding.get("proposed") or "").strip()
        piece = f"{kind}."
        if current and proposed:
            piece += f" « {current} » → « {proposed} »"
        elif proposed:
            piece += f" Proposed: « {proposed} »"
        if why:
            piece += f" {why}" if piece.endswith(("»", ".")) else f". {why}"
        lines.append(piece.strip())
    return "\n".join(lines)


def build_requests(findings: list[dict], manifest: dict,
                   author: str = "Ane Gasser (localise review)") -> tuple[list, list[str]]:
    """Pair findings to anchor paragraphs. Returns (requests, skipped reasons).

    A finding is skipped rather than guessed at when its slide is not in the
    deck, when the anchor repeats, or when it is a query rather than a
    correction. Every skip is reported so it can still reach the worklist.
    """
    by_slide = {slide["slide"]: slide for slide in manifest["slides"]
                if not slide["is_chrome"]}
    requests, skipped = [], []

    for key, group in sorted(merge_findings(findings).items()):
        actionable = [
            finding for finding in group
            if str(finding.get("type") or "").strip().lower() not in SHEET_ONLY_TYPES
        ]
        queries = len(group) - len(actionable)
        if queries:
            skipped.append(f"slide {key}: {queries} query/data-gap finding(s) → worklist only")
        if not actionable:
            continue

        slide = by_slide.get(key)
        if slide is None:
            skipped.append(f"slide {key}: not in the deck ({len(actionable)} finding(s)) → worklist only")
            continue
        if not slide["anchor_usable"]:
            reason = "anchor repeats on another slide" if slide["anchor"] else "no anchor paragraph"
            skipped.append(f"slide {key}: {reason} ({len(actionable)} finding(s)) → worklist only")
            continue

        requests.append(CommentRequest(
            match=slide["anchor"], text=comment_text(actionable), author=author,
        ))
    return requests, skipped


def worklist_rows(findings: list[dict], manifest: dict) -> list[dict]:
    """Every finding as a worklist row, in slide order. Nothing is dropped here.

    The sheet is the complete record: comments carry what a translator can act
    on in the deck, and the sheet carries that plus the queries the comments
    deliberately leave out.
    """
    by_slide = {slide["slide"]: slide for slide in manifest["slides"]}
    rows = []
    for key, group in sorted(merge_findings(findings).items()):
        slide = by_slide.get(key)
        for finding in group:
            en_page = finding.get("en_page")
            if en_page is None and slide is not None:
                en_page = slide.get("en_page")
            rows.append({
                "Slide": str(key),
                "EN page": "" if en_page is None else str(en_page),
                "Type": str(finding.get("type") or "Correction"),
                "EN source": str(finding.get("en_source") or ""),
                "Current": str(finding.get("current") or ""),
                "Proposed": str(finding.get("proposed") or ""),
                "Why": str(finding.get("why") or ""),
                "Severity": str(finding.get("severity") or "Medium"),
            })
    return rows


def render(manifest: dict) -> str:
    """Markdown for the reviewer: what to read, in what order, with what caveats."""
    lines = [
        "# Deck export — slides to review",
        "",
        f"- **Deck export:** {'yes' if manifest['is_deck_export'] else 'NO'} — {manifest['reason']}",
        f"- **Main part:** `{manifest['main_part']}`",
        f"- **Images:** {manifest['image_count']} "
        f"({manifest['slide_count']} to review, {manifest['chrome_count']} navigation chrome)",
        "",
    ]

    if not manifest["is_deck_export"]:
        lines += [
            "> This document does not look like an image-based export. Its text is "
            "live, so review it as an ordinary draft (mode 3) rather than reading "
            "the images.",
            "",
        ]

    if manifest["anchor_collisions"]:
        lines += [
            "## ⚠️ Anchors that cannot carry a comment",
            "",
            "These titles appear on more than one slide, so a comment matched to "
            "them would land on the wrong paragraph. Findings on these slides go "
            "to the corrections sheet only.",
            "",
        ]
        lines += [f"- \"{anchor}\"" for anchor in manifest["anchor_collisions"]]
        lines.append("")

    if manifest["unnumbered"]:
        listed = ", ".join(str(index) for index in manifest["unnumbered"])
        lines += [
            f"⚠️ Slides keyed by image order, not by a label in the document: {listed}. "
            "Check the numbering against the deck before keying the sheet.",
            "",
        ]

    lines += ["## Read these", "", "| Slide | Anchor | EN page | Image | Size |",
              "|---|---|---|---|---|"]
    for slide in manifest["slides"]:
        if slide["is_chrome"]:
            continue
        anchor = slide["anchor"] or "_(none)_"
        if not slide["anchor_usable"]:
            anchor += " ⚠️"
        image = Path(slide["image"]).name if slide["image"] else "_(not written)_"
        page = slide["en_page"] if slide["en_page"] is not None else ""
        lines.append(f"| {slide['slide']} | {anchor} | {page} | `{image}` | {slide['size_kb']} KB |")
    lines.append("")

    chrome = [slide for slide in manifest["slides"] if slide["is_chrome"]]
    if chrome:
        indices = ", ".join(str(slide["index"]) for slide in chrome)
        lines += [
            f"## Set aside as navigation chrome ({len(chrome)})",
            "",
            f"Repeated on {CHROME_REPEATS} or more slides: images {indices}. "
            "Read one of them once to confirm it holds no translatable text.",
            "",
        ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# The three functions that open the document
# --------------------------------------------------------------------------

def collect(path: Path, out_dir: Path | None = None,
            en_offset: int | None = None) -> dict:
    """Read the deck. Without ``out_dir`` no image is written, which is what the
    comment and sheet steps want: they need the anchors, not the pictures."""
    check = looks_like_deck_export(path)
    images = slide_images(path, out_dir=out_dir)
    return assemble(images, check, en_offset=en_offset)


def write_comments(path: Path, findings: list[dict], out_path: Path | None,
                   manifest: dict) -> tuple[Path, list[str]]:
    requests, skipped = build_requests(findings, manifest)
    if not requests:
        return path, skipped
    written = add_comments(path, requests, out_path=out_path)
    return Path(written), skipped


def write_sheet(rows: list[dict], out_path: Path, title: str, date_dmy: str) -> Path:
    import pandas as pd

    from ane_package.reporting.excel_templates import build_review_worklist

    build_review_worklist(
        pd.DataFrame(rows, columns=SHEET_COLUMNS), str(out_path), title,
        "localise deck-export review", date_dmy,
        wide_cols=["EN source", "Current", "Proposed", "Why"],
    )
    return out_path


# --------------------------------------------------------------------------

def _load_findings(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("findings", [])
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a list of findings, or an object holding 'findings'")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    extract = sub.add_parser("extract", help="pull the slide images and list them")
    extract.add_argument("doc", type=Path)
    extract.add_argument("--out-dir", type=Path, required=True)
    extract.add_argument("--en-offset", type=int, default=None,
                         help="slide N maps to English page N + offset")
    extract.add_argument("--json", action="store_true")
    extract.add_argument("--out", type=Path, help="write here instead of stdout")

    comment = sub.add_parser("comment", help="write anchored comments to a copy")
    comment.add_argument("doc", type=Path)
    comment.add_argument("--findings", type=Path, required=True)
    comment.add_argument("--out", type=Path, help="the commented copy to write")

    sheet = sub.add_parser("sheet", help="emit the branded corrections worklist")
    sheet.add_argument("doc", type=Path)
    sheet.add_argument("--findings", type=Path, required=True)
    sheet.add_argument("--out", type=Path, required=True)
    sheet.add_argument("--title", default="Deck export — corrections")
    sheet.add_argument("--date", default="", help="dd/mm/yyyy for the source line")

    args = parser.parse_args(argv)

    if not args.doc.is_file():
        print(f"No such file: {args.doc}", file=sys.stderr)
        return 2
    if args.doc.suffix.lower() != ".docx":
        print(f"Expected a .docx, got {args.doc.suffix or 'no extension'}", file=sys.stderr)
        return 2

    if args.command == "extract":
        manifest = collect(args.doc, args.out_dir, en_offset=args.en_offset)
        if manifest["image_count"] == 0:
            print(
                f"{args.doc.name} holds no embedded images. If its text is live, "
                "review it as an ordinary draft (mode 3) instead.",
                file=sys.stderr,
            )
            return 1
        payload = (json.dumps(manifest, indent=2, ensure_ascii=False)
                   if args.json else render(manifest))
        if args.out:
            args.out.write_text(payload + "\n", encoding="utf-8")
            print(f"Wrote {args.out} — {manifest['slide_count']} slides to review, "
                  f"{manifest['chrome_count']} chrome")
        else:
            print(payload)
        return 0

    findings = _load_findings(args.findings)
    if not findings:
        print(f"{args.findings} holds no findings.", file=sys.stderr)
        return 1

    if args.command == "comment":
        manifest = collect(args.doc)
        written, skipped = write_comments(args.doc, findings, args.out, manifest)
        for note in skipped:
            print(f"⚠️  {note}", file=sys.stderr)
        if written == args.doc:
            print("No finding could be anchored; nothing written.", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0

    manifest = collect(args.doc)
    rows = worklist_rows(findings, manifest)
    write_sheet(rows, args.out, args.title, args.date)
    print(f"Wrote {args.out} — {len(rows)} findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
