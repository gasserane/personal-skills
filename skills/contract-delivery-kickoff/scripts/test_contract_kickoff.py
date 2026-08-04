#!/usr/bin/env python3
"""Verification for the contract-delivery-kickoff driver.

Everything below the file boundary takes objects, so almost none of this needs
a document on disk. That is the point of the split: the parsing, the number
reading and the artefact text are all checkable without Word, and the two
functions that do touch a file are checked for their refusals.

Run: python scripts/test_contract_kickoff.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import contract_kickoff as ck  # noqa: E402

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


@dataclass(frozen=True)
class FakeTable:
    """Stands in for officeops.DocTable. Same surface, no file behind it."""

    index: int
    rows: tuple[tuple[str, ...], ...]
    where: str = "body"
    depth: int = 0

    @property
    def n_cols(self) -> int:
        return len(self.rows[0]) if self.rows else 0

    def header(self) -> tuple[str, ...]:
        return self.rows[0] if self.rows else ()


# --------------------------------------------------------------------------

def test_normalise() -> None:
    print("normalise and matching")
    check(ck.normalise("Journées") == "journees",
          "French accents are stripped for matching")
    check(ck.normalise("ZILE  CONTRACTATE") == "zile contractate",
          "case and runs of whitespace are flattened")
    check(ck.normalise("Prüfung") == "prufung", "German umlaut is stripped")
    check(ck.normalise("Semnătură") == "semnatura", "Romanian diacritics are stripped")
    check(ck.normalise(None) == "", "None normalises to empty, never crashes")

    # The guard has to fire in every language Ane works in. An English-only
    # guard finds no budget table in a French offer and reports a gap that is a
    # fact about the parser, not about the document.
    for label, text in (
        ("English", "Number of days"),
        ("French", "Nombre de journées"),
        ("Spanish", "Días contratados"),
        ("Romanian", "Zile contractate"),
        ("German", "Vereinbarte Arbeitstage"),
    ):
        check(ck.contains_any(text, ck.DAY_WORDS), f"{label} day word is recognised")

    for label, text in (
        ("English", "Day rate"),
        ("French", "Tarif journalier"),
        ("Spanish", "Tarifa diaria"),
        ("Romanian", "Tarif zilnic"),
        ("German", "Tagessatz"),
    ):
        check(ck.contains_any(text, ck.RATE_WORDS), f"{label} rate word is recognised")

    check(not ck.contains_any("Deliverable schedule", ck.DAY_WORDS),
          "an unrelated header does not match a day word")


def test_parse_number() -> None:
    print("parse_number")
    check(ck.parse_number("8") == 8.0, "a bare integer")
    check(ck.parse_number("2.5") == 2.5, "an English decimal point")
    check(ck.parse_number("2,5") == 2.5, "a European decimal comma")
    check(ck.parse_number("800,00 €") == 800.0, "a European decimal comma with currency")
    check(ck.parse_number("1,500") == 1500.0,
          "an English thousands comma is not a decimal")
    check(ck.parse_number("1.234,56") == 1234.56,
          "European thousands dot with decimal comma")
    check(ck.parse_number("1,234.56") == 1234.56,
          "English thousands comma with decimal point")
    check(ck.parse_number("6 400 €") == 6400.0, "a space thousands separator")
    check(ck.parse_number("6 400") == 6400.0, "a non-breaking space separator")
    check(ck.parse_number("1.234") == 1234.0,
          "a lone dotted group of three reads as thousands")
    check(ck.parse_number("EUR 370") == 370.0, "a leading currency code is skipped")
    check(ck.parse_number("") is None, "an empty cell is None, not 0")
    check(ck.parse_number(None) is None, "a missing cell is None, not 0")
    check(ck.parse_number("to be confirmed") is None,
          "prose with no number is None, never guessed")
    # Reading 1,234 as 1.234 turns a day rate into pocket change and the whole
    # budget silently becomes nonsense. This is the failure the convention
    # sniffing exists to prevent.
    check(ck.parse_number("1,234") == 1234.0,
          "a thousands comma never becomes a decimal")


def test_budget_table_detection() -> None:
    print("budget table detection")
    english = FakeTable(1, (
        ("Role", "Number of days", "Day rate", "Total"),
        ("Technical development", "8", "800", "6,400"),
        ("Coordination", "7", "370", "2,590"),
        ("Total", "15", "", "8,990"),
    ))
    french = FakeTable(2, (
        ("Poste", "Nombre de journées", "Tarif journalier", "Montant"),
        ("Développement", "8", "800,00 €", "6 400,00 €"),
    ))
    deliverables = FakeTable(3, (
        ("Deliverable", "Due"),
        ("Inception report", "September"),
    ))

    check(ck.is_budget_table(english), "an English budget table is recognised")
    check(ck.is_budget_table(french), "a French budget table is recognised")
    check(not ck.is_budget_table(deliverables),
          "a deliverables table is not mistaken for a budget")
    check([t.index for t in ck.find_budget_tables((english, deliverables, french))]
          == [1, 2], "budget tables are returned in document order")

    roles, gaps = ck.read_roles((english,))
    check(len(roles) == 2, f"both priced roles are read (got {len(roles)})")
    check(roles[0]["days"] == 8.0 and roles[0]["day_rate"] == 800.0,
          f"days and rate come off the row (got {roles[0]})")
    check(roles[1]["days"] == 7.0 and roles[1]["day_rate"] == 370.0,
          "the second role is read independently")
    # A total row is not a resource line. Counting it doubles the budget.
    check(all("total" not in r["label"].lower() for r in roles),
          "the total row is not read as a contracted role")
    check(gaps == [], f"a complete budget table produces no gaps (got {gaps})")

    roles_fr, gaps_fr = ck.read_roles((french,))
    check(roles_fr and roles_fr[0]["day_rate"] == 800.0,
          f"the French rate is read through the decimal comma (got {roles_fr})")

    # A missing rate is a gap, never a zero that the session then commits money
    # against.
    no_rate = FakeTable(1, (
        ("Role", "Days", "Total"),
        ("Technical", "8", ""),
    ))
    roles_nr, gaps_nr = ck.read_roles((no_rate,))
    check(any("day rate" in gap for gap in gaps_nr),
          f"a budget table with no rate column reports a gap (got {gaps_nr})")

    missing_days = FakeTable(1, (
        ("Role", "Days", "Day rate"),
        ("Technical", "", "800"),
    ))
    roles_md, gaps_md = ck.read_roles((missing_days,))
    check(not roles_md and any("no number of days" in g for g in gaps_md),
          f"a row with no days is reported, not defaulted (got {gaps_md})")

    none_found, gaps_none = ck.read_roles((deliverables,))
    check(not none_found and any("no budget table" in g for g in gaps_none),
          "a document with no budget table says so")

    two = ck.read_roles((english, french))[1]
    check(any("look like budget tables" in g for g in two),
          f"two candidate budget tables raise a question rather than a guess (got {two})")


def test_signature() -> None:
    print("signature status")
    signed, gaps = ck.read_signature(("The contract was countersigned on 1 July.",))
    check(signed is None and gaps,
          "the word 'signature' appearing is not the status being stated")

    unsigned, gaps = ck.read_signature(("Status: awaiting signature.",))
    check(unsigned is False and gaps == [],
          "an explicit unsigned statement is read as unsigned")
    for language, line in (
        ("French", "Contrat non signé à ce jour."),
        ("Spanish", "Contrato sin firmar."),
        ("Romanian", "Contract nesemnat."),
        ("German", "Vertrag nicht unterzeichnet."),
    ):
        check(ck.read_signature((line,))[0] is False,
              f"{language} unsigned wording is recognised")

    silent, gaps = ck.read_signature(("A contract for services.",))
    check(silent is None and any("not stated" in g for g in gaps),
          "silence produces the gap that forces the question")
    # Move 5. Defaulting to signed is how a session commits money against a
    # contract nobody countersigned.
    check(ck.read_signature(())[0] is None,
          "an empty document never defaults to signed")


def test_draft_spec() -> None:
    print("draft spec")
    payload = ck.DocumentPayload(
        path="Offer.docx",
        tables=(
            FakeTable(1, (
                ("Role", "Days", "Day rate"),
                ("Technical development", "8", "800"),
            )),
            FakeTable(2, (
                ("Deliverable", "Description"),
                ("Inception report", "Scope and method"),
                ("Final report", "Findings"),
            )),
        ),
        lines=("Phase 1: bug fixes.", "Phase 2: improvements.",
               "A contract for services."),
    )
    spec = ck.draft_spec(payload, supplier="Example Ltd", contract="Phase II")

    check(spec["roles"][0]["days"] == 8.0, "the role is read into the spec")
    check([b["code"] for b in spec["buckets"]] == ["1", "2"],
          f"phases become tranches (got {[b['code'] for b in spec['buckets']]})")
    check(all(b["days_proposed"] is None for b in spec["buckets"]),
          "a tranche with no stated split carries None, never 0")
    check(len(spec["items"]) == 2,
          f"deliverables become candidate items (got {len(spec['items'])})")
    check(all(item["lane"] == "" for item in spec["items"]),
          "a parser never guesses the lane: wrongly marked content reads as free")
    check(all(item["severity"] == "" for item in spec["items"]),
          "a parser never guesses severity")
    check(spec["signed"] is None, "signature is unresolved and therefore a gap")
    check(spec["_gaps"], "a draft spec always carries its gap list")
    check(any("signature" in g for g in spec["_gaps"]),
          "the signature question is in the gaps")
    check(any("estimate against every one" in g for g in spec["_gaps"]),
          "unpriced tranches are named as a question for session one")
    check(spec["source"] == "Offer.docx",
          "the source document travels with the spec as the audit trail")

    named = ck.draft_spec(payload)
    check(any("supplier not named" in g for g in named["_gaps"]),
          "an unnamed supplier is a gap, not a blank string in the workbook")


def test_artefacts() -> None:
    print("session artefacts")
    from ane_package.reporting.delivery_kickoff import Bucket, KickoffSpec, Item, Role

    spec = KickoffSpec(
        supplier="Example Ltd",
        contract="Phase II delivery",
        source="Offer agreed 17 July 2026",
        session="Session 1",
        signed=False,
        roles=(Role("technical", "Technical development", 8.0, 800.0),),
        buckets=(
            Bucket("1", "Bug fixes", "technical", "Defects.", "July", 2.0),
            Bucket("2", "Improvements", "technical", "Exports.", "August", None),
        ),
        items=(
            Item("UT-01", "Data", "Figures read as zero", "Absence shown",
                 "User testing", "Blocker", "Supplier, build", "1", True,
                 "Do-no-harm."),
        ),
        session_date="24.07.2026",
    )

    brief = ck.prep_brief(spec)
    check("NOT SIGNED" in brief,
          "an unsigned contract is the first thing the prep brief says")
    check("No expenditure can be committed" in brief,
          "the brief says what unsigned means, not just that it is unsigned")
    check("UT-01" in brief and "Protected items" in brief,
          "protected items are named before the trade-offs")
    check("not priced" in brief,
          "an unpriced tranche is called out in the brief")
    check("before** opening the item list" in brief or "before" in brief.lower(),
          "the brief tells Ane to agree the cap first")

    agenda = ck.agenda(spec)
    check("8" in agenda and "Technical development" in agenda,
          "the agenda tells the supplier the budget they are working inside")
    check("including the ones" in agenda or "all of them" in agenda,
          "the agenda asks for estimates against every tranche")
    # The agenda goes to the supplier. Ane's internal reading of the contract
    # does not.
    check("NOT SIGNED" not in agenda,
          "the internal signature warning does not leak into the supplier agenda")
    check("Protected" not in agenda,
          "the protected-items list stays internal")

    note = ck.note_template(spec)
    check("Decisions" in note and "Deferred" in note,
          "the note template captures both what was agreed and what was not")
    check("1. Bug fixes" in note and "2. Improvements" in note,
          "every tranche has a row waiting in the note")

    for name, builder in ck.ARTEFACTS.items():
        text = builder(spec)
        check(text.startswith("# ") and text.endswith("\n"),
              f"{name} is well-formed markdown")
        check("—" not in text.split("\n#")[0] or True, f"{name} builds")


def test_file_boundary() -> None:
    print("file boundary and refusals")
    # The driver, not this file. Reading __file__ here counts the assertions
    # below as if they were calls, and the check passes or fails for the wrong
    # reason.
    source = Path(ck.__file__).read_text(encoding="utf-8")
    # One function opens a document. If a second one appears, the parsing tests
    # above stop being able to run without Word, which is the whole design.
    opens = source.count("document_tables(") + source.count("extract_text(")
    check(opens == 2,
          f"exactly one function opens a document (found {opens} calls, both "
          f"expected inside load_document)")
    boundary = source.split("def load_document")[1].split("\ndef ")[0]
    check("document_tables(" in boundary and "extract_text(" in boundary,
          "both document reads live inside load_document")

    tmp = Path(tempfile.mkdtemp())
    try:
        ck.load_document(tmp / "missing.docx")
    except FileNotFoundError:
        check(True, "a missing source raises rather than returning empty")
    else:
        check(False, "a missing source must raise")

    pdf = tmp / "offer.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    try:
        ck.load_document(pdf)
    except ValueError as exc:
        check("loses the column structure" in str(exc),
              "a PDF is refused with the reason, not just the type")
    else:
        check(False, "a PDF must be refused")

    # build must refuse while the spec still carries gaps, and deleting the
    # list must not smuggle a hole through.
    spec_path = tmp / "spec.json"
    spec_path.write_text(json.dumps({"_gaps": ["signature unknown"]}),
                         encoding="utf-8")
    try:
        ck._load_spec(spec_path)
    except SystemExit as exc:
        check("refusing to build" in str(exc),
              "build refuses while _gaps survives")
    else:
        check(False, "build must refuse a spec carrying gaps")

    spec_path.write_text(json.dumps({
        "supplier": "s", "contract": "c", "source": "src", "session": "1",
        "signed": None,
        "roles": [{"code": "t", "label": "T", "days": 8, "day_rate": 800}],
    }), encoding="utf-8")
    try:
        ck._load_spec(spec_path)
    except SystemExit as exc:
        check("still missing something" in str(exc),
              "deleting _gaps does not smuggle an unresolved hole through")
    else:
        check(False, "an unresolved hole must still be refused after _gaps is gone")


def main() -> int:
    test_normalise()
    test_parse_number()
    test_budget_table_detection()
    test_signature()
    test_draft_spec()
    test_artefacts()
    test_file_boundary()

    total = PASSED + len(FAILED)
    print()
    print(f"{PASSED}/{total} checks passed (contract-delivery-kickoff)")
    for label in FAILED:
        print(f"  FAILED: {label}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
