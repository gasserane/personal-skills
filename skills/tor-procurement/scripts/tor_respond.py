#!/usr/bin/env python3
"""Answer a reviewer who has objected to a ToR, without changing the ToR.

Two subcommands:

``extract``
    Open the commented ToR and report the objections: who raised each one, what
    clause it lands on, which section that clause sits in, and whether it has
    already been answered. Writes a worksheet to fill in. Decides nothing.
``compile``
    Take the filled worksheet and produce the round: a reply at two lengths per
    objection, one response register covering the round, and a follow-on sizing
    sketch wherever the verdict defers. Runs every guard first and refuses to
    emit a round that contradicts itself.

**The file boundary.** Exactly one function here opens a document:
:func:`load_threads`. Everything downstream takes objects and opens nothing, so
the verdict logic, the guards and the register are testable without a fixture.

**Three of the four verdicts leave the ToR untouched.** ``defend`` answers the
objection from the text as written; ``defer`` accepts the point and sizes a
follow-on contract; ``escalate`` sends it out of the ToR as a governance
question. Only ``concede`` changes the document, and only a conceded objection
reaches finalise mode as a revision. A round that attaches an edit to any other
verdict is refused rather than emitted, because finalise would act on it.

**The anchor is not the clause.** A reviewer selects a phrase and writes about
the argument behind it. On the 2026-07-31 round the one open objection was
anchored on an ethics sentence in section 13 while the discussion was about
Objective 1. ``extract`` reports the anchor and the section separately so the
mismatch is visible before a reply is drafted against the wrong clause.

**Nothing is invented.** A defence cites what the ToR or a governance document
actually says, or it is refused. A sizing sketch costs days at a rate band that
was supplied, or it says it is not costed — never zero. A procurement route is
assessed against a threshold that was supplied, or it is not assessed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

WORK_FOLDER_ROOT = os.environ.get(
    "WORK_FOLDER_ROOT", r"C:\Users\AGasser\OneDrive\5 ANE CLAUDE work folder"
)
if WORK_FOLDER_ROOT not in sys.path:
    sys.path.insert(0, WORK_FOLDER_ROOT)

from ane_package.officeops import comment_threads, same_person  # noqa: E402
from ane_package.qa.prose_lint import lint_text  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):  # a console that cannot encode a name
    sys.stdout.reconfigure(errors="replace")  # must not take out the run
    sys.stderr.reconfigure(errors="replace")

VERDICTS = ("defend", "concede", "defer", "escalate")

#: Verdict pairs that cannot both be true of the same clause. Defending a clause
#: as written and conceding it needs an edit are the same sentence contradicting
#: itself; the rest compose (defend-plus-defer is the reference case).
INCOMPATIBLE = {frozenset({"defend", "concede"})}

DEFAULT_COMPACT_WORDS = 180
DEFAULT_FULL_WORDS = 500


# --------------------------------------------------------------------------
# the round
# --------------------------------------------------------------------------

@dataclass
class SizingOption:
    """One shape the follow-on contract could take.

    ``days`` is ``None`` when nobody has estimated it, which is a different fact
    from zero and has to stay different: an unestimated option costed at zero
    reads as free.
    """

    name: str
    days: float | None = None
    note: str = ""

    def band(self, rate_band: tuple[float, float] | None) -> tuple[float, float] | None:
        if self.days is None or rate_band is None:
            return None
        low, high = rate_band
        return (self.days * low, self.days * high)


@dataclass
class Sizing:
    """The follow-on contract a deferred objection points at."""

    trigger: str = ""
    profile_change: str = ""
    options: list[SizingOption] = field(default_factory=list)
    day_rate_band: tuple[float, float] | None = None
    route_threshold: float | None = None
    currency: str = "EUR"

    def route_note(self) -> str:
        """What the sizing implies about the procurement route, or that it cannot say."""
        if self.route_threshold is None:
            return ("Procurement route not assessed: no threshold was supplied. "
                    "Confirm the applicable threshold before commissioning.")
        priced = [option.band(self.day_rate_band) for option in self.options]
        tops = [band[1] for band in priced if band is not None]
        if not tops:
            return ("Procurement route not assessed: no option carries both an "
                    "estimate and a rate band.")
        currency = self.currency
        if max(tops) >= self.route_threshold:
            return (f"At least one option reaches {currency} {max(tops):,.0f}, which "
                    f"meets or passes the stated threshold of {currency} "
                    f"{self.route_threshold:,.0f}. This cannot be a direct award.")
        return (f"Every option tops out below the stated threshold of {currency} "
                f"{self.route_threshold:,.0f}.")


@dataclass
class Objection:
    """One reviewer objection and the answer to it."""

    id: str
    reviewer: str
    clause: str
    objection: str
    verdict: str
    steelman: str = ""
    verdict_secondary: str = ""
    edit: str = ""
    sources: list[str] = field(default_factory=list)
    reply_full: str = ""
    reply_compact: str = ""
    sizing: Sizing | None = None
    anchor: str = ""
    section: str = ""

    @property
    def verdicts(self) -> tuple[str, ...]:
        return tuple(v for v in (self.verdict, self.verdict_secondary) if v)

    @property
    def changes_tor(self) -> bool:
        """Derived, never stated. Only a concession moves the document."""
        return "concede" in self.verdicts

    def verdict_label(self) -> str:
        return " + ".join(self.verdicts)


@dataclass
class Round:
    """Every objection from one review round on one ToR."""

    tor: str
    objections: list[Objection] = field(default_factory=list)
    round_label: str = ""
    compact_max_words: int = DEFAULT_COMPACT_WORDS
    full_max_words: int = DEFAULT_FULL_WORDS


def word_count(text: str) -> int:
    """Words in ``text``. Computed here so no count about a reply is ever typed."""
    return len(text.split())


def _sizing_from_dict(payload: dict | None) -> Sizing | None:
    if not payload:
        return None
    band = payload.get("day_rate_band")
    if band is not None:
        if len(band) != 2:
            raise ValueError("day_rate_band takes exactly two numbers: [low, high]")
        band = (float(band[0]), float(band[1]))
        if band[0] > band[1]:
            raise ValueError("day_rate_band runs low to high")
    threshold = payload.get("route_threshold")
    return Sizing(
        trigger=payload.get("trigger", ""),
        profile_change=payload.get("profile_change", ""),
        options=[
            SizingOption(
                name=option["name"],
                days=None if option.get("days") is None else float(option["days"]),
                note=option.get("note", ""),
            )
            for option in payload.get("options", [])
        ],
        day_rate_band=band,
        route_threshold=None if threshold is None else float(threshold),
        currency=payload.get("currency", "EUR"),
    )


def round_from_dict(payload: dict) -> Round:
    """Build a round from the filled worksheet, raising on anything unreadable."""
    objections = []
    for index, item in enumerate(payload.get("objections", []), start=1):
        missing = [key for key in ("reviewer", "objection", "verdict") if not item.get(key)]
        if missing:
            raise ValueError(
                f"objection {item.get('id', index)}: missing {', '.join(missing)}")
        objections.append(
            Objection(
                id=str(item.get("id", index)),
                reviewer=item["reviewer"],
                clause=item.get("clause", ""),
                objection=item["objection"],
                verdict=item["verdict"].strip().lower(),
                steelman=item.get("steelman", ""),
                verdict_secondary=(item.get("verdict_secondary") or "").strip().lower(),
                edit=item.get("edit") or "",
                sources=list(item.get("sources", [])),
                reply_full=item.get("reply_full", ""),
                reply_compact=item.get("reply_compact", ""),
                sizing=_sizing_from_dict(item.get("sizing")),
                anchor=item.get("anchor", ""),
                section=item.get("section", ""),
            )
        )
    return Round(
        tor=payload.get("tor", ""),
        round_label=payload.get("round", ""),
        objections=objections,
        compact_max_words=int(payload.get("compact_max_words", DEFAULT_COMPACT_WORDS)),
        full_max_words=int(payload.get("full_max_words", DEFAULT_FULL_WORDS)),
    )


# --------------------------------------------------------------------------
# guards
# --------------------------------------------------------------------------

@dataclass
class Finding:
    code: str
    objection_id: str
    message: str


#: Which guard failures stop a round being emitted.
#:
#: The line sits where a mistake reaches someone other than Ane. A round that
#: contradicts itself sends finalise mode a revision list that is wrong, and an
#: unsourced defence goes to a named external reviewer as an institutional claim
#: nobody can trace — both cost more to retract than to fix here. Length and
#: voice are craft: the reply is still correct and Ane can trim it in the pane,
#: so they warn and emit.
BLOCKING = {
    "CONTRADICTORY_VERDICT",
    "UNKNOWN_VERDICT",
    "EDIT_WITHOUT_CONCESSION",
    "CONCESSION_WITHOUT_EDIT",
    "DEFER_WITHOUT_SIZING",
    "SIZING_WITHOUT_DEFER",
    "UNSOURCED_DEFENCE",
    "MISSING_REPLY",
    "SIZING_ZERO_DAYS",
}


def check_round(round_: Round) -> list[Finding]:
    """Every guard, in the order a reader would want them."""
    findings: list[Finding] = []

    def flag(code: str, objection: Objection, message: str) -> None:
        findings.append(Finding(code=code, objection_id=objection.id, message=message))

    seen: set[str] = set()
    for objection in round_.objections:
        if objection.id in seen:
            flag("DUPLICATE_ID", objection, f"objection id {objection.id} is used twice")
        seen.add(objection.id)

        for verdict in objection.verdicts:
            if verdict not in VERDICTS:
                flag("UNKNOWN_VERDICT", objection,
                     f"{verdict!r} is not one of {', '.join(VERDICTS)}")
        if objection.verdict_secondary:
            if objection.verdict_secondary == objection.verdict:
                flag("CONTRADICTORY_VERDICT", objection,
                     f"primary and secondary verdict are both {objection.verdict!r}")
            elif frozenset(objection.verdicts) in INCOMPATIBLE:
                flag("CONTRADICTORY_VERDICT", objection,
                     f"{objection.verdict_label()} cannot both be true of one clause")

        if objection.edit and "concede" not in objection.verdicts:
            flag("EDIT_WITHOUT_CONCESSION", objection,
                 f"an edit is attached but the verdict is {objection.verdict_label()}; "
                 "finalise would apply a change this round did not agree")
        if "concede" in objection.verdicts and not objection.edit.strip():
            flag("CONCESSION_WITHOUT_EDIT", objection,
                 "conceded, but no minimal edit is named — a concession that names "
                 "no edit cannot reach finalise")

        if "defer" in objection.verdicts and objection.sizing is None:
            flag("DEFER_WITHOUT_SIZING", objection,
                 "deferred to a follow-on contract that is never sized; the reply "
                 "answers a legitimate point with a prohibition rather than a plan")
        if objection.sizing is not None and "defer" not in objection.verdicts:
            flag("SIZING_WITHOUT_DEFER", objection,
                 f"a follow-on is sized but the verdict is {objection.verdict_label()}")
        if objection.sizing is not None:
            for option in objection.sizing.options:
                if option.days is not None and option.days <= 0:
                    flag("SIZING_ZERO_DAYS", objection,
                         f"option {option.name!r} is estimated at {option.days} days; "
                         "leave days out entirely when nobody has estimated it")

        if "defend" in objection.verdicts and not [s for s in objection.sources if s.strip()]:
            flag("UNSOURCED_DEFENCE", objection,
                 "the clause is defended but no source is cited; a defence rests on "
                 "what the ToR or a governance document says, never on recall")

        for label, text in (("full", objection.reply_full),
                            ("compact", objection.reply_compact)):
            if not text.strip():
                flag("MISSING_REPLY", objection, f"the {label} reply is empty")

        compact = word_count(objection.reply_compact)
        if compact > round_.compact_max_words:
            flag("COMPACT_TOO_LONG", objection,
                 f"the compact reply runs {compact} words against a ceiling of "
                 f"{round_.compact_max_words}; it has to be readable in the comment pane")
        full = word_count(objection.reply_full)
        if full > round_.full_max_words:
            flag("FULL_TOO_LONG", objection,
                 f"the full reply runs {full} words against a ceiling of "
                 f"{round_.full_max_words}")

        if not objection.steelman.strip():
            flag("NO_STEELMAN", objection,
                 "the strongest version of the objection is not stated; answering the "
                 "weakest reading of a reviewer is how a round goes to four")

        for label, text in (("full", objection.reply_full),
                            ("compact", objection.reply_compact)):
            for issue in lint_text(text):
                flag("VOICE", objection, f"{label} reply: {issue.message}")

    return findings


def blocking(findings: list[Finding]) -> list[Finding]:
    return [finding for finding in findings if finding.code in BLOCKING]


def format_findings(findings: list[Finding]) -> str:
    if not findings:
        return "No findings."
    lines = []
    for finding in findings:
        mark = "BLOCK" if finding.code in BLOCKING else " warn"
        lines.append(f"  {mark}  [{finding.objection_id}] {finding.code}: {finding.message}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# outputs
# --------------------------------------------------------------------------

def _escape_cell(text: str) -> str:
    return text.replace("|", r"\|").replace("\n", " ").strip()


def register_markdown(round_: Round) -> str:
    """The response register: one row per objection, whatever the verdict.

    This is the audit trail a losing bidder's challenge asks for — every point
    raised, what was decided, and whether the published document moved. Its
    conceded rows are finalise mode's revision list.
    """
    lines = [f"# Response register — {round_.tor or 'ToR'}"]
    if round_.round_label:
        lines.append("")
        lines.append(round_.round_label)
    lines.append("")
    changed = [o for o in round_.objections if o.changes_tor]
    lines.append(
        f"**{len(round_.objections)} objections answered. "
        f"{len(changed)} change the ToR; {len(round_.objections) - len(changed)} do not.**"
    )
    lines.append("")
    lines.append("| # | Reviewer | Clause | Verdict | ToR changes | Minimal edit |")
    lines.append("|---|---|---|---|---|---|")
    for objection in round_.objections:
        lines.append(
            f"| {_escape_cell(objection.id)} "
            f"| {_escape_cell(objection.reviewer)} "
            f"| {_escape_cell(objection.clause)} "
            f"| {_escape_cell(objection.verdict_label())} "
            f"| {'yes' if objection.changes_tor else 'no'} "
            f"| {_escape_cell(objection.edit) or '-'} |"
        )
    if changed:
        lines.append("")
        lines.append("## Revision list for finalise mode")
        lines.append("")
        for objection in changed:
            lines.append(f"1. **{objection.clause or objection.id}** — {objection.edit}")
    return "\n".join(lines) + "\n"


def sizing_markdown(objection: Objection) -> str:
    """The follow-on contract a deferred objection points at."""
    sizing = objection.sizing
    if sizing is None:
        return ""
    lines = [f"### Follow-on contract — {objection.clause or objection.id}", ""]
    if sizing.trigger:
        lines += [f"**What would justify commissioning it.** {sizing.trigger}", ""]
    lines.append("| Option | Days | Indicative cost | Note |")
    lines.append("|---|---|---|---|")
    for option in sizing.options:
        band = option.band(sizing.day_rate_band)
        if band is None:
            cost = "not costed"
            days = "not estimated" if option.days is None else f"{option.days:g}"
        else:
            cost = f"{sizing.currency} {band[0]:,.0f} to {band[1]:,.0f}"
            days = f"{option.days:g}"
        lines.append(f"| {_escape_cell(option.name)} | {days} | {cost} "
                     f"| {_escape_cell(option.note)} |")
    lines.append("")
    if sizing.day_rate_band:
        lines.append(
            f"Costed at {sizing.currency} {sizing.day_rate_band[0]:,.0f} to "
            f"{sizing.day_rate_band[1]:,.0f} per day. **Indicative only: this is "
            "uncosted work, not a budget.**")
    else:
        lines.append("**No day rate band was supplied, so no option is costed.**")
    lines.append("")
    if sizing.profile_change:
        lines += [f"**How the consultant profile differs.** {sizing.profile_change}", ""]
    lines.append(sizing.route_note())
    return "\n".join(lines) + "\n"


def replies_markdown(round_: Round) -> str:
    """Every reply at both lengths, paste-ready into the comment pane."""
    lines = [f"# Replies — {round_.tor or 'ToR'}"]
    if round_.round_label:
        lines += ["", round_.round_label]
    for objection in round_.objections:
        lines += ["", f"## {objection.id}. {objection.clause or 'objection'} "
                      f"— {objection.verdict_label()}", ""]
        lines.append(f"**{objection.reviewer} raised.** {objection.objection}")
        if objection.section or objection.anchor:
            lines += ["", f"*Anchored on:* {objection.anchor or 'not recorded'}  "]
            lines.append(f"*Section:* {objection.section or 'not resolved'}")
        if objection.steelman:
            lines += ["", f"**The strongest version of the point.** {objection.steelman}"]
        lines += ["", f"**Verdict: {objection.verdict_label()}.** "
                      f"The ToR {'changes' if objection.changes_tor else 'does not change'}."]
        if objection.edit:
            lines.append("")
            lines.append(f"**Minimal edit.** {objection.edit}")
        if objection.sources:
            lines += ["", "**Answered from:** " + "; ".join(objection.sources)]
        lines += ["", f"### Full reply ({word_count(objection.reply_full)} words)", ""]
        lines.append(objection.reply_full)
        lines += ["", f"### Compact reply ({word_count(objection.reply_compact)} words)", ""]
        lines.append(objection.reply_compact)
        if objection.sizing is not None:
            lines += ["", sizing_markdown(objection)]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# reading the document — the only place a file is opened
# --------------------------------------------------------------------------

def load_threads(path: Path, include_resolved: bool = False) -> list:
    """Open the commented ToR. The single file boundary in this module."""
    return comment_threads(path, include_resolved=include_resolved)


def worksheet(threads: list, me: str, tor: str = "") -> dict:
    """Turn threads into the worksheet to fill in, deciding nothing.

    Two facts the caller cannot see from a comment list alone are computed here.
    ``answered`` is true when ``me`` has already replied in the thread, so a
    round does not answer the same point twice. ``also_on_this_clause`` names
    anyone who commented on the same paragraph in a separate thread, because
    Word only records a reply as a reply when the reviewer used the reply
    button: on the AI-for-Research ToR the author's own answer to the fenced-off
    objection sits on the same paragraph as a root comment of its own, and
    reading threading alone reports that objection as unanswered.
    """
    by_block: dict[int, list] = {}
    for thread in threads:
        by_block.setdefault(thread.block_index, []).append(thread)

    objections = []
    own_notes = []
    for thread in threads:
        if same_person(thread.root.author, me):
            # Her own margin note to herself, not an objection from anyone. It
            # reads as open because she has not replied to it, and she never
            # will. Counted and listed rather than dropped, because a working
            # note ("this section needs rewriting") often matters more than the
            # objection beside it — it is simply not this mode's job.
            own_notes.append({"id": f"c{thread.root.id}",
                              "clause": thread.section,
                              "note": thread.root.text})
            continue
        if not thread.is_open(me):
            continue
        neighbours = sorted({
            other.root.author
            for other in by_block.get(thread.block_index, [])
            if other is not thread
        })
        objections.append({
            "id": f"c{thread.root.id}",
            "reviewer": thread.root.author,
            "clause": thread.section,
            "section": thread.section,
            "anchor": thread.anchor,
            "objection": thread.root.text,
            "block": thread.block_index,
            "replies": [{"author": reply.author, "text": reply.text}
                        for reply in thread.replies],
            "also_on_this_clause": neighbours,
            "steelman": "",
            "verdict": "",
            "verdict_secondary": "",
            "edit": "",
            "sources": [],
            "reply_full": "",
            "reply_compact": "",
        })
    return {
        "tor": tor,
        "round": "",
        "compact_max_words": DEFAULT_COMPACT_WORDS,
        "full_max_words": DEFAULT_FULL_WORDS,
        "_read": {
            "threads": len(threads),
            "open": len(objections),
            "answered": len(threads) - len(objections) - len(own_notes),
            "own_notes": len(own_notes),
            "answered_as": me,
        },
        "_own_notes": own_notes,
        "objections": objections,
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _cmd_extract(args: argparse.Namespace) -> int:
    path = Path(args.docx)
    if not path.exists():
        print(f"not found: {path}", file=sys.stderr)
        return 2
    threads = load_threads(path, include_resolved=args.include_resolved)
    sheet = worksheet(threads, me=args.me, tor=path.name)
    read = sheet["_read"]
    print(f"{path.name}: {read['threads']} threads, {read['open']} to answer, "
          f"{read['answered']} already answered by {read['answered_as']}, "
          f"{read['own_notes']} own notes")
    for objection in sheet["objections"]:
        note = ""
        if objection["also_on_this_clause"]:
            note = ("  <- also commented here: "
                    + ", ".join(objection["also_on_this_clause"]))
        print(f"  [{objection['id']}] {objection['reviewer']} "
              f"| {objection['clause'] or 'section not resolved'}{note}")
        print(f"        {' '.join(objection['objection'].split())[:120]}")
    if sheet["_own_notes"]:
        print(f"\n  {len(sheet['_own_notes'])} of her own notes, not objections "
              "(nobody is waiting on a reply to these):")
        for note in sheet["_own_notes"]:
            print(f"    [{note['id']}] {note['clause'] or '-'}: "
                  f"{' '.join(note['note'].split())[:90]}")
    if args.json:
        Path(args.json).write_text(json.dumps(sheet, indent=2, ensure_ascii=False),
                                   encoding="utf-8")
        print(f"worksheet: {args.json}")
    return 0


def _cmd_compile(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.responses).read_text(encoding="utf-8"))
    try:
        round_ = round_from_dict(payload)
    except (ValueError, KeyError) as exc:
        print(f"worksheet unreadable: {exc}", file=sys.stderr)
        return 2

    findings = check_round(round_)
    if findings:
        print(format_findings(findings))
    stoppers = blocking(findings)
    if stoppers and not args.force:
        print(f"\n{len(stoppers)} blocking findings. Nothing written.", file=sys.stderr)
        print("Fix them, or pass --force to write the round anyway.", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    replies = out / "replies.md"
    register = out / "response-register.md"
    replies.write_text(replies_markdown(round_), encoding="utf-8")
    register.write_text(register_markdown(round_), encoding="utf-8")
    written = [replies, register]

    if args.docx:
        from ane_package.reporting.markdown_docx import render_markdown
        for source in (replies, register):
            target = source.with_suffix(".docx")
            report = render_markdown(source.read_text(encoding="utf-8"), target)
            written.append(target)
            for item in getattr(report, "unsupported", []) or []:
                print(f"  note  {target.name}: not rendered structurally — {item}")

    changed = [o for o in round_.objections if o.changes_tor]
    print(f"\n{len(round_.objections)} objections; {len(changed)} change the ToR.")
    for path in written:
        print(f"  {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser(
        "extract", help="read the objections out of a commented ToR")
    extract.add_argument("docx")
    extract.add_argument("--me", default="Ane Gasser",
                         help="whose replies count as having answered")
    extract.add_argument("--json", help="write the worksheet here")
    extract.add_argument("--include-resolved", action="store_true")
    extract.set_defaults(func=_cmd_extract)

    compile_ = subparsers.add_parser(
        "compile", help="guard a filled worksheet and write the round")
    compile_.add_argument("responses")
    compile_.add_argument("--out", default=".", help="directory to write into")
    compile_.add_argument("--docx", action="store_true",
                          help="also render branded Word beside the markdown")
    compile_.add_argument("--force", action="store_true",
                          help="write even when a blocking guard fails")
    compile_.set_defaults(func=_cmd_compile)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
