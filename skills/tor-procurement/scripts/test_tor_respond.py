#!/usr/bin/env python3
"""Verification for the tor-procurement respond-mode driver.

Only one function in the driver opens a document, so nothing here needs Word.
The verdict logic, every guard, the register and the worksheet are all checked
against constructed objects — including the thread reading, which stands on a
stub carrying the same surface as ``officeops.CommentThread``.

Run: python scripts/test_tor_respond.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tor_respond as tr  # noqa: E402

PASSED = 0
FAILED: list[str] = []


def check(condition: bool, label: str) -> None:
    global PASSED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED.append(label)
        print(f"  FAIL  {label}")


# --------------------------------------------------------------------------
# fixtures, none of them on disk
# --------------------------------------------------------------------------

def objection_payload(**overrides) -> dict:
    """A clean defend-plus-defer objection: the 2026-07-31 reference case."""
    payload = {
        "id": "c3",
        "reviewer": "Stefanie Wallach",
        "clause": "2. Objectives — Objective 1",
        "objection": "Why is this fenced off? A lot of our research does consider "
                     "client and service data.",
        "steelman": "Read at its strongest, the objection says the fence excludes "
                    "the research the federation most wants help with.",
        "verdict": "defend",
        "verdict_secondary": "defer",
        "sources": ["ToR section 2, Objective 1"],
        "reply_full": "The fence covers one category and leaves the rest in scope. "
                      "Aggregated data stays inside the assignment.",
        "reply_compact": "The fence covers one category. Aggregated data stays in scope.",
        "sizing": {
            "trigger": "A Member Association asks to run service-user data through a tool.",
            "profile_change": "A data-protection lawyer joins the panel.",
            "day_rate_band": [450, 650],
            "options": [
                {"name": "Narrow: one country pilot", "days": 12, "note": "One MA."},
                {"name": "Federation-wide protocol", "days": None,
                 "note": "Nobody has estimated this."},
            ],
        },
    }
    payload.update(overrides)
    return payload


def round_payload(*objections: dict, **overrides) -> dict:
    payload = {
        "tor": "AI for Research ToR v0.9",
        "round": "Review round 1, 2026-07-31",
        "objections": list(objections) or [objection_payload()],
    }
    payload.update(overrides)
    return payload


@dataclass
class FakeComment:
    id: str
    author: str
    text: str
    resolved: bool = False


@dataclass
class FakeThread:
    """Stands in for officeops.CommentThread. Same surface, no file behind it."""

    root: FakeComment
    section: str = ""
    block_index: int = 1
    anchor: str = "anchor text"
    replies: list = field(default_factory=list)

    def is_open(self, author: str = "") -> bool:
        if self.root.resolved:
            return False
        return not any(tr.same_person(author, reply.author) for reply in self.replies)


# --------------------------------------------------------------------------
# parsing and derivation
# --------------------------------------------------------------------------

def test_parsing() -> None:
    round_ = tr.round_from_dict(round_payload())
    check(len(round_.objections) == 1, "parse: one objection read")
    objection = round_.objections[0]
    check(objection.verdicts == ("defend", "defer"),
          f"parse: both verdicts kept in order (got {objection.verdicts})")
    check(objection.verdict_label() == "defend + defer",
          "parse: the compound verdict reads as one label")
    check(objection.sizing is not None and len(objection.sizing.options) == 2,
          "parse: sizing options survive")
    check(round_.compact_max_words == tr.DEFAULT_COMPACT_WORDS,
          "parse: the compact ceiling defaults")

    for missing in ("reviewer", "objection", "verdict"):
        payload = objection_payload()
        payload[missing] = ""
        try:
            tr.round_from_dict(round_payload(payload))
            check(False, f"parse: a missing {missing} raises")
        except ValueError as exc:
            check(missing in str(exc), f"parse: a missing {missing} raises and names it")

    payload = objection_payload(verdict="DEFEND ", verdict_secondary=None)
    parsed = tr.round_from_dict(round_payload(payload)).objections[0]
    check(parsed.verdicts == ("defend",),
          "parse: a verdict is normalised and an absent secondary is not invented")

    try:
        bad = objection_payload()
        bad["sizing"] = dict(bad["sizing"], day_rate_band=[650, 450])
        tr.round_from_dict(round_payload(bad))
        check(False, "parse: an inverted rate band raises")
    except ValueError:
        check(True, "parse: an inverted rate band raises")


def test_changes_tor() -> None:
    cases = {
        ("defend", ""): False,
        ("defend", "defer"): False,
        ("defer", ""): False,
        ("escalate", ""): False,
        ("concede", ""): True,
        ("concede", "defer"): True,
    }
    for (primary, secondary), expected in cases.items():
        payload = objection_payload(verdict=primary, verdict_secondary=secondary,
                                    edit="Add one sentence." if primary == "concede" else "")
        objection = tr.round_from_dict(round_payload(payload)).objections[0]
        check(objection.changes_tor is expected,
              f"verdict: {primary}{'+' + secondary if secondary else ''} "
              f"{'changes' if expected else 'leaves'} the ToR")

    check(sum(1 for value in cases.values() if value) == 2,
          "verdict: only concession moves the document")


def test_word_count() -> None:
    check(tr.word_count("one two three") == 3, "count: words are counted, not estimated")
    check(tr.word_count("  spaced   out \n lines ") == 3,
          "count: whitespace does not inflate the count")
    check(tr.word_count("") == 0, "count: an empty reply counts zero")


# --------------------------------------------------------------------------
# guards
# --------------------------------------------------------------------------

def codes(payload: dict) -> set[str]:
    return {finding.code for finding in tr.check_round(tr.round_from_dict(payload))}


def test_clean_round() -> None:
    found = codes(round_payload())
    check(not found, f"guard: the reference case passes every guard (got {found})")
    check(not tr.blocking(tr.check_round(tr.round_from_dict(round_payload()))),
          "guard: nothing blocks a clean round")


def test_contradictions() -> None:
    check("CONTRADICTORY_VERDICT" in codes(round_payload(
        objection_payload(verdict="defend", verdict_secondary="concede",
                          edit="Rewrite the clause."))),
        "guard: defend plus concede is refused")
    check("CONTRADICTORY_VERDICT" in codes(round_payload(
        objection_payload(verdict="defer", verdict_secondary="defer"))),
        "guard: the same verdict twice is refused")
    check("CONTRADICTORY_VERDICT" not in codes(round_payload()),
          "guard: defend plus defer is allowed — it is the reference case")
    check("UNKNOWN_VERDICT" in codes(round_payload(objection_payload(verdict="reject"))),
          "guard: a verdict outside the four is refused")


def test_edit_guards() -> None:
    check("EDIT_WITHOUT_CONCESSION" in codes(round_payload(
        objection_payload(edit="Delete the sentence."))),
        "guard: an edit attached to a defence is refused")
    check("CONCESSION_WITHOUT_EDIT" in codes(round_payload(
        objection_payload(verdict="concede", verdict_secondary="", edit="",
                          sizing=None))),
        "guard: a concession naming no edit is refused")
    check("EDIT_WITHOUT_CONCESSION" not in codes(round_payload(
        objection_payload(verdict="concede", verdict_secondary="",
                          edit="Add 'aggregated' before 'data'.", sizing=None))),
        "guard: a concession with its edit passes")


def test_sizing_guards() -> None:
    check("DEFER_WITHOUT_SIZING" in codes(round_payload(
        objection_payload(sizing=None))),
        "guard: deferring without sizing the follow-on is refused")
    check("SIZING_WITHOUT_DEFER" in codes(round_payload(
        objection_payload(verdict="defend", verdict_secondary=""))),
        "guard: sizing a follow-on nobody deferred to is refused")

    zeroed = objection_payload()
    zeroed["sizing"] = dict(zeroed["sizing"],
                            options=[{"name": "Pilot", "days": 0}])
    check("SIZING_ZERO_DAYS" in codes(round_payload(zeroed)),
          "guard: an option estimated at zero days is refused")
    check("SIZING_ZERO_DAYS" not in codes(round_payload()),
          "guard: an option nobody estimated is not the same as zero")


def test_source_guard() -> None:
    check("UNSOURCED_DEFENCE" in codes(round_payload(
        objection_payload(sources=[]))),
        "guard: a defence citing nothing is refused")
    check("UNSOURCED_DEFENCE" in codes(round_payload(
        objection_payload(sources=["  "]))),
        "guard: a blank source does not count as a source")
    check("UNSOURCED_DEFENCE" not in codes(round_payload(
        objection_payload(verdict="escalate", verdict_secondary="", sources=[],
                          sizing=None))),
        "guard: escalating out of the ToR needs no clause to cite")


def test_length_and_craft_guards() -> None:
    long_compact = objection_payload(reply_compact=" ".join(["word"] * 200))
    found = tr.check_round(tr.round_from_dict(round_payload(long_compact)))
    hit = next(f for f in found if f.code == "COMPACT_TOO_LONG")
    check("200 words" in hit.message,
          f"guard: the compact ceiling reports the counted length ({hit.message})")
    check(not tr.blocking([hit]), "guard: an overlong reply warns, it does not block")

    tight = round_payload(objection_payload(reply_compact=" ".join(["word"] * 200)),
                          compact_max_words=250)
    check("COMPACT_TOO_LONG" not in codes(tight),
          "guard: the ceiling is a setting, not a constant")

    check("FULL_TOO_LONG" in codes(round_payload(
        objection_payload(reply_full=" ".join(["word"] * 600)))),
        "guard: the full reply has its own ceiling")
    check("MISSING_REPLY" in codes(round_payload(objection_payload(reply_compact=""))),
          "guard: an empty reply is refused")
    check("NO_STEELMAN" in codes(round_payload(objection_payload(steelman=""))),
          "guard: answering without stating the strongest version warns")
    check("DUPLICATE_ID" in codes(round_payload(objection_payload(),
                                                objection_payload())),
          "guard: two objections cannot share an id")


def test_voice_guard() -> None:
    found = codes(round_payload(objection_payload(
        reply_full="It should be noted that we might want to consider the clause.")))
    check("VOICE" in found, "guard: hedging and filler in a reply is flagged")
    check("VOICE" not in codes(round_payload()),
          "guard: a clean reply raises no voice finding")


def test_blocking_split() -> None:
    findings = [tr.Finding("CONTRADICTORY_VERDICT", "c1", "x"),
                tr.Finding("COMPACT_TOO_LONG", "c1", "y"),
                tr.Finding("VOICE", "c1", "z")]
    check([f.code for f in tr.blocking(findings)] == ["CONTRADICTORY_VERDICT"],
          "guard: only the findings that reach someone else block the round")
    rendered = tr.format_findings(findings)
    check("BLOCK" in rendered and "warn" in rendered,
          "guard: the render marks which findings stop the round")
    check(tr.format_findings([]) == "No findings.", "guard: a clean round says so")


# --------------------------------------------------------------------------
# outputs
# --------------------------------------------------------------------------

def test_register() -> None:
    conceded = objection_payload(id="c5", verdict="concede", verdict_secondary="",
                                 edit="Add 'aggregated' before 'data'.", sizing=None)
    round_ = tr.round_from_dict(round_payload(objection_payload(), conceded))
    text = tr.register_markdown(round_)

    rows = [line for line in text.splitlines()
            if line.startswith("| ") and not line.startswith("| #")
            and not line.startswith("|---")]
    check(len(rows) == 2,
          f"register: one row per objection whatever the verdict (got {len(rows)})")
    check("1 change the ToR; 1 do not" in text,
          "register: the split between changed and unchanged is counted")
    check("Revision list for finalise mode" in text,
          "register: the conceded rows are handed to finalise")
    check(text.count("Add 'aggregated' before 'data'.") == 2,
          "register: the edit appears in its row and in the revision list")

    defended_only = tr.register_markdown(tr.round_from_dict(round_payload()))
    check("Revision list for finalise mode" not in defended_only,
          "register: a round that changes nothing hands finalise no list")

    piped = tr.register_markdown(tr.round_from_dict(round_payload(
        objection_payload(clause="Section 2 | Objective 1"))))
    check(r"Section 2 \| Objective 1" in piped,
          "register: a pipe in a clause name cannot break the table")


def test_replies() -> None:
    text = tr.replies_markdown(tr.round_from_dict(round_payload()))
    check("### Full reply (" in text and "### Compact reply (" in text,
          "replies: both lengths are written")
    expected = tr.word_count(objection_payload()["reply_compact"])
    check(f"### Compact reply ({expected} words)" in text,
          f"replies: the heading carries the counted length ({expected})")
    check("The ToR does not change." in text,
          "replies: the reader is told whether the document moves")
    check("**Answered from:** ToR section 2, Objective 1" in text,
          "replies: the sources the answer rests on are named")
    check("strongest version" in text,
          "replies: the steelman reaches the page")


def test_sizing_output() -> None:
    objection = tr.round_from_dict(round_payload()).objections[0]
    text = tr.sizing_markdown(objection)
    check("EUR 5,400 to 7,800" in text,
          "sizing: a costed option multiplies days by the supplied band")
    check("not costed" in text and "not estimated" in text,
          "sizing: an unestimated option says so rather than costing zero")
    check("Indicative only" in text, "sizing: the bands are marked uncosted")
    check("not assessed: no threshold was supplied" in objection.sizing.route_note(),
          "sizing: with no threshold the route is not guessed")

    objection.sizing.route_threshold = 5000
    check("cannot be a direct award" in objection.sizing.route_note(),
          "sizing: an option reaching the stated threshold rules out a direct award")
    objection.sizing.route_threshold = 50000
    check("tops out below" in objection.sizing.route_note(),
          "sizing: below the threshold it says so")
    objection.sizing.day_rate_band = None
    check("no option carries both" in objection.sizing.route_note(),
          "sizing: without a rate band the route cannot be assessed either")
    check("no option is costed" in tr.sizing_markdown(objection),
          "sizing: without a rate band nothing is priced")


# --------------------------------------------------------------------------
# the worksheet
# --------------------------------------------------------------------------

def test_worksheet() -> None:
    threads = [
        FakeThread(FakeComment("1", "Stefanie Wallach", "Why is this fenced off?"),
                   section="2. Objectives", block_index=66),
        FakeThread(FakeComment("2", "Ane Gasser", "Most research is unaffected."),
                   section="2. Objectives", block_index=66),
        FakeThread(FakeComment("3", "Dome Jagalo", "Recognise this as a deliverable."),
                   section="3. Scope of work", block_index=74,
                   replies=[FakeComment("4", "Ane Gasser PERSONAL", "Agreed.")]),
        FakeThread(FakeComment("5", "Ane Gasser PERSONAL", "To do: book the panel."),
                   section="5. Timeline", block_index=90),
    ]
    sheet = tr.worksheet(threads, me="Ane Gasser", tor="v0.9.docx")

    check([o["id"] for o in sheet["objections"]] == ["c1"],
          f"worksheet: only the unanswered objection is listed "
          f"(got {[o['id'] for o in sheet['objections']]})")
    check(sheet["_read"]["own_notes"] == 2,
          "worksheet: her own comments are her notes, not objections to answer")
    check(sheet["_read"]["answered"] == 1,
          "worksheet: a thread she replied to counts as answered")
    check(sheet["_read"]["threads"] == 4,
          "worksheet: every thread is accounted for, none silently dropped")
    check(sum([sheet["_read"]["open"], sheet["_read"]["own_notes"],
               sheet["_read"]["answered"]]) == sheet["_read"]["threads"],
          "worksheet: the three counts add back to the total")

    check(sheet["objections"][0]["also_on_this_clause"] == ["Ane Gasser"],
          "worksheet: another comment on the same paragraph is surfaced, because "
          "Word only records a reply as a reply when the reply button was used")
    check(sheet["objections"][0]["clause"] == "2. Objectives",
          "worksheet: the section is carried through as the clause")
    check(sheet["objections"][0]["verdict"] == "",
          "worksheet: extract decides nothing")
    check([note["id"] for note in sheet["_own_notes"]] == ["c2", "c5"],
          "worksheet: the own notes are listed, not just counted")

    resolved = [FakeThread(FakeComment("9", "Stefanie Wallach", "Fine now.",
                                       resolved=True))]
    check(not tr.worksheet(resolved, me="Ane Gasser")["objections"],
          "worksheet: a resolved thread needs no answer")


def test_file_boundary() -> None:
    source = Path(tr.__file__).read_text(encoding="utf-8")
    openers = [line for line in source.splitlines()
               if "comment_threads(" in line and "def " not in line
               and "import" not in line]
    check(len(openers) == 1,
          f"boundary: exactly one call opens the document (found {len(openers)})")
    check("def load_threads" in source and
          source.index("def load_threads") < source.index("comment_threads(path"),
          "boundary: it is load_threads that opens it")


def test_cli() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="tor-respond-"))
    responses = tmp / "round.json"
    responses.write_text(json.dumps(round_payload()), encoding="utf-8")
    code = tr.main(["compile", str(responses), "--out", str(tmp)])
    check(code == 0, f"cli: a clean round compiles at exit 0 (got {code})")
    check((tmp / "replies.md").exists() and (tmp / "response-register.md").exists(),
          "cli: both artefacts are written")

    bad = tmp / "bad.json"
    bad.write_text(json.dumps(round_payload(
        objection_payload(edit="Delete it."))), encoding="utf-8")
    out = tmp / "blocked"
    code = tr.main(["compile", str(bad), "--out", str(out)])
    check(code == 1, f"cli: a contradictory round exits 1 (got {code})")
    check(not out.exists(),
          "cli: and writes nothing — a refused round leaves no half-artefact")
    check(tr.main(["compile", str(bad), "--out", str(out), "--force"]) == 0,
          "cli: --force writes it anyway")

    unreadable = tmp / "unreadable.json"
    unreadable.write_text(json.dumps(round_payload(
        objection_payload(verdict=""))), encoding="utf-8")
    check(tr.main(["compile", str(unreadable), "--out", str(tmp)]) == 2,
          "cli: an unreadable worksheet exits 2, distinct from a refused one")
    check(tr.main(["extract", str(tmp / "nothing.docx")]) == 2,
          "cli: a missing document exits 2")


def main() -> int:
    test_parsing()
    test_changes_tor()
    test_word_count()
    test_clean_round()
    test_contradictions()
    test_edit_guards()
    test_sizing_guards()
    test_source_guard()
    test_length_and_craft_guards()
    test_voice_guard()
    test_blocking_split()
    test_register()
    test_replies()
    test_sizing_output()
    test_worksheet()
    test_file_boundary()
    test_cli()

    total = PASSED + len(FAILED)
    print()
    print(f"{PASSED}/{total} checks passed (tor-procurement respond)")
    for label in FAILED:
        print(f"  FAILED: {label}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
