# Word export: two shapes, two builders

Markdown is canonical. Word is the offer, and the offer should be made both times because scoring outputs get circulated to management and proposal leads who will not open a `.md` file.

Pick the builder by the shape of the deliverable. Using the narrative builder for a table-first document produces a cramped result, because `WordReport` finding cards carry only a label, a value and a meaning: two columns of content. The comparison output needs three to six.

| Deliverable | Shape | Builder |
|---|---|---|
| SCORE output | Narrative, sectioned, a few score cards | `write_word_report` |
| CALIBRATE output | Table-first, many multi-column tables | Direct python-docx on `_open_branded_base()` |

Brand values come from `ane_package.reporting.brand.IPPF_FORMAT_TEMPLATE` in both cases. Hard-coding a colour, font or number format is a regression and fails QA review.

Both generators live next to the markdown they build from, named `gen_<slug>_scoring_docx.py` and `gen_<slug>_comparison_docx.py`.

## Every generator carries this docstring

The staleness warning is not optional. Once Ane has hand-edited the `.docx`, re-running the generator overwrites her edits and loses formatting-level changes silently.

```python
"""Build the IPPF-branded Word version of <the deliverable>.

Source of truth for the content is <slug>.md in this folder.

EDIT-PRESERVATION NOTE
----------------------
Once Ane has hand-edited <slug>.docx, this generator is STALE.
Do not re-run it to "refresh" the document: that overwrites her edits and loses
formatting-level changes silently. Edit the .docx in place with python-docx instead.
See mel_wiki/wiki/concepts/edit-preservation-protocol.md.

Run:  python gen_<slug>_docx.py
"""
```

## Shape 1 — narrative scoring, via `write_word_report`

```python
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\AGasser\OneDrive\5 ANE CLAUDE work folder")

from ane_package.reporting.word_export import (
    FindingCard,
    Section,
    WordReport,
    artifact_labels,
    write_word_report,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "<slug>-proposal-scoring.docx"
```

Structure the content as module-level constants so the generator reads as data plus one build call:

- `GLOSSARY` — a `dict` of term to plain-language definition. Cover the call vocabulary (award criteria, threshold, call fiche, funding rate, work package, milestone, deliverable, dissemination level, sub-granting or FSTP, Declaration of Honour, due diligence) and the MEL vocabulary (baseline, indicator, outcome, output, theory of change, gender-responsive indicator). Non-specialist readers get every term glossed.
- `BLUF` — a list of strings. The verdict first, then the load-bearing reason, then the things to know. Six to eight bullets.
- `SECTIONS` — a list of `Section(heading, plain_summary, bullets, finding_cards, technical_paragraph)`. `technical_paragraph` is the right place for "sections to fix", so the fix stays attached to the criterion that generated it.
- `METHOD_NOTE` — the sequence gate (criteria listed before scoring), the self-assessment bias statement, the score range, and the AI disclosure.
- `SOURCE` — the evidence base as one string: the call document with its page ranges, the proposal with its part and page ranges, and any sources cited inside the proposal that were relied on but not independently re-verified. Say that last part explicitly.

Score cards belong in the verdict section, one per criterion plus the overall:

```python
FindingCard(
    label="Relevance",
    value="33 / 40",
    meaning="Passes the 25-point minimum with room to spare. The strongest criterion.",
)
```

Build:

```python
report = WordReport(
    title=...,
    subtitle=...,
    audience_note=...,          # who it is for, and that it is an internal working document
    bluf_bullets=BLUF,
    sections=SECTIONS,
    method_note=METHOD_NOTE,
    source=SOURCE,
    date_dmy="DD/MM/YYYY",
    custom_glossary=GLOSSARY,
    **artifact_labels("report"),
)
write_word_report(report, OUT, lang="en-GB", branded=True, template="general")
```

`template="general"` is the default. Letterhead is for memos or on request.

## Shape 2 — table-first calibration, direct on the branded base

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from ane_package.reporting.word_export import IPPF_FORMAT_TEMPLATE as T
from ane_package.reporting.word_export import (
    _add_bullet,
    _add_logo_header,
    _add_para,
    _add_pillar_footer,
    _apply_a4_portrait,
    _ensure_brand_styles,
    _hex_to_rgb,
    _open_branded_base,
)

FONT = T["fonts"]["default"]["name"]
C_HEAD = T["colours"]["dream"]
C_BODY = T["colours"]["coco"]
C_ACCENT = T["colours"]["fire_red"]
C_BAND = T["colours"]["platinum"]
C_WHITE = T["colours"]["white"]
```

Document skeleton:

```python
doc = _open_branded_base()
_apply_a4_portrait(doc)
_ensure_brand_styles(doc)
_add_logo_header(doc)
_add_pillar_footer(doc)

_add_para(doc, "<title>", style="IPPF Title")
_add_para(doc, "<subtitle>", style="IPPF Subtitle")
_add_para(doc, "<audience note and tag key>", style="IPPF Footnote")
```

Styles available on the branded base: `IPPF Title`, `IPPF Subtitle`, `IPPF Heading`, `IPPF Body`, `IPPF Footnote`, `IPPF Glossary Term`.

### The branded-table helper

Two helpers do the work. `_shade` fills a cell; `add_table` builds a banded table with a coloured header row. Wrap a cell value in `**` to render it in the accent colour and bold, which is how a headline score or a contradicted finding gets emphasis without a second table.

```python
def _shade(cell, hex_colour: str) -> None:
    """Apply a solid background fill to a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_colour.lstrip("#"))
    tc_pr.append(shd)


def _write_cell(cell, text, *, bold=False, colour=C_BODY, size=9.5, align=None) -> None:
    para = cell.paragraphs[0]
    if align is not None:
        para.alignment = align
    run = para.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = FONT
    run.font.color.rgb = _hex_to_rgb(colour)


def add_table(document, headers, rows, widths, *, band=True):
    """Add a branded table. `widths` are point values, one per column."""
    table = document.add_table(rows=1, cols=len(headers))
    table.autofit = False
    hdr = table.rows[0]
    for i, (head, width) in enumerate(zip(headers, widths)):
        hdr.cells[i].width = Pt(width)
        _shade(hdr.cells[i], C_HEAD)
        _write_cell(hdr.cells[i], head, bold=True, colour=C_WHITE, size=9.5)
    for r_i, row in enumerate(rows):
        cells = table.add_row().cells
        for i, (value, width) in enumerate(zip(row, widths)):
            cells[i].width = Pt(width)
            if band and r_i % 2 == 1:
                _shade(cells[i], C_BAND)
            emphasis = str(value).startswith("**") and str(value).endswith("**")
            text = str(value).strip("*")
            _write_cell(
                cells[i],
                text,
                bold=emphasis or i == 0 and len(headers) <= 5,
                colour=C_ACCENT if emphasis else C_BODY,
            )
    document.add_paragraph()
    return table
```

### Column widths that work on A4 portrait

Total usable width is about 490 points. Widths that have rendered cleanly:

- headline scores, six columns: `[110, 40, 45, 70, 80, 140]`
- strong points or recommendations with a source tag: `[430, 55]`
- three-column agreement or miss tables: `[330, 80, 80]`, `[215, 70, 205]`, `[200, 85, 205]`
- two-column verdict table: `[175, 315]`

### Glossary footer

```python
for term, definition in GLOSSARY:
    para = doc.add_paragraph(style="IPPF Glossary Term")
    run = para.add_run(f"{term}: ")
    run.bold = True
    run.font.name = FONT
    run.font.color.rgb = _hex_to_rgb(C_ACCENT)
    run2 = para.add_run(definition)
    run2.font.name = FONT
    run2.font.color.rgb = _hex_to_rgb(C_BODY)
```

Close with `doc.core_properties.language = "en-GB"` before saving.

## Working originals

Two proven generators, one of each shape, are on disk at:

`C:\Users\AGasser\OneDrive\1. Ane's PROJECTS\AI in IPPF EN 2026\MY MEL AI SYSTEM DEMO\DEMO ARTEFACTS\test\`

- `gen_cerv_scoring_docx.py` — narrative shape
- `gen_cerv_comparison_docx.py` — table-first shape

Read them when a structure question comes up that this page does not answer. They are references, not templates to copy wholesale: their content is CERV-specific.
