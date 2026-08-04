---
name: office-repair
description: 'Handle a hand-edited Office artefact that is now the authoritative version: repair a feature-rich Excel workbook in place through COM (broken slicers or dropdowns, #REF!, circular reference warnings), or promote a generated .docx/.pptx/.xlsx to canonical hand-edited source and retire its generator. Use when Ane reports a damaged workbook or declares an edited file the source of truth. Distinct from office-review-pass (Word review cycle), the ane_package.reporting builders (generate new branded files), and check-deliverable (read-only QA verdict on prose).'
model: opus
---

# /office-repair — fix a workbook in place, or hand a generated file over to Ane

One job: an Office file Ane already owns needs work, and the version on disk is the one that counts.

All Office surgery lives in `ane_package.officeops`. This skill contributes judgement, not plumbing. If a mode needs a capability officeops lacks, add it to officeops and test it there — `office-review-pass` is the worked example of that rule holding, and Wave 3 added five capabilities that way rather than growing its own. `references/officeops-excel-api.md` carries the exact call signatures; read it before writing any code.

The line, so it does not get relitigated: **anything that opens an Office file belongs in officeops.** Diffing two lists of strings, spotting an autocorrect flip and rewriting a `.py` generator are not Office operations, so they live in `scripts/office_repair.py` and are tested there.

## Mode routing

- **repair** — an Excel workbook Ane maintains is broken or needs a change, and it carries features a naive write would destroy.
- **canonical** — a generated artefact has been hand-edited, and the generator is now the stale copy.

The two meet when a repaired workbook also has a generator behind it. Run `repair` first, then `canonical` to retire the generator.

## Shared rules — both modes

- **Ane's file is the baseline.** Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists. Read what is on disk, change only what was asked, leave everything else byte-identical. This skill exists because that rule is hardest to keep on binaries, where a loss is both silent and unrecoverable.
- **Never write an Office file with openpyxl when it carries features openpyxl cannot see.** Slicers have no openpyxl representation at all: load and save, and `xl/slicers/` is simply gone, the workbook still opens, and nothing reports anything. Scanning is read-only for that reason, not only for safety.
- **Verify on the written file, against what it had before.** `workbook_inventory` before, `assert_inventory_unchanged` after. A save that returned proves nothing.
- **Never invent a fact.** Cell addresses, sheet names, figures, formulas. If it is not in the scan or in loaded context, ask.
- **Report in the EDIT-PRESERVATION DELIVERY format**: what changed, what was left alone, and out-of-scope observations listed but not acted on.

## repair mode

The workbook has slicers, charts, protection, structured references and spill formulas. All of them are invisible to the tools that would be quickest, which is why this mode is a sequence rather than a call.

1. **Diagnose first, read-only.**
   `python scripts/office_repair.py scan <workbook>`
   This reports structure, ListObject coverage, cached error cells with the formula behind each one, fragmented data-validation ranges, and the feature inventory. Nothing is written and the workbook may be open in Excel while it runs.

   Add `--com` to also ask Excel for circular references. That pass needs Excel and opens the file read-only. It is worth running whenever Ane reports a warning dialog on open or zeros where numbers belong: a circular reference lives in the dependency graph Excel builds at calculation time and not in the stored XML, so no amount of reading the file will find it.

2. **Read the scan honestly.** Two results look like good news and are not:
   - **No cached errors in a workbook Excel has never opened.** The file caches the last calculated result, so a library-written workbook caches nothing. Empty means "nothing cached", not "nothing wrong".
   - **Fragmented validation ranges.** A dropdown applied to a column arrives as one area. Row insertion shatters it into single-row areas, and the rule then holds on some rows and not others. Nothing errors, because a missing dropdown shows as an empty cell.

3. **Agree the fix list with Ane before writing.** Name each cell, its current value and its new one. The scan gives you the current values; do not describe a change you have not read the current state of.

4. **Build the payload and apply it.** Write a JSON list of `{sheet, cell, old, new}` and run
   `python scripts/office_repair.py repair <workbook> --edits edits.json`
   `old` is a guard, not documentation: the current formula is read first and the edit is skipped when it does not match. Five rails come with it — a timestamped backup, the per-cell guard, sheet protection captured and re-applied exactly as found, one save at the very end, and a throw before that save so a partial repair is discarded rather than written.

5. **A skipped cell is a failure, not a no-op.** It means the payload is stale or the address is wrong. The command exits non-zero and says so. Re-scan rather than re-running with `--no-strict`, which writes what matched and leaves the rest — useful only for a deliberate second pass.

6. **Verify against the backup.**
   `python scripts/office_repair.py verify <workbook> --baseline <workbook>.backup-1.xlsx`
   The backup is the only honest record of what the workbook had before, which is why the assertion compares against it rather than against a remembered count.

**Why COM and not openpyxl.** Not preference. Slicers, sheet protection and ListObject geometry have no openpyxl equivalent Excel then honours. The COM path costs an Excel launch and about a minute; an openpyxl write costs a workbook.

## canonical mode

Ane has edited a generated file in Word, PowerPoint or Excel. From now on her file is the source and the generator is the stale copy. The job is to make that true in the file system, not just in the conversation.

1. **Extract and compare.**
   `python scripts/office_repair.py diff <edited> --against <generated>`
   Extraction recurses into grouped shapes and table cells. That matters more than it sounds: a flat pass over a .pptx returns every slide title and not one bullet, because python-pptx reports a group as a single shape with no text and the bullets live on its children. A deck that comes back as headings only is the extraction failing, not the deck.

2. **Separate her edits from Word's.** The command flags four things it thinks Office did rather than Ane: diacritics silently stripped, smart-quote and dash autocorrection, a space landing inside a URL, and a near-identical rewording that reads like a stray keystroke. None of these is a verdict — put each in front of her. The asymmetry is what justifies asking: propagating an autocorrect flip into the canonical version makes it permanent and invisible, while asking about a deliberate edit costs one line of reply.

   It also flags structurally when the edited file has less than half the text blocks of the generated one. That is the 2026-07-22 signature of a redesign that dropped the body layer and left titles.

3. **Report her changes as a change list**, grouped and in her terms — what the document now says, not which block index moved. Confirm the flagged artefacts one at a time.

4. **Sync the `.md` mirror where one exists**, and add a note naming the Office file as canonical and the date. Where no mirror exists, do not create one.

5. **Retire the generator.**
   `python scripts/office_repair.py archive <generator>.py --canonical <edited file>`
   This prepends a guard that refuses to run without `--force`, and under `--force` restores the canonical file byte-for-byte if the run touches it. It is code rather than a comment because a comment does not stop anyone, and the failure being prevented is a future session running `python gen_x.py` in good faith. Running it twice changes nothing.

**Do not fold her edits back into the generator.** It is the obvious move and it is wrong: a generator can reproduce text but not the formatting-level changes Ane made in Word, so folding in produces a script that looks current and silently regenerates a worse file. Archive it instead. Where a change genuinely belongs in the generator because it will be generated again for a different document, say so and make that a separate piece of work.

## Verification plan

Every mode states its check before it works, and the check reopens the written file:

| Mode | What gets asserted |
|---|---|
| scan | Read-only — nothing written. Report the feature inventory and the counts found. |
| repair | Replacement outcome per cell read back from Excel, then `assert_inventory_unchanged` against the pre-repair inventory, then `verify --baseline` against the backup: tables cover their rows, no cached errors, no feature lost. |
| diff | Read-only. Report block counts both sides and every flagged artefact explicitly, including the ones Ane confirms were deliberate. |
| archive | Run the archived generator. It must exit non-zero and leave the canonical file byte-identical. Asserting on the guard's source text tests the wrong thing — a refusal that only exists in a docstring is the failure this mode exists to prevent. |

`python scripts/test_office_repair.py` checks the driver itself: the change list, the artefact heuristics, and the generator guard actually refusing as a subprocess. Office behaviour is covered by `tests/test_officeops.py` in the work folder.

## Scope boundary

- A Word review cycle — reading comments, tracked changes, a glossary and source annex — is `office-review-pass`. This skill is Excel repair and the canonical handover.
- Producing a new branded file is `ane_package.reporting`; building a ToR is `tor-procurement`; a read-only QA verdict on prose is `check-deliverable`.
- Both COM paths need Windows, Excel installed, and PowerShell 5.1 — never pwsh 7, whose null-method handling breaks the Excel path. `win32com` is not installed in this Python and is not the route.
- `PackageNotFoundError` means an open handle in Excel, not a corrupt file. Test with `zipfile` before telling Ane her workbook is damaged.
- On a web container the `diff` and `archive` paths still work; `scan --com` and `repair` do not.
