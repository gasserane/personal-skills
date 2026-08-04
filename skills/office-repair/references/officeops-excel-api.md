# `ane_package.officeops` — the Excel and extraction API this skill sits on

Read this before writing any code. Every name below already exists and is tested
in `tests/test_officeops.py` — run it for the current check count rather than
trusting a number written here, which went stale twice. Do not invent names, and do not
re-implement Office surgery inside the skill: a capability this skill needs and
officeops lacks is an addition to officeops, with its own test.

The Word surface — comments, tracked changes, `wordcom` find-and-replace, the
docx assertions — is documented in the sibling skill
`office-review-pass/references/officeops-api.md`. This file covers what
`office-repair` uses.

```python
from ane_package.officeops import (
    Checks, VerificationError, assert_inventory_unchanged,
    extract_blocks, extract_text, table_row_counts, workbook_inventory,
)
from ane_package.officeops import excelcom          # Windows only for the COM calls
```

If the import fails from outside the work folder, call
`officeops.bootstrap.ensure_ane_package_importable()` first, or set
`WORK_FOLDER_ROOT`. `scripts/office_repair.py` carries the inline form for a
script living in the clone — copy that preamble.

## Contents

- [Diagnosis](#diagnosis) — read-only, no Excel needed
- [Diagnosis through Excel](#diagnosis-through-excel) — COM, read-only
- [Applying a repair](#applying-a-repair) — COM, writes
- [Verification](#verification)
- [Extraction](#extraction) — canonical mode, plus image-based deck exports
- [Traps](#traps)
- [Writing a branded workbook](#writing-a-branded-workbook) — not officeops, but check here before building one

## Writing a branded workbook

`officeops` repairs and reads Office files. It does not *author* them. Anything
that writes a branded artefact lives in `ane_package.reporting`, on xlsxwriter,
reading `IPPF_FORMAT_TEMPLATE` — never a hard-coded colour, font or number
format. Check this list before writing a builder; the shape you need often
exists.

```python
from ane_package.reporting.excel_templates import (
    build_disaggregation_crosstab,   # a category x category table
    build_time_trend,                # a series over periods
    build_indicator_tracker,         # indicator x target x actual x variance x status
    build_baseline_endline,          # before / after with change
    build_review_worklist,           # one row per finding, severity colour-coded
)
from ane_package.reporting.selection_toolkit import (
    SelectionSpec, build_master_workbook, build_scorer_workbook,
    panel_mean, financial_score, decide, rank_rows,   # the engine, tested directly
)
from ane_package.reporting.delivery_kickoff import (
    KickoffSpec, Role, Bucket, Item, build_kickoff_workbook,
    allocation, budget_status, over_commitment_signal, lane_split,  # the engine
)
```

`selection_toolkit` runs a weighted selection between a published ToR and the
award. `delivery_kickoff` runs the first working session of a delivery contract
against a fixed day budget, and is the shape to copy for any multi-sheet
workbook whose numbers matter: a validated frozen dataclass, then pure
arithmetic, then builders that write formulas agreeing with that arithmetic.

**Why the arithmetic is a separate importable layer in both.** A formula string
proves nothing about the number Excel produces. Test the rules in Python, write
the formulas to agree with them, then assert Excel's computed values against the
same functions through COM. Reading a formula back only proves you wrote the
formula you wrote.

## Diagnosis

```python
excelcom.scan_workbook(path) -> dict
```
Sheets, ListObjects with their `ref`, headers, covered row counts, protection
flags, defined names. Read-only openpyxl; never saves.

```python
excelcom.scan_errors(path) -> list[dict]
```
`{sheet, cell, error, formula}` for every cell holding a cached Excel error.
Loads the workbook twice — `data_only=True` for the cached result,
`data_only=False` for the formula — because the error says what broke and the
formula says why. A cell holding a literal error and no formula reports
`formula: None` rather than naming itself.

**An empty result is not a clean bill of health.** Excel caches the last
calculated value, so a workbook written by a library and never opened in Excel
caches nothing. `find_circular_references` is the pass that catches what a cached
scan cannot.

```python
excelcom.scan_validations(path, min_areas=3) -> list[dict]
```
`{sheet, type, formula1, areas, single_row_areas, sqref, fragmented}` per
data-validation rule. `fragmented` is true when a rule spans `min_areas` or more
areas and at least half are single rows — the fingerprint of row insertion
shattering a contiguous `sqref`. Three separate blocks of ten rows is scattered,
not shattered, and is not flagged.

```python
excelcom.ERROR_VALUES
```
The nine cached error strings, if a caller needs to match them directly.

## Diagnosis through Excel

```python
excelcom.scan_com(workbook, payload, body, timeout=300) -> dict
```
Runs a PowerShell body against a workbook opened **read-only**, with no `Save`
in the skeleton and no backup taken, because nothing is written. Safe to run
while the file is open in Excel. Body sees `$xl`, `$wb`, `$p`; write results into
`$result`.

```python
excelcom.find_circular_references(workbook, timeout=300) -> list[dict]
```
`{sheet, address}` per affected sheet. openpyxl cannot see these — a circular
reference is a property of the dependency graph Excel builds at calculation time,
not of the stored XML. An empty list is a stronger statement than a clean
`scan_errors` pass.

## Applying a repair

```python
excelcom.apply_cell_edits(workbook, edits, strict=True, backup=True,
                          timeout=600) -> {"applied": [...], "skipped": [...]}
```
`edits` is a list of `{sheet, cell, old, new}`. `old` is the guard: the current
formula is read first and the edit is skipped when it does not match. Five rails,
all inside the call:

1. a timestamped backup before the first write (COM has no undo);
2. the expected-old-value guard per cell;
3. sheet protection captured before unprotecting and re-applied exactly as found;
4. a single save at the very end, owned by the skeleton;
5. under `strict`, a throw *before* that save, so a partial repair is discarded.

A `skipped` entry means a stale payload or a wrong address. `strict=False` writes
what matched and reports the rest — for a deliberate second pass only.

```python
excelcom.apply_com(workbook, payload, body, backup=True, timeout=600) -> dict
excelcom.build_script(workbook, payload_path, body, read_only=False) -> str
excelcom.write_payload(data, path) -> Path
excelcom.set_locked(workbook, sheet, ranges, locked=True) -> dict
```
The lower-level pattern, for a change `apply_cell_edits` does not cover. Keep the
split: UTF-8 JSON payload, ASCII PS1 script. `set_locked` writes one area at a
time and reads each back, because a bulk `Range.Locked` write returns without
error and changes nothing.

## Verification

```python
workbook_inventory(path) -> dict
```
Counts of `slicers`, `slicer_caches`, `charts`, `tables`, `pivot_caches`,
`pivot_tables`, `drawings`, plus `defined_names` and `sheets` by name, read
straight from the zip.

```python
assert_inventory_unchanged(path, baseline)          # baseline: dict or a path
```
Raises `VerificationError` naming what was lost. Take the inventory before the
repair, or pass the backup path — the backup is the only honest record of what
the workbook had. **Gains are not failures**; the defect being guarded against is
subtraction.

```python
excelcom.verify_tables(path, expected=None) -> dict
table_row_counts(path) -> {name: (covered, populated)}
assert_table_covers_rows(path, table, expected=None)
```
The openpyxl defect these exist to catch: appended rows fall outside the
`ListObject` ref because openpyxl does not grow it, so structured references and
slicers quietly miss them.

`Checks` is the pass-fail collector: `checks.check(condition, label)`,
`checks.expect(label, fn, *args)` for a call that should not raise, then
`checks.report()` returns a process exit code.

## Extraction

```python
extract_blocks(path) -> list[Block]        # .index .where .kind .text
extract_text(path)   -> list[str]
```
Covers `.docx`, `.pptx`, `.xlsx`, `.xlsm`; a legacy `.doc`/`.ppt`/`.xls` raises
and says to convert first. Blocks are numbered in document order from 1.

Both readers recurse. In Word that means table cells, including a table nested in
a cell. In PowerPoint it means grouped shapes, table cells and speaker notes.
`where` carries the location — `body table r2c1`, `slide 4 group`,
`REF_SAM!B7` — so a change list can point at something.

### Word tables as grids

```python
document_tables(path) -> list[DocTable]    # .index .where .depth .rows .merged .ragged
                                           # .n_rows .n_cols
                                           # .header() .column(i) .records()
```
`.docx` only. Use this and never `extract_blocks` whenever a table's *shape*
carries meaning — award criteria against their weights, a compliance checklist, a
milestone schedule. Added for `selection-toolkit`, which reads the criteria out of
a published procurement ToR.

`extract_blocks` cannot do this job and fails at it silently. It labels every cell
`body table r2c1` with **no table ordinal**, so two tables in one ToR are
indistinguishable, and it **drops empty cells**, so a criterion row with a blank
weight shifts every later column one place left. The caller gets plausible strings
and scores a panel against the wrong weights for six weeks.

`rows` is padded to a constant width, so `rows[r][c]` always addresses the cell a
reader sees. `merged` holds the positions that *continue* a span rather than being
cells of their own — python-docx returns the same cell object for every position a
merge covers, so a header reading `Financial | Financial | Financial` is one merged
heading, not three columns. `records()` keys body rows by the header and **raises**
on a repeated or blank header rather than dropping the collision. Nested tables
arrive as their own entries with `depth` above 0; a cell holding a table reads as
empty in its parent, because python-docx reads only direct paragraphs for
`cell.text`.

### Image-based deck exports

```python
looks_like_deck_export(path) -> DeckExportCheck   # .is_deck_export .reason .main_part
                                                  # .image_count .body_paragraphs
                                                  # .mean_paragraph_chars .has_altchunk
slide_images(path, out_dir=None) -> list[SlideImage]
                                                  # .index .anchor .anchor_index .part
                                                  # .image_format .size .digest .path
```
`.docx` only. For a Storyline or PowerPoint export where the translatable text is
rasterised inside slide images and the body holds only slide titles. Used by
`localise` deck mode.

Four things it gets right that a hand-rolled reader does not. The main part is
resolved through `_rels/.rels`, because these exports name it `document2.xml` and
a reader hard-coded to `word/document.xml` reports an empty document. Relationship
targets are normalised, so `../media/image1.bin` resolves to the package root.
The image format is sniffed from the bytes, because the parts are `.bin` and hold
JPEGs. And both the DrawingML (`a:blip`) and legacy VML (`v:imagedata`) paths are
read, since a reader that knows only the first drops whole slides.

`anchor` is the slide-title paragraph the image sits under, and it is what a
comment hangs on, since a comment cannot sit on text inside an image. Match on
`anchor` text, not on `anchor_index`: `add_comments` resolves paragraphs by
string, and its index space excludes empty paragraphs. `digest` is what separates
a slide from the navigation chrome repeated on every one. Without `out_dir`
nothing is written and `path` stays `None`, which is what the anchoring and
worklist steps want.

`DeckExportCheck` carries the evidence with the verdict because the verdict is a
heuristic: three or more images plus either the Storyline layout, an `altChunk`,
or live paragraphs averaging 80 characters or fewer.

## Traps

1. **Slicers do not survive openpyxl.** There is no representation for them, so
   load-and-save drops `xl/slicers/` and the workbook still opens. Never write a
   feature-rich workbook with openpyxl; that is what the COM path is for. Charts
   and pivot caches are version-dependent, which is why `workbook_inventory`
   counts them rather than assuming either way.

2. **`TableList.items()` yields `(name, ref-string)`, not `Table` objects.**
   Fetch by name. This cost a debugging round in Wave 1.

3. **PowerShell 5.1, never pwsh 7.** COM objects come back from pwsh 7 with null
   methods, so a script that looks right does nothing. `win32com` is not
   installed in this Python and is not the fallback.

4. **Bulk `Range.Locked` writes fail silently.** Setting `Locked` on a
   multi-area range returns without error and leaves the cells as they were.
   Verify per run.

5. **`PackageNotFoundError` means an open handle in Excel, not corruption.**
   Test with `zipfile` before telling Ane her workbook is damaged.

6. **A flat text walk loses PowerPoint bullets.** python-pptx reports a group as
   one shape whose text is empty; the bullets are on its children. A deck that
   extracts as titles only is the walk failing, not the deck.
