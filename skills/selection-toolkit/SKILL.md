---
name: selection-toolkit
description: 'Build the Excel toolkit that runs a selection between a published ToR and the award: procurement mode (master workbook plus one scorer workbook per panel member) and appraisal mode (generic multi-criteria decision analysis), off one weighted scoring engine. Use for panel scoring set-up, scoring grids, evaluation workbooks, or any weighted multi-criteria appraisal. Distinct from tor-procurement (writes and grades the ToR), procurement-offer-review (analyses one incoming offer), donor-proposal-scoring (proposals IPPF sends out rather than receives), and accreditation-desk-review (MAs against IPPF standards).'
model: opus
---

# /selection-toolkit — the instrument the panel scores in

One job: a selection has to be run, and the panel needs the workbook that runs it. Between publication and award. `/tor-procurement` wrote the ToR and stopped; `procurement-offer-review` reads one offer once the bids are in. This builds what sits between them.

## The rule that governs everything here

**Nothing is invented.** Every criterion, every weight, every threshold, every date comes from the source document or is reported as a gap for Ane to resolve. A default weight is indistinguishable from a published one once it is in a cell, and the panel scores against it for six weeks without noticing. `validate_spec` refuses a spec with a hole in it, and `read` never fills one.

Two rules to carry into anything you write for a user of this skill:

1. **Scoring may only use criteria the source published.** A criterion the panel wishes had been published is a lesson for the next ToR, not a column in this workbook.
2. **Once distributed or scored in, these files are edited in place, never regenerated.** `build` refuses to overwrite an existing toolkit for exactly this reason. The scores in a returned scorer file exist nowhere else.

## Where the code lives

All Office work is in `ane_package`. This skill contributes judgement, not plumbing.

- `ane_package.reporting.selection_toolkit` — the spec, the scoring engine, both workbook builders.
- `ane_package.officeops.document_tables` — reads the ToR's tables as grids that keep their blanks.
- `scripts/selection_toolkit.py` — the driver: table scoring, weight parsing, threshold reading, spec assembly, verification.

The boundary, so it does not get relitigated: **anything that opens an Office file belongs in the module.** Exactly two calls in the driver open a document. Deciding which of a ToR's five tables is the award criteria, and pulling `35` out of `"up to 35 points"`, are text logic and live in the driver.

Read `references/officeops-excel-api.md` (in `office-repair`) before writing any Office code, and `references/modes.md` here for what each mode changes.

## Running it

### 1. Read the source

```bash
python scripts/selection_toolkit.py read "path/to/ToR.docx" --out selection-spec.json
```

Prints the criteria it found, the weight against each, and every gap. Take the gaps to Ane — they are the questions the ToR did not answer. Common ones: the panel roster (a ToR never names it), the compliance checks, the title, and an ambiguous threshold where the ToR says both "70%" and "60 points".

Never resolve a gap yourself. If the ToR does not state a weight, ask; do not read one off a similar procurement.

### 2. Fill the spec with Ane, then delete `_gaps`

The spec file is the audit trail for "why is this criterion worth 35". Keep it beside the workbooks. `build` refuses while `_gaps` is present, and `validate_spec` still refuses afterwards if a real value is missing — deleting the gap list does not smuggle a hole through.

Set `mode` to `appraisal` for a non-procurement comparison; see `references/modes.md`.

### 3. Build

```bash
python scripts/selection_toolkit.py build selection-spec.json --out "3 Selection toolkit"
```

Writes `selection-master.xlsx` plus `scorer-<name>.xlsx` per panel member. Separate files, never one shared workbook: independent scoring is the control that makes a panel mean worth computing, and a shared file removes it the moment the second person opens it.

### 4. Verify by execution — this is the part that earns the skill

```bash
python scripts/selection_toolkit.py verify "3 Selection toolkit" --spec selection-spec.json
```

Copies the workbook, injects sample applicants and scores through Excel COM, forces a full recalculation, and asserts the computed means, thresholds, financial scores and rankings against the same engine the formulas were written from — plus zero formula-error cells.

**A workbook that looks right and calculates wrong is the failure mode here, and only execution catches it.** Reading a formula back proves only that the formula you wrote is the formula you wrote. Verification runs on a copy, so sample data never lands in a live procurement record.

If Excel is unavailable the command exits 2 and says the workbook was not verified. Report that as unverified. Do not present an unverified workbook as checked.

### 5. Commit the output

The edit-preservation guard cannot see Excel COM or openpyxl writes, so it flags the emitted files as hand-edited. Commit them as the final step rather than leaving them dirty.

## What the master workbook holds

`00 DASHBOARD` (computed, type nothing), `01 Read me` (the running order), `02 Applicants`, `03 Questions log`, `04 Q&A to publish`, `05 Stage 1 Compliance`, `06 Score inbox` (paste returned scorer files here), `07 Stage 2 Technical` (panel means, spread, qualification), `08 Stage 3 Financial`, `09 Stage 4 Interview`, `10 Conflict of interest`, `11 Decision log`, `12 Applicant feedback`, `98 REF` (the published parameters, so the audit trail travels with the file).

Stages the source does not define get no sheet.

## Things that will bite

1. **Blanks are absences, not zeros.** A reserve panellist who never scored must not drag a mean down by a third. `panel_mean` ignores blanks and the AVERAGE formulas are written to match. Never "clean" a scorer file by filling empties with 0.
2. **Every computed cell guards its own blank.** A workbook handed over on day one is empty, and a sheet of `#DIV/0!` reads as broken rather than as waiting. It is also what makes "zero formula-error cells" a real check rather than a tautology.
3. **Order runs compliance, then gates, then scoring.** Scoring a non-compliant bid and excluding it afterwards is how a panel talks itself into an exception.
4. **A wide spread is a signal, not an error.** The workbook shades a spread at or above the trigger. The panel discusses it; nobody averages it away quietly.
5. **The ToR may not be in English.** Header matching, threshold sentences and date parsing are written accent-blind across English, French, Spanish, Romanian and German. An English-only guard on a French ToR finds no criteria table and reports a gap that is an artefact of the parser rather than a fact about the document. This has now bitten three times across Waves 4 and 5.
6. **The column headed "Criterion" often holds the codes.** The criterion itself sits under "Description". Matching the header word alone labels every criterion "C1", "C2" — correct numbers, useless headers, and nothing raises. `is_code_column` closes it; do not remove the check.
7. **Prices are read from `02 Applicants`,** so correct a price there and every dependent score follows. Overtyping the financial sheet does nothing: it is protected.

## Where this does not go

It does not write the ToR (`/tor-procurement`), analyse a single incoming offer (`procurement-offer-review`), score proposals IPPF sends out (`donor-proposal-scoring`), or assess a Member Association against IPPF standards (`accreditation-desk-review`). It does not decide the award. It builds the instrument, and the panel decides.
