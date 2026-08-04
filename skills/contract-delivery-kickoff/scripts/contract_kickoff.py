#!/usr/bin/env python3
"""Prepare the first working session of a delivery contract, against its budget.

Three subcommands:

``read``
    Open the agreed offer or contract and report what it states about
    contracted days, rates, tranches and signature — and what it does not.
    Writes a draft spec carrying ``_gaps``. Never fills one.
``build``
    Turn a confirmed spec into the session pack: a branded workbook, and a prep
    brief, agenda and note template in markdown with Word rendered from it.
``verify``
    Drive the written workbook through Excel, recalculate, and assert the
    numbers Excel produces against the same Python engine the formulas were
    written from.

**The file boundary.** Exactly one function here opens a document:
:func:`load_document`. Everything downstream takes objects and opens nothing,
which is what makes the parsing testable without a single fixture on disk. All
Office plumbing lives in ``ane_package``; this file contributes text judgement.

**Nothing is invented.** A contract that does not state a day rate produces a
gap, not a plausible rate from a similar contract. A number in a cell is
indistinguishable from a published one once it is there, and the session
commits against it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

WORK_FOLDER_ROOT = os.environ.get(
    "WORK_FOLDER_ROOT", r"C:\Users\AGasser\OneDrive\5 ANE CLAUDE work folder"
)
if WORK_FOLDER_ROOT not in sys.path:
    sys.path.insert(0, WORK_FOLDER_ROOT)

from ane_package.reporting.delivery_kickoff import (  # noqa: E402
    KickoffSpec,
    UnstatedInSource,
    allocation,
    budget_status,
    build_kickoff_workbook,
    over_commitment_signal,
    protected_items,
    spec_from_dict,
)

# --------------------------------------------------------------------------
# Multilingual vocabulary
#
# Ane's contracts arrive in English, French, Spanish, Romanian and German. An
# English-only guard finds no budget table in a French offer and reports a gap
# that is a fact about the parser, not about the document. Three waves running,
# this has been the bite.
# --------------------------------------------------------------------------

DAY_WORDS = (
    "day", "days",
    "jour", "jours", "journee", "journees",
    "dia", "dias", "jornada", "jornadas",
    "zi", "zile",
    "tag", "tage", "arbeitstag", "arbeitstage", "personentag", "personentage",
    "man-day", "man-days", "person-day", "person-days",
)

RATE_WORDS = (
    "rate", "day rate", "daily rate", "unit price", "fee",
    "tarif", "taux", "prix unitaire", "honoraire", "honoraires",
    "tarifa", "tasa", "precio unitario", "honorario", "honorarios",
    "tarif zilnic", "rata", "onorariu", "pret unitar",
    "satz", "tagessatz", "honorar", "einzelpreis", "stundensatz",
)

TOTAL_WORDS = (
    "total", "subtotal", "sum", "amount",
    "totale", "montant", "somme",
    "importe", "suma", "monto",
    "gesamt", "gesamtsumme", "betrag", "summe",
)

QUANTITY_WORDS = ("quantity", "qty", "number", "nombre", "quantite", "cantidad",
                  "numar", "cantitate", "anzahl", "menge")

SIGNED_WORDS = (
    "signed", "signature", "countersigned", "executed",
    "signe", "signee", "signature", "contresigne",
    "firmado", "firma", "suscrito",
    "semnat", "semnatura", "semnat de",
    "unterzeichnet", "unterschrift", "unterschrieben", "gegengezeichnet",
)

UNSIGNED_WORDS = (
    "not signed", "unsigned", "awaiting signature", "pending signature",
    "non signe", "en attente de signature",
    "sin firmar", "no firmado", "pendiente de firma",
    "nesemnat", "in asteptarea semnaturii",
    "nicht unterzeichnet", "unterschrift ausstehend",
)

CURRENCY_SYMBOLS = ("€", "$", "£", "EUR", "USD", "GBP", "CHF", "RON")

# A bucket, tranche, phase or lot: the tranches a contract splits delivery into.
BUCKET_WORDS = (
    "bucket", "tranche", "phase", "lot", "batch", "stage", "workstream",
    "etape", "tranche", "phase", "lot",
    "fase", "etapa", "lote",
    "etapa", "faza", "transa",
    "phase", "los", "stufe", "arbeitspaket",
)


def normalise(text: str) -> str:
    """Lower-case and strip accents, so one guard covers five languages.

    ``Journées`` and ``journees`` have to match the same word, or a French offer
    silently reports no budget table.
    """
    decomposed = unicodedata.normalize("NFKD", str(text or ""))
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", stripped).strip().lower()


def contains_any(text: str, words: tuple[str, ...]) -> bool:
    flat = normalise(text)
    return any(normalise(word) in flat for word in words)


_NUMBER = re.compile(r"-?\d[\d\s.,\u00a0']*\d|-?\d")


def parse_number(text: str) -> float | None:
    """Read a number written in either decimal convention. ``None`` when absent.

    ``1.234,56`` is one thousand two hundred and thirty-four in French, Spanish,
    Romanian and German, and one point two in English. Guessing wrong turns a
    1,234 EUR day rate into 1.234 and the whole budget is nonsense, so the
    convention is inferred from the separators actually present rather than
    assumed.
    """
    if text is None:
        return None
    raw = str(text).strip()
    if not raw:
        return None
    match = _NUMBER.search(raw.replace("\u00a0", " "))
    if not match:
        return None
    token = match.group(0).replace(" ", "").replace("'", "")

    has_comma = "," in token
    has_dot = "." in token
    if has_comma and has_dot:
        # Whichever separator comes last is the decimal point.
        decimal = "," if token.rfind(",") > token.rfind(".") else "."
        thousands = "." if decimal == "," else ","
        token = token.replace(thousands, "").replace(decimal, ".")
    elif has_comma:
        # A single comma with exactly three digits after it is a thousands
        # separator in English and a decimal comma nowhere: 1,500 is 1500.
        tail = token.rsplit(",", 1)[1]
        token = token.replace(",", "" if len(tail) == 3 else ".")
    elif has_dot:
        tail = token.rsplit(".", 1)[1]
        if len(tail) == 3 and token.count(".") == 1 and len(token.split(".")[0]) <= 3:
            # 1.234 is ambiguous. Treat it as thousands only when nothing else
            # in the document disambiguates, which is the commoner reading for
            # a money column in the four non-English languages here.
            token = token.replace(".", "")
    try:
        return float(token)
    except ValueError:
        return None


# --------------------------------------------------------------------------
# The file boundary — the only function that opens a document
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class DocumentPayload:
    """Everything read off disk, so nothing downstream needs the file again."""

    path: str
    tables: tuple  # tuple[DocTable, ...]
    lines: tuple[str, ...]


def load_document(path: str | Path) -> DocumentPayload:
    """Open the offer once and hand back objects.

    The only function in this file that touches a document. Everything after it
    is text logic over the returned payload, which is why the parsing tests
    below need no .docx fixture at all.
    """
    from ane_package.officeops import document_tables, extract_text

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() != ".docx":
        raise ValueError(
            f"read expects a .docx, got {path.suffix or 'no suffix'}; convert a "
            f"legacy .doc or a .pdf in Word first, because a table read out of "
            f"a PDF loses the column structure the budget depends on"
        )
    return DocumentPayload(
        path=str(path),
        tables=tuple(document_tables(path)),
        lines=tuple(extract_text(path)),
    )


# --------------------------------------------------------------------------
# Pure parsing — takes objects, opens nothing
# --------------------------------------------------------------------------

def is_budget_table(table) -> bool:
    """A table pricing days: a day column plus a rate, total or money column."""
    header = " | ".join(table.header())
    if not contains_any(header, DAY_WORDS + QUANTITY_WORDS):
        return False
    return (
        contains_any(header, RATE_WORDS + TOTAL_WORDS)
        or any(symbol in header for symbol in CURRENCY_SYMBOLS)
    )


def find_budget_tables(tables) -> list:
    return [table for table in tables if is_budget_table(table)]


def _column_index(header: tuple[str, ...], words: tuple[str, ...]) -> int | None:
    for index, cell in enumerate(header):
        if contains_any(cell, words):
            return index
    return None


def read_roles(tables) -> tuple[list[dict], list[str]]:
    """Contracted resource lines from the budget table, plus what is missing.

    Returns dicts rather than :class:`Role` objects because a line missing its
    rate still has to be shown to Ane, and ``Role`` would refuse to hold it.
    """
    gaps: list[str] = []
    budget_tables = find_budget_tables(tables)
    if not budget_tables:
        gaps.append(
            "no budget table found: the contract must price the days, or the "
            "session has no ceiling to plan against"
        )
        return [], gaps

    table = budget_tables[0]
    if len(budget_tables) > 1:
        gaps.append(
            f"{len(budget_tables)} tables look like budget tables (indices "
            f"{', '.join(str(t.index) for t in budget_tables)}); confirm which "
            f"one prices this contract"
        )

    header = table.header()
    day_column = _column_index(header, DAY_WORDS + QUANTITY_WORDS)
    rate_column = _column_index(header, RATE_WORDS)
    label_column = 0 if day_column != 0 else None
    if label_column is None:
        gaps.append(f"budget table {table.index} has no label column")
        return [], gaps
    if rate_column is None:
        gaps.append(
            f"budget table {table.index} states days but no day rate; the "
            f"contracted value cannot be computed from it"
        )

    roles: list[dict] = []
    for row in table.rows[1:]:
        label = row[label_column].strip()
        if not label or contains_any(label, TOTAL_WORDS):
            continue
        days = parse_number(row[day_column]) if day_column is not None else None
        rate = parse_number(row[rate_column]) if rate_column is not None else None
        if days is None:
            gaps.append(f"row {label!r} states no number of days")
            continue
        if rate is None:
            gaps.append(f"row {label!r} states {days} days but no day rate")
        roles.append({
            "code": _slug(label),
            "label": label,
            "days": days,
            "day_rate": rate if rate is not None else 0.0,
            "covers": "",
        })

    if not roles:
        gaps.append(
            f"budget table {table.index} priced no resource line that could be "
            f"read as contracted days"
        )
    return roles, gaps


def _slug(label: str) -> str:
    flat = normalise(label)
    flat = re.sub(r"[^a-z0-9]+", "-", flat).strip("-")
    return (flat or "role")[:32]


def read_buckets(tables, lines, role_codes: list[str]) -> tuple[list[dict], list[str]]:
    """Tranches the contract splits delivery into, with any days proposed."""
    gaps: list[str] = []
    found: list[dict] = []
    seen: set[str] = set()

    pattern = re.compile(
        r"(?P<word>%s)\s*(?P<code>[0-9]+|[ivx]+)\b[\s:.\u2013-]*(?P<label>[^.;]{0,90})"
        % "|".join(re.escape(normalise(word)) for word in BUCKET_WORDS),
        re.IGNORECASE,
    )
    for line in lines:
        for match in pattern.finditer(normalise(line)):
            code = match.group("code")
            if code in seen:
                continue
            seen.add(code)
            label = match.group("label").strip(" -–:;,")
            found.append({
                "code": code,
                "label": label.capitalize() if label else f"Tranche {code}",
                "draws_on": role_codes[0] if role_codes else "",
                "buys": "",
                "window": "",
                "days_proposed": None,
            })

    if not found:
        gaps.append(
            "no tranches, buckets or phases named: confirm whether the contract "
            "splits delivery, and how many days each split was proposed at"
        )
    else:
        gaps.append(
            f"{len(found)} tranche(s) named but none carries a day split; ask "
            f"the supplier for an estimate against every one in session one, "
            f"not only the one starting now"
        )
    if len(role_codes) > 1 and found:
        gaps.append(
            f"every tranche is attributed to role {role_codes[0]!r}; confirm "
            f"which role each one draws on ({', '.join(role_codes)})"
        )
    return found, gaps


def read_signature(lines) -> tuple[bool | None, list[str]]:
    """Signature status, or the gap that forces the question.

    An offer almost never states whether it was countersigned, so this usually
    returns a gap — which is the point. An unsigned contract means nothing can
    be committed in the session, and it usually means the first contractual
    deliverable has already slipped.
    """
    for line in lines:
        if contains_any(line, UNSIGNED_WORDS):
            return False, []
    for line in lines:
        if contains_any(line, SIGNED_WORDS):
            # The word appearing is not the same as the status being stated: a
            # signature block on the last page says nothing about whether
            # anybody signed it.
            return None, [
                f"the document mentions signature ({line.strip()[:60]!r}) but "
                f"does not state whether it was signed; confirm before the "
                f"session, because nothing can be committed against an "
                f"unsigned contract"
            ]
    return None, [
        "signature status is not stated in the document; confirm it before the "
        "session, because nothing can be committed against an unsigned contract "
        "and the first contractual deliverable has usually slipped"
    ]


def read_components(tables, lines) -> list[dict]:
    """Contracted components, as candidate items with no severity or lane yet.

    Deliberately thin. Severity, lane and protection are judgement calls made
    with Ane, not values a parser should guess: an item wrongly marked
    ``Client, content`` reads as free and is not.
    """
    items: list[dict] = []
    for table in tables:
        if is_budget_table(table):
            continue
        header = table.header()
        if not header or table.n_cols < 2:
            continue
        if not contains_any(" | ".join(header),
                            ("deliverable", "component", "activity", "task",
                             "livrable", "composante", "activite", "tache",
                             "entregable", "componente", "actividad", "tarea",
                             "livrabil", "componenta", "activitate", "sarcina",
                             "leistung", "komponente", "aufgabe", "arbeitspaket")):
            continue
        for index, row in enumerate(table.rows[1:], start=1):
            text = row[0].strip() or (row[1].strip() if table.n_cols > 1 else "")
            if not text or contains_any(text, TOTAL_WORDS):
                continue
            items.append({
                "ref": f"CT-{len(items) + 1:02d}",
                "area": table.header()[0].strip()[:40] or "Contract",
                "issue": text[:300],
                "good": "",
                "source": f"Contract, table {table.index} row {index}",
                "severity": "",
                "lane": "",
                "bucket": "",
                "protected": False,
                "note": "",
            })
    return items


def draft_spec(payload: DocumentPayload, *, supplier: str = "",
               contract: str = "", session: str = "Session 1") -> dict:
    """Assemble a draft spec plus the ``_gaps`` list that blocks ``build``."""
    gaps: list[str] = []
    roles, role_gaps = read_roles(payload.tables)
    gaps.extend(role_gaps)

    role_codes = [role["code"] for role in roles]
    buckets, bucket_gaps = read_buckets(payload.tables, payload.lines, role_codes)
    gaps.extend(bucket_gaps)

    signed, signature_gaps = read_signature(payload.lines)
    gaps.extend(signature_gaps)

    items = read_components(payload.tables, payload.lines)
    if items:
        gaps.append(
            f"{len(items)} contracted component(s) read as candidate items; set "
            f"a severity, a lane and any protected flag with Ane. A parser "
            f"cannot tell client content from supplier build, and an item "
            f"wrongly lane-marked reads as free when it is not"
        )
    if not supplier:
        gaps.append("supplier not named: pass --supplier")
    if not contract:
        gaps.append("contract not named: pass --contract")

    return {
        "supplier": supplier,
        "contract": contract,
        "source": Path(payload.path).name,
        "session": session,
        "signed": signed,
        "roles": roles,
        "buckets": buckets,
        "items": items,
        "session_date": "",
        "_gaps": gaps,
    }


# --------------------------------------------------------------------------
# Session artefacts — markdown is canonical, Word renders from it
# --------------------------------------------------------------------------

def _fmt(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)


def prep_brief(spec: KickoffSpec) -> str:
    """Internal brief. Ane reads this before the session, nobody else sees it."""
    lines = [
        f"# Prep: {spec.contract}, {spec.session}",
        "",
        f"**Supplier:** {spec.supplier}  ",
        f"**Session date:** {spec.session_date or 'to confirm'}  ",
        f"**Source:** {spec.source}",
        "",
        "## What has to come out of this session",
        "",
        "1. An agreed day split across every tranche, not only the one "
        "starting now.",
        "2. A decision against every candidate item.",
        "3. A written record of both, in the workbook.",
        "",
        "## Before anything else: is the contract signed?",
        "",
    ]
    if spec.signed:
        lines += [
            "Signed. Days agreed in this session can be committed. Confirm the "
            "start date and the first contractual deliverable against the "
            "schedule.",
        ]
    else:
        lines += [
            "**NOT SIGNED.** No expenditure can be committed. Everything agreed "
            "in this session is provisional, and the first contractual "
            "deliverable has probably slipped already. Put the signature date "
            "first on the agenda.",
        ]

    lines += ["", "## The budget you are working inside", "", "| Role | Days | Day rate | Value |",
              "|---|---|---|---|"]
    for role in spec.roles:
        lines.append(
            f"| {role.label} | {_fmt(role.days)} | "
            f"{role.day_rate:,.0f} {spec.currency} | "
            f"{role.value:,.0f} {spec.currency} |"
        )
    lines.append(
        f"| **Total** | **{_fmt(spec.contracted_days)}** | | "
        f"**{spec.contracted_value:,.0f} {spec.currency}** |"
    )

    if spec.buckets:
        lines += ["", "## What the contract proposed per tranche", "",
                  "| Tranche | Window | Days proposed | What it buys |",
                  "|---|---|---|---|"]
        for bucket in spec.buckets:
            proposed = _fmt(bucket.days_proposed) if bucket.estimated else "**not priced**"
            lines.append(
                f"| {bucket.code}. {bucket.label} | {bucket.window or '–'} | "
                f"{proposed} | {bucket.buys or '–'} |"
            )
        unpriced = [b.code for b in spec.buckets if not b.estimated]
        if unpriced:
            lines += [
                "",
                f"Tranche{'s' if len(unpriced) > 1 else ''} "
                f"{', '.join(unpriced)} carr{'y' if len(unpriced) > 1 else 'ies'} "
                f"no day estimate. Ask for one in this session. A tranche with "
                f"no estimate is not a tranche with no cost, and the remainder "
                f"of the budget is not free until it has one.",
            ]

    protected = protected_items(spec)
    lines += ["", "## Protected items", ""]
    if protected:
        lines.append(
            "These survive the cap. They are not candidates to trade against "
            "it. Say so before the trade-offs start, not after."
        )
        lines.append("")
        for item in protected:
            lines.append(f"- **{item.ref}** — {item.issue}"
                         + (f" ({item.note})" if item.note else ""))
    else:
        lines.append(
            "No item is marked protected. Check that deliberately: a list with "
            "no do-no-harm, credibility or compliance item on it is unusual, "
            "and an unmarked one gets traded away."
        )

    lines += [
        "",
        "## How to run the hour",
        "",
        "1. Signature status, then the day budget. Agree the cap **before** "
        "opening the item list. A list read first answers 'what fits' against "
        "the list instead of against the contract.",
        "2. Ask for estimates against every tranche, including the ones that "
        "start months from now.",
        "3. Walk the items. Ask for the estimate before saying what you want, "
        "so the number is not anchored.",
        "4. Split by lane as you go. Content the client owns costs the supplier "
        "almost nothing once handed over.",
        "5. Fill the Decision column live. It is the output.",
        "",
        "## What to watch for",
        "",
        "- An item list that grows in the session is normal. A cap that grows "
        "with it is the failure this whole pack exists to prevent.",
        "- 'We can probably fit that in' is an estimate. Write it down as one.",
        "- Anything agreed against an unsigned contract is provisional. Say so "
        "out loud, so nobody starts work on it.",
    ]
    return "\n".join(lines) + "\n"


def agenda(spec: KickoffSpec) -> str:
    """Sent to the supplier ahead of the session."""
    lines = [
        f"# {spec.contract} — {spec.session}",
        "",
        f"**With:** {spec.supplier}  ",
        f"**Date:** {spec.session_date or 'to confirm'}",
        "",
        "The purpose of this session is to agree how the contracted days are "
        "split, and what enters the first batch of work. We will work from a "
        "shared workbook and fill it in as we go.",
        "",
        "## Agenda",
        "",
        "| # | Item | Why |",
        "|---|---|---|",
        "| 1 | Contract status and start date | Confirm what can be committed |",
        "| 2 | The day budget across all tranches | Agree the ceiling before the "
        "detail |",
        "| 3 | Estimates against every tranche | So later work is not priced "
        "after the budget is spent |",
        "| 4 | Item-by-item walkthrough | Confirm what is still open, and what "
        "it costs |",
        "| 5 | Decisions and next steps | Written down in the session |",
        "",
        "## What we would ask you to bring",
        "",
        "1. An hour estimate against each tranche, including the ones "
        "scheduled later. A rough range is more useful than no number.",
        "2. Confirmation of which items on the list are already resolved.",
        "3. Anything you consider out of scope, so we can route it rather than "
        "leave it ambiguous.",
        "",
        "## The budget we are working inside",
        "",
        "| Role | Contracted days |",
        "|---|---|",
    ]
    for role in spec.roles:
        lines.append(f"| {role.label} | {_fmt(role.days)} |")
    lines += [
        "",
        "These days cover the whole contract, not this batch. Time spent on "
        "the first tranche is time not available for the later ones, which is "
        "why we want estimates against all of them today.",
    ]
    return "\n".join(lines) + "\n"


def note_template(spec: KickoffSpec) -> str:
    """Filled in during or straight after the session."""
    lines = [
        f"# Session note: {spec.contract}, {spec.session}",
        "",
        f"**Supplier:** {spec.supplier}  ",
        f"**Date:** {spec.session_date or '[date]'}  ",
        "**Present:** [names]",
        "",
        "## Decisions",
        "",
        "| Decision | Why | Owner | By when |",
        "|---|---|---|---|",
        "| [what was agreed] | [the reason, in one line] | [who] | [date] |",
        "",
        "## Day budget agreed",
        "",
        "| Tranche | Days agreed | Running total | Remaining |",
        "|---|---|---|---|",
    ]
    for bucket in spec.buckets:
        lines.append(f"| {bucket.code}. {bucket.label} | | | |")
    lines += [
        "",
        "Copy the agreed figures from the workbook rather than retyping them, "
        "so the note and the workbook cannot disagree.",
        "",
        "## Items entering the first batch",
        "",
        "| Ref | Item | Lane | Est. hours |",
        "|---|---|---|---|",
        "| | | | |",
        "",
        "## Deferred, with the reason",
        "",
        "| Ref | Item | Deferred to | Why |",
        "|---|---|---|---|",
        "| | | | |",
        "",
        "## Open questions",
        "",
        "1. [question, owner, by when]",
        "",
        "## What to check before the next session",
        "",
        "1. Did the agreed days stay inside the cap once everything was "
        "entered?",
        "2. Did any tranche end the session still unpriced?",
        "3. Was anything committed against an unsigned contract?",
    ]
    return "\n".join(lines) + "\n"


ARTEFACTS = {
    "PREP-brief.md": prep_brief,
    "AGENDA-to-supplier.md": agenda,
    "NOTE-template.md": note_template,
}


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def cmd_read(args: argparse.Namespace) -> int:
    payload = load_document(args.source)
    spec = draft_spec(
        payload,
        supplier=args.supplier or "",
        contract=args.contract or "",
        session=args.session,
    )

    print(f"Read {Path(payload.path).name}: {len(payload.tables)} tables, "
          f"{len(payload.lines)} text blocks")
    print()
    if spec["roles"]:
        print("Contracted roles")
        for role in spec["roles"]:
            rate = (f"{role['day_rate']:,.0f}" if role["day_rate"]
                    else "NO RATE STATED")
            print(f"  {role['label']}: {_fmt(role['days'])} days at {rate}")
    else:
        print("Contracted roles: none found")
    print()
    print(f"Tranches: {len(spec['buckets'])}")
    for bucket in spec["buckets"]:
        print(f"  {bucket['code']}. {bucket['label']}")
    print()
    print(f"Candidate items: {len(spec['items'])}")
    print(f"Signature status: "
          f"{'signed' if spec['signed'] else 'NOT SIGNED' if spec['signed'] is False else 'not stated'}")
    print()
    print(f"GAPS ({len(spec['_gaps'])}) — take these to Ane, never fill one:")
    for gap in spec["_gaps"]:
        print(f"  - {gap}")

    out = Path(args.out)
    out.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    print()
    print(f"Draft spec written: {out}")
    print("build refuses while _gaps is present. Resolve them with Ane, then "
          "delete the list.")
    return 0


def _load_spec(path: str | Path) -> KickoffSpec:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "_gaps" in data:
        gaps = data["_gaps"]
        raise SystemExit(
            f"refusing to build: the spec still carries {len(gaps)} unresolved "
            f"gap(s).\n"
            + "\n".join(f"  - {gap}" for gap in gaps)
            + "\n\nResolve each with Ane and delete _gaps. Deleting it without "
              "resolving them does not help: validate_spec refuses a real hole "
              "afterwards anyway."
        )
    try:
        return spec_from_dict(data)
    except UnstatedInSource as exc:
        # A hole the source never filled, surviving after _gaps was deleted.
        # This is a question for Ane, not a bug, so say which.
        raise SystemExit(
            f"the spec is still missing something the contract has to state:\n"
            f"  {exc}\n\nGo back to the contract or ask the supplier. Do not "
            f"read the value off a similar contract."
        ) from exc


def cmd_build(args: argparse.Namespace) -> int:
    from ane_package.reporting.markdown_docx import render_markdown_file

    spec = _load_spec(args.spec)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    workbook = out / f"{_slug(spec.contract)}-kickoff.xlsx"
    if workbook.exists() and not args.force:
        raise SystemExit(
            f"refusing to overwrite {workbook}.\nOnce this workbook has been "
            f"used in a session the estimates and decisions in it exist nowhere "
            f"else. Edit it in place, or pass --force if it is genuinely "
            f"untouched."
        )
    build_kickoff_workbook(spec, workbook)
    print(f"workbook: {workbook}")

    written: list[str] = []
    for name, builder in ARTEFACTS.items():
        md_path = out / name
        if md_path.exists() and not args.force:
            print(f"kept (already exists, not overwritten): {md_path}")
        else:
            md_path.write_text(builder(spec), encoding="utf-8")
        report = render_markdown_file(md_path)
        written.append(report.output_path)
        status = "clean" if report.clean else f"{len(report.unsupported)} unsupported"
        print(f"  {md_path.name} -> {Path(report.output_path).name} ({status})")
        for item in report.unsupported:
            print(f"      {item}")

    _report_contract_arithmetic(spec)

    print()
    print("Markdown is canonical. Edit the .md and re-run build to re-render "
          "the .docx; never edit the .docx and expect it to survive.")
    return 0


def _report_contract_arithmetic(spec: KickoffSpec) -> None:
    """Does the contract's own proposal fit inside the contract's own ceiling?

    Worth asking before the session rather than during it. A contract whose
    proposed splits already exceed the days it bought has a problem no session
    can negotiate away, and finding that out while drafting the agenda is
    considerably cheaper than finding it out in the room.
    """
    proposed = {
        bucket.code: bucket.days_proposed
        for bucket in spec.buckets if bucket.estimated
    }
    if not proposed:
        print()
        print("The contract proposes no day split at all. Every tranche is an "
              "open question for the session.")
        return

    print()
    print("Against the contract's own proposed split:")
    for code, line in budget_status(spec, proposed).items():
        if not spec.buckets_for(code):
            continue
        print(f"  {line['label']}: {line['verdict']}")
    for signal in over_commitment_signal(spec, proposed):
        print(f"  ! {signal['message']}")


def cmd_verify(args: argparse.Namespace) -> int:
    """Drive the workbook through Excel and check what it actually computes."""
    from ane_package.officeops import excelcom

    spec = spec_from_dict(
        {k: v for k, v in
         json.loads(Path(args.spec).read_text(encoding="utf-8")).items()
         if k != "_gaps"}
    )
    target = Path(args.pack)
    workbook = target if target.suffix == ".xlsx" else (
        target / f"{_slug(spec.contract)}-kickoff.xlsx"
    )
    if not workbook.exists():
        raise SystemExit(f"no workbook at {workbook}; run build first")

    # Verification runs on a copy, so sample numbers never land in a live
    # contract record.
    scratch = workbook.with_name(workbook.stem + "--verify.xlsx")
    shutil.copy2(workbook, scratch)

    sample = {}
    for index, bucket in enumerate(spec.buckets):
        sample[bucket.code] = 1.0 + index * 0.5

    expected_status = budget_status(spec, sample)
    expected_rows = allocation(spec, sample)

    payload = {
        "writes": _budget_writes(spec, sample),
        "reads": _budget_reads(spec),
    }
    try:
        result = excelcom.apply_com(scratch, payload, _VERIFY_BODY, backup=False)
    except Exception as exc:  # noqa: BLE001
        print(f"NOT VERIFIED: Excel was not available or the run failed ({exc})")
        print("Report this workbook as unverified. Do not present it as checked.")
        scratch.unlink(missing_ok=True)
        return 2

    failures: list[str] = []
    for key, want in _expected_reads(spec, expected_rows, expected_status).items():
        got = result.get(key)
        if got is None:
            failures.append(f"{key}: Excel returned nothing")
        elif abs(float(got) - float(want)) > 0.005:
            failures.append(f"{key}: Excel computed {got}, the engine says {want}")

    errors = [key for key, value in result.items()
              if isinstance(value, str) and value.startswith("#")]
    if errors:
        failures.append(f"formula-error cells: {', '.join(errors)}")

    scratch.unlink(missing_ok=True)
    if failures:
        print(f"VERIFICATION FAILED ({len(failures)}):")
        for line in failures:
            print(f"  - {line}")
        return 1
    print(f"verified: {len(result)} computed cells agree with the engine, "
          f"zero formula errors")
    return 0


# PowerShell body for `verify`. Runs with $xl, $wb and $p in scope and reports
# into $result; the skeleton owns opening, saving and releasing.
#
# [double] on every write is not decoration. PowerShell deserialises a JSON
# number as System.Decimal, Range.Value2 refuses to cast it, and the COM error
# names String — which reads as a payload mismatch and sends you looking in the
# wrong place. Found on the live Excel run of 2026-08-04.
_VERIFY_BODY = """
foreach ($w in $p.writes) {
    $ws = $wb.Worksheets.Item($w.sheet)
    $ws.Range($w.cell).Value2 = [double]$w.value
}
$xl.CalculateFullRebuild()
foreach ($r in $p.reads) {
    $ws = $wb.Worksheets.Item($r.sheet)
    $v = $ws.Range($r.cell).Value2
    if ($null -eq $v) { $result[$r.key] = $null }
    else { $result[$r.key] = $v }
}
"""


def _budget_writes(spec: KickoffSpec, sample: dict[str, float]) -> list[dict]:
    """Sample day figures, addressed by the layout the builder wrote."""
    writes = []
    for role_index, role in enumerate(spec.roles):
        for index, bucket in enumerate(spec.buckets_for(role.code)):
            writes.append({
                "sheet": "01 Day budget",
                "cell": f"D{_bucket_row(spec, role.code, index)}",
                "value": float(sample.get(bucket.code, 0.0)),
            })
    return writes


def _bucket_row(spec: KickoffSpec, role_code: str, index: int) -> int:
    """Excel row of one bucket on the day-budget sheet.

    Mirrors the builder's layout: a title block, then per role a heading row, a
    header row, one row per bucket, then three summary rows and a blank.
    """
    row = 4  # title (1), subtitle (2), blank (3), first content row is 4
    for role in spec.roles:
        buckets = spec.buckets_for(role.code)
        row += 1  # role heading
        if not buckets:
            row += 2
            continue
        row += 1  # column headers
        if role.code == role_code:
            return row + index
        row += len(buckets) + 4
    raise KeyError(role_code)


def _budget_reads(spec: KickoffSpec) -> list[dict]:
    reads = []
    for role in spec.roles:
        buckets = spec.buckets_for(role.code)
        for index, bucket in enumerate(buckets):
            row = _bucket_row(spec, role.code, index)
            reads.append({"sheet": "01 Day budget", "cell": f"E{row}",
                          "key": f"hours:{bucket.code}"})
            reads.append({"sheet": "01 Day budget", "cell": f"G{row}",
                          "key": f"value:{bucket.code}"})
        if buckets:
            total_row = _bucket_row(spec, role.code, len(buckets))
            reads.append({"sheet": "01 Day budget", "cell": f"D{total_row}",
                          "key": f"committed:{role.code}"})
            reads.append({"sheet": "01 Day budget", "cell": f"D{total_row + 2}",
                          "key": f"remaining:{role.code}"})
    return reads


def _expected_reads(spec: KickoffSpec, rows: list[dict],
                    status: dict[str, dict]) -> dict[str, float]:
    expected: dict[str, float] = {}
    for row in rows:
        if row["hours_agreed"] is not None:
            expected[f"hours:{row['code']}"] = row["hours_agreed"]
            expected[f"value:{row['code']}"] = row["value"]
    for code, line in status.items():
        if spec.buckets_for(code):
            expected[f"committed:{code}"] = line["committed_days"]
            expected[f"remaining:{code}"] = line["remaining_days"]
    return expected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="contract_kickoff",
        description="Prepare the first working session of a delivery contract.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    read = sub.add_parser("read", help="read the offer and report what it states")
    read.add_argument("source", help="the agreed offer or contract (.docx)")
    read.add_argument("--out", default="kickoff-spec.json")
    read.add_argument("--supplier", default="")
    read.add_argument("--contract", default="")
    read.add_argument("--session", default="Session 1")
    read.set_defaults(func=cmd_read)

    build = sub.add_parser("build", help="build the session pack from a spec")
    build.add_argument("spec")
    build.add_argument("--out", required=True)
    build.add_argument("--force", action="store_true",
                       help="overwrite an existing pack (refuses by default)")
    build.set_defaults(func=cmd_build)

    verify = sub.add_parser("verify", help="check the workbook through Excel")
    verify.add_argument("pack")
    verify.add_argument("--spec", required=True)
    verify.set_defaults(func=cmd_verify)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
