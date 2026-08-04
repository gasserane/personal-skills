---
name: contract-delivery-kickoff
description: 'Prepare the first working session with a contracted supplier against a fixed day budget: reads the agreed offer or contract, then builds a branded session workbook whose day-budget sheet totals against the contracted ceiling, an internal prep brief, a supplier agenda and a post-session note template. Use for kick-off or delivery-session prep with a supplier, or day-budget splits over a signed offer. Distinct from tor-procurement (writes the ToR), selection-toolkit (panel scoring), procurement-offer-review (one incoming offer), implementation-pack (donor grants IPPF receives), and meeting-notes mode 2 (1-1 prep).'
model: opus
---

# /contract-delivery-kickoff — the session that sets the ceiling

One job: a contract is signed, work is about to start, and the first session decides how a fixed number of days gets spent. `/tor-procurement` wrote the ToR, `selection-toolkit` ran the award. This is what happens after signature.

## Why this exists

A delivery contract does not fail loudly. It drifts. The first session walks an issue list, agrees to everything reasonable on it, and the overrun surfaces in month five when the last tranche has no days left. The reference run is the Abortion Dashboard Phase II session of 24 July 2026: 8 technical and 7 coordination days against 17 contracted components, done entirely by hand.

**So the deliverable is the arithmetic.** The prep brief and the agenda are how the arithmetic reaches the room. If you produce beautiful documents and no day budget, you have built nothing.

## The rule that governs everything here

**Nothing is invented.** Every contracted day, every rate, every tranche comes from the contract or is reported as a gap for Ane to resolve. A day rate read off a similar contract is indistinguishable from a real one once it is in a cell, and the session commits money against it. `read` never fills a gap; `build` refuses while `_gaps` survives; `validate_spec` refuses a real hole afterwards, so deleting the gap list smuggles nothing through.

## The five moves this encodes

All five are proven on the 24 July 2026 session. They are not style preferences; each one closes a way the session goes wrong.

1. **Split every item into lanes.** Content the client owns (final text, labels, definitions, files) costs the supplier almost nothing once handed over. Build work costs days, and there are few. The lane split is usually the cheapest scope win in the hour.
2. **Agree the cap before the walkthrough.** The workbook puts `01 Day budget` before `02 Triage` for this reason, which reverses the hand-built version. A list of 17 plausible items read first answers "what fits in 8 days" against the list instead of against the contract.
3. **Ask for estimates on every tranche in session one**, not only the one starting now. A tranche with no estimate is not a tranche with no cost. The workbook writes `not priced` where a zero would have gone, and the engine keeps it as `None` so it cannot hide inside a total.
4. **Name the protected items first.** A do-no-harm, credibility or compliance defect survives the cap; it does not compete for it. Saying so before the trade-offs start stops the trade being offered.
5. **Check signature status before anything else.** An unsigned contract means no expenditure can be committed, and it usually means the first contractual deliverable has already slipped. `validate_spec` refuses a spec whose signature status is unknown, so this cannot be skipped by omission.

## Where the code lives

All Office work is in `ane_package`. This skill contributes judgement, not plumbing.

- `ane_package.reporting.delivery_kickoff` — the spec, the day-budget engine, the workbook builder.
- `ane_package.reporting.markdown_docx` — renders the markdown artefacts as branded Word.
- `ane_package.officeops.extract` — `document_tables` reads the contract's budget table as a grid that keeps its blanks; `extract_text` reads the prose.
- `scripts/contract_kickoff.py` — the driver: budget-table detection, number parsing, signature reading, spec assembly, artefact text, verification.

The boundary, so it does not get relitigated: **anything that opens an Office file belongs in the module.** Exactly one function in the driver opens a document, `load_document`, and a test asserts that it stays exactly one. Everything downstream takes objects, which is why the whole parser is tested without a single `.docx` fixture.

Read `references/officeops-excel-api.md` (in `office-repair`) before writing any Office code, and `references/session-moves.md` here for how to run the hour.

## Running it

### 1. Read the contract

```bash
python scripts/contract_kickoff.py read "Agreed offer.docx" \
    --supplier "Baobab Tech" --contract "Phase II delivery" \
    --out kickoff-spec.json
```

Prints the contracted roles it found, the tranches, the candidate items, and every gap. Take the gaps to Ane. The common ones, in order of how often they appear:

- **Signature status.** An offer almost never states whether it was countersigned. This gap is close to guaranteed, and it is move 5 doing its job rather than a parser failure.
- **Day splits per tranche.** A contract names its tranches and rarely prices them separately. That is the question for session one.
- **Lane and severity on every item.** A parser cannot tell client content from supplier build, and an item wrongly marked `Client, content` reads as free when it is not. These are set with Ane, never guessed.

### 2. Fill the spec with Ane, then delete `_gaps`

The spec file is the audit trail for "why does this contract have 8 days". Keep it beside the pack.

### 3. Build

```bash
python scripts/contract_kickoff.py build kickoff-spec.json --out "Session 1"
```

Writes the workbook plus `PREP-brief.md`, `AGENDA-to-supplier.md` and `NOTE-template.md`, each rendered to branded Word. **Markdown is canonical.** Edit the `.md` and re-run; never edit the `.docx` and expect it to survive a rebuild.

`build` also runs the contract's own proposal through the engine and reports whether it fits its own ceiling. A contract proposing 9 days against 8 bought has a problem no session can negotiate away, and finding that out while drafting the agenda is much cheaper than finding it out in the room.

`build` refuses to overwrite an existing workbook. Once it has been used in a session, the estimates and decisions in it exist nowhere else.

### 4. Verify by execution

```bash
python scripts/contract_kickoff.py verify "Session 1" --spec kickoff-spec.json
```

Copies the workbook, injects sample day figures through Excel COM, forces a full recalculation, and asserts the numbers Excel produces against the same Python engine the formulas were written from, plus zero formula-error cells.

**A workbook that looks right and calculates wrong is the failure mode here.** Reading a formula back proves only that the formula you wrote is the formula you wrote. Verification runs on a copy, so sample data never lands in a live contract record.

If Excel is unavailable the command exits 2 and says the workbook was not verified. Report that as unverified. Do not present an unverified workbook as checked.

### 5. Commit the output

The edit-preservation guard cannot see Excel COM or openpyxl writes, so it flags the emitted files as hand-edited. Commit them as the final step rather than leaving them dirty.

## What the workbook holds

`00 Guide` (signature status first, then how to run the hour, then the severity and lane vocabularies), `01 Day budget` (per role: tranches, days proposed against days agreed, hours, share, value, then total, contracted and remaining, with the lane split computed live from the triage sheet), `02 Triage` (one row per candidate item, with the columns the session fills shaded), `03 Decision log`, `98 REF` (the contracted parameters, so the audit trail travels with the file).

## Things that will bite

1. **A contract in another language.** Budget-table headers, rate words and signature wording are matched accent-blind across English, French, Spanish, Romanian and German. An English-only guard finds no budget table in a French offer and reports a gap that is a fact about the parser, not about the document. This has bitten on three consecutive waves.
2. **`1.234` is one thousand two hundred and thirty-four**, in four of the five languages above. Reading it as 1.234 turns a day rate into pocket change and the whole budget silently becomes nonsense. `parse_number` infers the convention from the separators actually present rather than assuming one.
3. **A total row is not a resource line.** Reading it as one doubles the contracted days, and the resulting ceiling is generous enough that nothing ever looks over budget.
4. **`None` and `0.0` are not the same day count.** A tranche nobody has priced and a tranche priced at zero are indistinguishable inside a total, and the first is what sinks the contract. The engine propagates `None`; the workbook writes `not priced`.
5. **The early warning fires while the budget is still positive.** A bucket whose agreed days exceed the contract's own proposal by more than 1.5x raises a signal even when the total is still under the ceiling. A constraint that only signals once breached signals too late, which is the failure this skill exists to prevent.
6. **The agenda goes to the supplier.** The signature warning, the protected-items list and Ane's reading of where the contract is weak stay in the prep brief. A test asserts they do not leak.
7. **Ask for the estimate before saying what you want.** Naming the outcome first anchors the number, and the anchored number is the one the whole budget is then built on.

## Where this does not go

It does not write the ToR (`/tor-procurement`), run the award panel (`selection-toolkit`), analyse a single incoming offer (`procurement-offer-review`), or track a donor grant IPPF receives (`implementation-pack`). It does not manage the contract after session one, and it does not decide what comes out of scope. It builds the instrument and does the arithmetic; Ane and the supplier decide.
