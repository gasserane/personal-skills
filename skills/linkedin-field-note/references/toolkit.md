# Stage 4 — TOOLKIT: the companion artifact

The article promises one attachable artifact; this stage builds it to the Start-with-three bar. Exemplars: `build_three_agent_kit.py` (the generator pattern) and Ane's hand-edited `Start-with-three.docx` (the final quality bar — read it, not just the script, because her edits define the bar).

## Generator pattern

One Python script beside the content, named `build_<slug>_kit.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, r"C:/Users/AGasser/OneDrive/5 ANE CLAUDE work folder/personal-brand/generators")
from pb import (APRICOT, BODY, CTA, DISPLAY, GROUND, GROUND_TINT, INK, LABEL,
                MONO, MONOGRAM, SLATE, WINE, base_document, box, brand_footer,
                page_setup, para, rule_below, style_run)
from gen_report import glossary, h1, h2
```

Content lives in the script (it IS the canonical source for the toolkit, alongside a reader-facing `.md` mirror). Re-running the script regenerates the `.docx` — until Ane hand-edits the `.docx`, after which edit-preservation applies and changes go in as targeted fixes (docx-revision-pass method), never regeneration.

## The quality bar (checklist — all items, every toolkit)

- **Cover page:** monogram PNG at 2.4cm; title in Newsreader (DISPLAY) ~34pt wine; apricot `rule_below`; subtitle naming it a companion to the article (quote the article title); name · title line; date · `linkedin.com/in/anemariegasser`; page break.
- **Page map** ("Inside this kit" or similar) with **printed page numbers** per part. Page numbers must be real: after the first render, read the actual page of each anchor (Word COM `doc.Repaginate()` + `Find` + `Information(3)`, PowerShell 5.1 — pwsh 7 nulls COM methods), write the numbers into the map, render again, and re-check once (a changed map can reflow). Never ship guessed page numbers.
- **Type-first box labels**, Zilla Slab (LABEL) 10pt slate caps, one per box: `COPY-PASTE ...` for paste-ready blocks; `WHY IT MATTERS` / `WATCH OUT` / `TRY THIS` / `NOTE` for callouts. The label tells the reader what to DO with the box before they read it.
- **Copy-paste blocks:** `box(doc, fill=GROUND, border=SLATE)`, body lines in IBM Plex Mono (MONO) at 9.5-10pt ink, `space_after=0` between lines. Mono carries paste-ready instructions and values only, never running prose.
- **Callouts:** `box(doc, fill=GROUND_TINT, border=SLATE)`, body 11pt Nunito Sans ink.
- **Keep-together:** `w:cantSplit` on the row of every single-cell box (the `no_split(cell)` helper in the exemplar script) so no box breaks across pages.
- **Numbered lists** via manual runs (the exemplar's `numbered()`), not python-docx List Number styles (numbering carries over between lists).
- **Worked example** somewhere in the kit: one artifact's journey through whatever the kit teaches.
- **Footer:** `brand_footer(doc, closing=CTA)` — learning artefacts close with "Try. Measure. Share.", not the motto.
- **Afternoon-usable test:** a reader with no code, no budget, and no IT ticket can apply the kit the same day. Name the no-tool floor version where one exists.

## Outputs

1. `build_<slug>_kit.py` + `YYYY-MM-DD <Kit name> (article companion).docx` + `.md` mirror.
2. **PDF** for the LinkedIn document post: Word COM `SaveAs2(path, 17)` from the final `.docx` (fonts embed per brand rule). Regenerate the PDF from whichever file is authoritative at that moment.
3. **Cover visual** PNG if the document post wants one, per `AG Business/Brand/BRAND-SPEC.md` (field-notebook motifs, `FIELD NOTE #NN` stamp, apricot on exactly one element).

Present the rendered PDF to Ane page by page if she asks; iterate; record approval per artifact. Update the ledger.
