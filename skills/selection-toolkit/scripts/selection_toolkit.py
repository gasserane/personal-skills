"""Thin command-line driver over ``ane_package`` for building a selection toolkit.

The line Waves 2 to 4 settled and this file holds: **anything that opens an
Office file belongs in the module.** Exactly two calls here open a document —
:func:`read_source` reads the ToR, and ``verify`` drives Excel through COM.
Finding the criteria table among the others, parsing a weight out of "35 points",
recognising a threshold sentence and assembling the spec are text logic, so they
live here and are tested here.

The rule the whole driver exists to serve: **nothing is invented.** ``read``
never fills a gap. Where the source does not state a weight, a threshold or a
date, the draft spec carries ``null`` and the gap is listed in ``_gaps`` with the
sentence that was inspected. Ane resolves those, and ``build`` refuses through
``validate_spec`` if any survive. A default weight is indistinguishable from a
published one once it is in a cell, and the panel scores against it for six weeks
without noticing.

Usage:
    python selection_toolkit.py read   TOR.docx --out SPEC.json [--json]
    python selection_toolkit.py build  SPEC.json --out DIR [--force]
    python selection_toolkit.py verify DIR [--keep]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
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


def _speak_utf8() -> None:
    """Print ToR text without dying on the console encoding.

    A Windows console is cp1252 by default and a ToR carries Chisinau with its
    diacritics, curly quotes and euro signs. Wave 3 shipped a UnicodeEncodeError
    that all 32 unit tests missed, because an in-process call never touches the
    console encoding. This driver echoes criteria labels straight from the
    source, so it hits the same wall unless it is reconfigured here.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


_speak_utf8()

from ane_package.officeops import DocTable, document_tables, extract_text  # noqa: E402
from ane_package.reporting.selection_toolkit import (  # noqa: E402
    SHEETS,
    Criterion,
    SelectionSpec,
    UnstatedInSource,
    build_master_workbook,
    build_scorer_workbook,
    spec_from_dict,
    spec_to_dict,
    validate_spec,
)

# ---------------------------------------------------------------------------
# Vocabulary
#
# Every guard here is written in each language Ane reviews procurement in, not
# only English. This has now bitten three times -- the marginalia date guard,
# the deck slide numbering, and it would bite here hardest of all: an
# English-only header match on a French ToR finds no criteria table, falls
# through to "the source published none", and the gap it reports is an artefact
# of the parser rather than a fact about the document.
# ---------------------------------------------------------------------------

CRITERION_WORDS = (
    "criterion", "criteria", "critere", "criteres", "criterio", "criterios",
    "criteriu", "criterii", "kriterium", "kriterien", "award criteria",
    "attribution", "adjudicacion", "atribuire", "critere d attribution",
)
POINTS_WORDS = (
    "point", "points", "puntos", "punte", "puncte", "punkte", "punkt",
    "score", "scoring", "note", "notation", "puntuacion", "punctaj",
    "weight", "weighting", "ponderation", "ponderacion", "pondere",
    "max", "maximum", "maxima", "maxim", "total",
)
THRESHOLD_WORDS = (
    "threshold", "seuil", "umbral", "prag", "schwelle",
    "minimum", "minimal", "minim", "minimo", "pass mark", "qualify",
    "qualification", "qualifying", "eliminatoire", "eliminatoriu",
    # The commonest phrasing of all carries none of the words above:
    # "proposals scoring below 63 points will not proceed". Safe to include
    # because a candidate sentence still yields nothing unless a number sits
    # against 'points' or a '%' -- "at least 2 references" is picked up as a
    # candidate and then correctly produces no reading.
    "below", "at least", "en dessous", "au moins", "inferieur",
    "al menos", "por debajo", "cel putin", "sub ",
)
FINANCIAL_WORDS = (
    "financial", "financiere", "financiar", "financiero", "price", "prix",
    "pret", "precio", "cost", "budget", "fee", "honoraires",
)


def _fold(text: str) -> str:
    """Lower-case and strip accents, so 'Critère' matches 'critere'.

    Accent-blind on purpose. A ToR is as likely to write ``Critere`` as
    ``Critère`` depending on who typed it, and a match that depends on which is
    a match that fails silently on half the documents.
    """
    stripped = unicodedata.normalize("NFKD", text)
    stripped = "".join(char for char in stripped if not unicodedata.combining(char))
    return stripped.lower().strip()


def _has_any(text: str, words: tuple[str, ...]) -> bool:
    folded = _fold(text)
    return any(word in folded for word in words)


NUMBER = re.compile(r"(\d+(?:[.,]\d+)?)")


def parse_points(text: str) -> float | None:
    """Pull a weight out of '35', '35 points', 'up to 35%', '12,5 puncte'.

    Returns ``None`` rather than a guess when the cell holds no number. That
    ``None`` becomes a reported gap, which is the entire contract of this driver.
    """
    if not text or not text.strip():
        return None
    match = NUMBER.search(text.replace(" ", " "))
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", "."))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# The file boundary: exactly one function here opens the document
# ---------------------------------------------------------------------------

def read_source(path: Path | str) -> tuple[list[DocTable], list[str]]:
    """Open the ToR once and hand back objects. The only reader in this file.

    Everything downstream takes these two lists and opens nothing, which is why
    the parsing below can be tested with a literal grid and no fixture document.
    """
    path = Path(path)
    return document_tables(path), list(extract_text(path))


# ---------------------------------------------------------------------------
# Pure logic over what read_source returned
# ---------------------------------------------------------------------------

def score_criteria_table(table: DocTable) -> int:
    """How much this table looks like the published award criteria.

    A ToR carries several tables — milestones, budget, contacts, deliverables —
    and picking the wrong one produces a plausible criteria list with the wrong
    numbers. Scored rather than first-match, and the score is reported, so a weak
    winner is visible instead of silently authoritative.
    """
    header = table.header()
    if not header or table.n_rows < 2:
        return 0

    score = 0
    joined = " | ".join(header)
    if _has_any(joined, CRITERION_WORDS):
        score += 3
    if _has_any(joined, POINTS_WORDS):
        score += 3

    # A criteria table's points column is mostly numbers. A milestones table's
    # date column is not, and this is what separates them when both headers
    # happen to carry a matching word.
    for index in range(table.n_cols):
        column = table.column(index)[1:]
        if not column:
            continue
        numeric = sum(1 for cell in column if parse_points(cell) is not None)
        if numeric >= max(2, len(column) // 2):
            score += 2
            break

    if any(_has_any(cell, THRESHOLD_WORDS) for cell in header):
        score += 1
    return score


def find_criteria_table(tables: list[DocTable]) -> tuple[DocTable | None, int]:
    """The best-scoring candidate and its score. ``None`` when nothing scores."""
    best, best_score = None, 0
    for table in tables:
        score = score_criteria_table(table)
        if score > best_score:
            best, best_score = table, score
    return best, best_score


def _column_for(table: DocTable, words: tuple[str, ...]) -> int | None:
    for index, cell in enumerate(table.header()):
        if _has_any(cell, words):
            return index
    return None


CODE_CELL = re.compile(r"[A-Za-z]{0,2}\.?\s?\d{1,2}\.?")


def is_code_column(table: DocTable, index: int) -> bool:
    """Whether a column holds criterion codes rather than criterion text.

    The trap this closes: a ToR heading its columns ``Criterion | Description |
    Max points`` puts ``C1`` under "Criterion" and the actual criterion under
    "Description". Matching the header word alone labels every criterion "C1",
    "C2", and the workbook ships with column headers that tell a scorer nothing.
    Nothing raises, and the numbers are all correct, so a review passes it.
    """
    body = [cell.strip() for cell in table.column(index)[1:] if cell.strip()]
    if not body:
        return False
    coded = sum(1 for cell in body if CODE_CELL.fullmatch(cell))
    return coded >= max(1, int(len(body) * 0.6))


def _widest_text_column(table: DocTable, exclude: set[int]) -> int | None:
    widths = [
        (sum(len(cell) for cell in table.column(index)[1:]), index)
        for index in range(table.n_cols)
        if index not in exclude
    ]
    return max(widths)[1] if widths else None


def parse_criteria(table: DocTable) -> tuple[list[dict], list[str]]:
    """Criteria and the gaps found, from a candidate table.

    Never drops a row it cannot fully read. A criterion whose weight the ToR left
    blank is returned with ``max_points: None`` and a gap beside it, because
    dropping it would quietly shorten the criteria list and rebalance the whole
    award.
    """
    gaps: list[str] = []
    header = table.header()
    if not header:
        return [], [f"{table.where}: the table has no header row"]

    points_col = _column_for(table, POINTS_WORDS)
    named = _column_for(table, CRITERION_WORDS)
    code_col: int | None = None
    label_col: int | None = None

    if named is not None and is_code_column(table, named):
        # 'Criterion' heads the codes and the criterion itself is elsewhere.
        code_col = named
        label_col = _widest_text_column(table, {points_col, code_col} - {None})
    elif named is not None:
        label_col = named
    else:
        # Many ToRs head the criteria column 'Description', 'Item' or nothing.
        label_col = _widest_text_column(table, {points_col} - {None})
        if label_col is not None:
            gaps.append(
                f"{table.where}: no column headed with a criterion word; read "
                f"column {label_col + 1} ('{header[label_col]}') as the criteria. "
                "Confirm."
            )

    if label_col is None:
        return [], [f"{table.where}: no column reads as the criteria text"]
    if code_col is None and 0 not in (points_col, label_col) and is_code_column(table, 0):
        code_col = 0

    if points_col is None:
        gaps.append(
            f"{table.where}: no column headed with a points or weighting word; "
            "the maximum for every criterion is unstated."
        )

    criteria: list[dict] = []
    for row_index, row in enumerate(table.rows[1:], start=1):
        label = row[label_col].strip()
        if not label:
            continue
        # A totals row is not a criterion, and adding it as one doubles the
        # available marks.
        if _fold(label) in ("total", "totals", "sum", "totaal", "totalul", "total general"):
            continue

        points = parse_points(row[points_col]) if points_col is not None else None
        # An explicit code in the source wins over a generated one, so the
        # workbook's column headers match the ToR the applicants read.
        code = f"C{len(criteria) + 1}"
        if code_col is not None:
            published = row[code_col].strip().rstrip(".").replace(" ", "")
            if published:
                code = published

        if points is None:
            gaps.append(
                f"{table.where} row {row_index + 1} ('{label[:60]}'): no maximum "
                "points stated. The ToR must publish the weight."
            )
        criteria.append({
            "code": code,
            "label": label,
            "max_points": points,
            "gloss": "",
        })

    if not criteria:
        gaps.append(f"{table.where}: no criteria rows could be read")
    return criteria, gaps


def find_threshold(paragraphs: list[str], technical_max: float | None) -> tuple[float | None, list[str]]:
    """A qualification threshold, or the sentences that mention one.

    Returns ``None`` and the candidate sentences rather than a number whenever
    the reading is not unambiguous. A threshold is the single number that decides
    who stays in the process; inferring it from "at least 70%" without Ane
    confirming what it is 70% of is exactly the failure this driver refuses.
    """
    candidates = [line for line in paragraphs if _has_any(line, THRESHOLD_WORDS)]
    if not candidates:
        return None, ["No sentence in the ToR mentions a qualification threshold."]

    readings: list[tuple[float, str]] = []
    for line in candidates:
        percent = re.search(r"(\d{1,3}(?:[.,]\d+)?)\s*%", line)
        if percent and technical_max:
            value = float(percent.group(1).replace(",", ".")) / 100 * technical_max
            # Round before comparing. 70% of 90 is 62.99999999999999 in binary
            # floating point, and two sentences saying the same thing would
            # otherwise read as two different thresholds and be reported as an
            # ambiguity that is not there.
            readings.append((round(value, 2), line.strip()))
            continue
        points = re.search(
            r"(\d{1,3}(?:[.,]\d+)?)\s*(?:points?|puncte|puntos|punkte|marks?)", line, re.I
        )
        if points:
            readings.append((float(points.group(1).replace(",", ".")), line.strip()))

    unique = sorted({value for value, _ in readings})
    if len(unique) == 1:
        return unique[0], []
    if not unique:
        return None, [
            "Threshold sentences found but no number could be read from them:"
        ] + [f"  - {line}" for line in candidates[:4]]
    return None, [
        f"More than one possible threshold ({', '.join(str(v) for v in unique)}). "
        "Confirm which applies:"
    ] + [f"  - {line}" for _, line in readings[:4]]


def find_financial_max(paragraphs: list[str], tables: list[DocTable]) -> tuple[float | None, list[str]]:
    """Points allotted to price, if the ToR states them."""
    for line in paragraphs:
        if not _has_any(line, FINANCIAL_WORDS):
            continue
        match = re.search(
            r"(\d{1,3}(?:[.,]\d+)?)\s*(?:points?|puncte|puntos|punkte|marks?|%)", line, re.I
        )
        if match:
            return float(match.group(1).replace(",", ".")), []
    return None, [
        "No sentence states how many points the financial proposal carries. If "
        "there is no financial stage, drop 'financial' from stages."
    ]


DATE_PATTERNS = (
    re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
    re.compile(r"\b(\d{1,2}\s+\w+\s+20\d{2})\b"),
    re.compile(r"\b(\d{1,2}[./]\d{1,2}[./]20\d{2})\b"),
)


def find_key_dates(paragraphs: list[str], tables: list[DocTable]) -> list[list[str]]:
    """Milestone and date pairs, from any table that reads like a schedule."""
    dates: list[list[str]] = []
    for table in tables:
        header = " | ".join(table.header())
        if not re.search(r"date|deadline|milestone|calendar|termen|fecha|echeance",
                         _fold(header)):
            continue
        for row in table.rows[1:]:
            cells = [cell for cell in row if cell.strip()]
            if len(cells) < 2:
                continue
            for pattern in DATE_PATTERNS:
                match = pattern.search(row[-1]) or pattern.search(" ".join(cells))
                if match:
                    dates.append([cells[0][:90], match.group(1)])
                    break
    return dates


def draft_spec(tables: list[DocTable], paragraphs: list[str], source: str) -> dict:
    """Assemble a draft spec plus the list of everything the ToR did not state."""
    table, confidence = find_criteria_table(tables)
    gaps: list[str] = []

    if table is None:
        criteria: list[dict] = []
        gaps.append(
            "No table in this document reads like published award criteria. "
            "Either the ToR states them in prose, or this is not the right file."
        )
    else:
        criteria, table_gaps = parse_criteria(table)
        gaps.extend(table_gaps)
        if confidence < 6:
            gaps.append(
                f"Criteria read from {table.where} on a weak match (score "
                f"{confidence} of 9). Check this is the award-criteria table and "
                "not another one."
            )

    stated = [item["max_points"] for item in criteria if item["max_points"] is not None]
    technical_max = sum(stated) if stated and len(stated) == len(criteria) else None

    threshold, threshold_gaps = find_threshold(paragraphs, technical_max)
    gaps.extend(threshold_gaps)
    financial_max, financial_gaps = find_financial_max(paragraphs, tables)
    gaps.extend(financial_gaps)

    return {
        "mode": "procurement",
        "title": "",
        "source": source,
        "criteria": criteria,
        "panel": [],
        "threshold": threshold,
        "financial_max": financial_max or 0.0,
        "compliance_checks": [],
        "gates": [],
        "key_dates": find_key_dates(paragraphs, tables),
        "stages": ["compliance", "technical", "financial"],
        "n_applicants": 20,
        "_gaps": gaps + [
            "Panel roster is not in the ToR. Name who scores, and who administers.",
            "Compliance checks: confirm the submission requirements to check "
            "pass/fail at stage 1.",
            "Title: what this selection is called on the dashboard.",
        ],
    }


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_read(args) -> int:
    path = Path(args.tor)
    tables, paragraphs = read_source(path)
    draft = draft_spec(tables, paragraphs, source=args.source or path.name)

    out = Path(args.out)
    out.write_text(json.dumps(draft, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.json:
        print(json.dumps(draft, indent=2, ensure_ascii=False))
        return 0

    print(f"Read {path.name}: {len(tables)} tables, {len(paragraphs)} paragraphs.")
    print(f"Draft spec written to {out}\n")
    print(f"Criteria found: {len(draft['criteria'])}")
    for item in draft["criteria"]:
        points = item["max_points"]
        shown = "NOT STATED" if points is None else str(points)
        print(f"  {item['code']}  {item['label'][:64]}  [{shown}]")
    print(f"\nGaps to resolve before building ({len(draft['_gaps'])}):")
    for gap in draft["_gaps"]:
        print(f"  - {gap}")
    print("\nNothing above was invented. Fill the nulls in the spec file, remove "
          "_gaps, then run `build`.")
    return 0


def _load_spec(path: Path) -> SelectionSpec:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    gaps = data.pop("_gaps", [])
    if gaps:
        raise UnstatedInSource(
            f"the spec still lists {len(gaps)} unresolved gap(s); resolve them "
            "and delete the _gaps key:\n  - " + "\n  - ".join(str(g) for g in gaps)
        )
    return spec_from_dict(data)


def cmd_build(args) -> int:
    spec = _load_spec(Path(args.spec))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    master = out / "selection-master.xlsx"
    # Re-running a generator is overwriting. Once this workbook has been
    # distributed or scored in, the copy on disk holds real panel data that
    # exists nowhere else.
    existing = [p for p in [master] if p.exists()]
    existing += [p for p in out.glob("scorer-*.xlsx")]
    if existing and not args.force:
        print("Refusing to overwrite an existing toolkit:")
        for path in existing:
            print(f"  {path}")
        print("\nIf the panel has scored in these, edit them in place instead. "
              "Pass --force only if you are certain they are empty.")
        return 1

    build_master_workbook(spec, master)
    written = [master]
    for scorer in spec.panel:
        safe = re.sub(r"[^A-Za-z0-9]+", "-", scorer).strip("-").lower()
        path = out / f"scorer-{safe}.xlsx"
        build_scorer_workbook(spec, scorer, path)
        written.append(path)

    print(f"Built {len(written)} workbooks in {out}")
    for path in written:
        print(f"  {path.name}")
    print(f"\nCriteria: {len(spec.criteria)} worth {spec.technical_max} points."
          f" Threshold: {spec.threshold}."
          f" Financial: {spec.financial_max if spec.has_financial else 'no stage'}.")
    print("Run `verify` next: a workbook that looks right and calculates wrong is "
          "the failure mode here, and only execution catches it.")
    return 0


# ---------------------------------------------------------------------------
# Verification by execution
# ---------------------------------------------------------------------------

VERIFY_BODY = r"""
foreach ($w in $p.writes) {
  $ws = $wb.Worksheets.Item($w.sheet)
  $v = $w.value
  # PowerShell deserialises a JSON number as System.Decimal, and Range.Value2
  # refuses to cast Decimal to its Variant. The error names String, which reads
  # as a type mismatch in the payload rather than in the marshalling, so cast
  # explicitly here instead of trying to make the JSON produce a double.
  if ($v -is [string]) {
    $ws.Range($w.cell).Value2 = [string]$v
  } else {
    $ws.Range($w.cell).Value2 = [double]$v
  }
}
$xl.CalculateFullRebuild()
$values = @{}
foreach ($r in $p.reads) {
  $ws = $wb.Worksheets.Item($r.sheet)
  $values[$r.label] = $ws.Range($r.cell).Value2
}
$errors = New-Object System.Collections.ArrayList
foreach ($ws in $wb.Worksheets) {
  $cells = $null
  try { $cells = $ws.UsedRange.SpecialCells(-4123, 16) } catch { $cells = $null }
  if ($cells -ne $null) {
    foreach ($c in $cells) {
      [void]$errors.Add(@{ sheet = $ws.Name; cell = $c.Address(0,0) })
    }
  }
}
$result = @{ values = $values; errors = $errors }
"""


def verification_plan(spec: SelectionSpec) -> tuple[list[dict], list[dict], dict]:
    """Sample data to inject, cells to read back, and what they must equal.

    Computed in Python from the same rules the formulas were written to, so the
    assertion is independent of the formula strings. The point is to catch a
    workbook that looks right and calculates wrong, and reading a formula back
    would only prove it is the formula that was written.
    """
    from ane_package.reporting.selection_toolkit import (
        _cell, decide, financial_score, panel_mean, _inbox_row,
    )

    n_crit = len(spec.criteria)
    subjects = [
        {"name": "Alpha Consulting", "price": 20000.0, "offset": 0},
        {"name": "Beta Research", "price": 15000.0, "offset": 1},
    ]
    # Deliberately uneven: the second scorer leaves Beta unscored, so the run
    # exercises the blanks-are-absences rule rather than a tidy full grid.
    grid = {
        0: [[30, 28, 26, 32], [20, 22, 18, 21], [12, 10, 11, 13], [10, 12, 9, 11]],
        1: [[25, None, 27, 24], [15, None, 16, 14], [9, None, 10, 8], [8, None, 7, 9]],
    }

    writes: list[dict] = []
    for subject in subjects:
        row = 4 + subject["offset"]
        writes.append({"sheet": SHEETS["applicants"], "cell": _cell(row, 1),
                       "value": subject["name"]})
        writes.append({"sheet": SHEETS["applicants"], "cell": _cell(row, 5),
                       "value": subject["price"]})

    for subject in subjects:
        offset = subject["offset"]
        for crit_index in range(n_crit):
            for scorer_index in range(len(spec.panel)):
                value = grid[offset][crit_index][scorer_index]
                if value is None:
                    continue
                writes.append({
                    "sheet": SHEETS["inbox"],
                    "cell": _cell(_inbox_row(spec, scorer_index, offset), 2 + crit_index),
                    "value": float(value),
                })

    expected: dict = {}
    means_by_subject = {}
    for subject in subjects:
        offset = subject["offset"]
        means = {}
        for crit_index, criterion in enumerate(spec.criteria):
            means[criterion.code] = panel_mean(grid[offset][crit_index])
        means_by_subject[offset] = means
        outcome = decide(spec, means)
        expected[f"total{offset}"] = outcome["total"]
        expected[f"qualified{offset}"] = (
            "Qualified" if outcome["qualified"] else "Below threshold"
        )
        scorer_totals = [
            sum(grid[offset][c][s] for c in range(n_crit))
            for s in range(len(spec.panel))
            if all(grid[offset][c][s] is not None for c in range(n_crit))
        ]
        expected[f"spread{offset}"] = (
            max(scorer_totals) - min(scorer_totals) if len(scorer_totals) >= 2 else None
        )

    reads: list[dict] = []
    total_col = 2 + n_crit
    for subject in subjects:
        offset = subject["offset"]
        row = 4 + offset
        reads.append({"label": f"total{offset}", "sheet": SHEETS["technical"],
                      "cell": _cell(row, total_col)})
        reads.append({"label": f"spread{offset}", "sheet": SHEETS["technical"],
                      "cell": _cell(row, total_col + 1)})
        reads.append({"label": f"qualified{offset}", "sheet": SHEETS["technical"],
                      "cell": _cell(row, total_col + 2)})

    if spec.has_financial:
        qualified_prices = [
            subject["price"] for subject in subjects
            if expected[f"qualified{subject['offset']}"] == "Qualified"
        ]
        cheapest = min(qualified_prices) if qualified_prices else None
        for subject in subjects:
            offset = subject["offset"]
            row = 4 + offset
            reads.append({"label": f"financial{offset}", "sheet": SHEETS["financial"],
                          "cell": _cell(row, 5)})
            reads.append({"label": f"combined{offset}", "sheet": SHEETS["financial"],
                          "cell": _cell(row, 7)})
            if cheapest and expected[f"qualified{offset}"] == "Qualified":
                score = financial_score(subject["price"], cheapest, spec.financial_max)
                expected[f"financial{offset}"] = score
                expected[f"combined{offset}"] = expected[f"total{offset}"] + score
            else:
                expected[f"financial{offset}"] = None
                expected[f"combined{offset}"] = None

    return writes, reads, expected


def _close(actual, wanted) -> bool:
    if wanted is None:
        return actual in (None, "", 0) or isinstance(actual, str)
    if isinstance(wanted, str):
        return str(actual).strip() == wanted
    try:
        return abs(float(actual) - float(wanted)) < 0.005
    except (TypeError, ValueError):
        return False


def cmd_verify(args) -> int:
    from ane_package.officeops import Checks, excelcom

    folder = Path(args.folder)
    master = folder / "selection-master.xlsx" if folder.is_dir() else folder
    if not master.exists():
        print(f"No workbook at {master}")
        return 1

    spec_path = Path(args.spec) if args.spec else None
    if spec_path is None:
        guess = (folder if folder.is_dir() else folder.parent) / "selection-spec.json"
        spec_path = guess if guess.exists() else None
    if spec_path is None:
        print("Need the spec to know what the numbers should be: pass --spec.")
        return 1
    spec = _load_spec(spec_path)

    # Verify on a copy. Injecting sample applicants into the workbook the panel
    # will actually use would leave test data in a live procurement record.
    scratch = Path(tempfile.mkdtemp(prefix="selection-verify-"))
    copy = scratch / "verify.xlsx"
    shutil.copy2(master, copy)

    writes, reads, expected = verification_plan(spec)
    try:
        outcome = excelcom.apply_com(
            str(copy), {"writes": writes, "reads": reads}, VERIFY_BODY,
            backup=False, timeout=600,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Could not drive Excel: {type(exc).__name__}: {exc}")
        print("\nThis check needs Excel on Windows. The workbook was NOT verified "
              "by execution; do not treat it as checked.")
        return 2

    values = (outcome or {}).get("values") or {}
    errors = (outcome or {}).get("errors") or []

    checks = Checks(title=f"selection toolkit: {master.name}")
    for label, wanted in sorted(expected.items()):
        actual = values.get(label)
        checks.check(
            _close(actual, wanted),
            f"{label}: Excel computed {actual!r}, engine says {wanted!r}",
        )
    checks.check(
        not errors,
        f"no formula error cells (found {len(errors)}"
        + (f", first at {errors[0].get('sheet')}!{errors[0].get('cell')}" if errors else "")
        + ")",
    )

    code = checks.report()
    if args.keep:
        print(f"verified copy kept at {copy}")
    else:
        shutil.rmtree(scratch, ignore_errors=True)
    return code


# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="selection_toolkit",
        description="Build the Excel toolkit that runs a selection.",
    )
    subs = parser.add_subparsers(dest="command", required=True)

    read = subs.add_parser("read", help="draft a spec from a published ToR")
    read.add_argument("tor")
    read.add_argument("--out", default="selection-spec.json")
    read.add_argument("--source", help="how the source should be cited in the workbook")
    read.add_argument("--json", action="store_true")
    read.set_defaults(func=cmd_read)

    build = subs.add_parser("build", help="write the master and scorer workbooks")
    build.add_argument("spec")
    build.add_argument("--out", required=True)
    build.add_argument("--force", action="store_true",
                       help="overwrite existing workbooks (discards panel data)")
    build.set_defaults(func=cmd_build)

    verify = subs.add_parser("verify", help="inject sample data and assert the maths")
    verify.add_argument("folder")
    verify.add_argument("--spec")
    verify.add_argument("--keep", action="store_true")
    verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
