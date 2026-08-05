# Stage 4 — TOOLKIT: the companion artifact

The article promises one attachable artifact; this stage builds it to the Start-with-three bar. Exemplars: `build_three_agent_kit.py` (the generator pattern) and Ane's hand-edited `Start-with-three.docx` (the final quality bar — read it, not just the script, because her edits define the bar).

## Generator pattern

One Python script beside the content, named `build_<slug>_kit.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, r"C:/Users/AGasser/OneDrive/2. Ane's AREAS/AG Business/Brand/generators")
from pb import (APRICOT, BODY, CTA, DISPLAY, GROUND, GROUND_TINT, INK, LABEL,
                MONO, MONOGRAM, SLATE, WINE, base_document, box, brand_footer,
                page_setup, para, rule_below, style_run)
from gen_report import glossary, h1, h2
```

Content lives in the script (it IS the canonical source for the toolkit, alongside a reader-facing `.md` mirror). Re-running the script regenerates the `.docx` — until Ane hand-edits the `.docx`, after which edit-preservation applies and changes go in as targeted fixes (docx-revision-pass method), never regeneration.

## The quality bar (checklist — all items, every toolkit)

- **Cover page:** monogram PNG at 2.4cm; title in Newsreader (DISPLAY) ~34pt wine; apricot `rule_below`; subtitle naming it a companion to the article (quote the article title); name · title line; date · `linkedin.com/in/anemariegasser`; page break.
- **Cover illustration:** one diagram on the title page, below the byline, at full text width (`Cm(16.2)` on the A4 page set by `page_setup`), with a right-aligned Zilla Slab (LABEL) 9.5pt slate caption stating what it shows. Build it in its own `render_<slug>_cover.py` beside the kit generator so wording changes re-render in seconds: PIL on a `GROUND` canvas, slate spine and faint notebook rules for the field-note family look, wine and slate as the two carriers, apricot on the numbered stations only. Draw at 3x and downsample with LANCZOS — PIL arcs are not anti-aliased. Make it *procedural*, not conceptual: whatever the article illustrated as an idea, the kit cover shows as the steps the reader will run, numbered, in the order the kit teaches them. Newsreader variable-font axes are `[Weight, Optical Size]` in that order.
- **Page map** ("Inside this kit" or similar) with **printed page numbers** per part. Page numbers must be real: after the first render, read the actual page of each anchor (Word COM `doc.Repaginate()` + `Find` + `Information(3)`, PowerShell 5.1 — pwsh 7 nulls COM methods), write the numbers into the map, render again, and re-check once (a changed map can reflow). Never ship guessed page numbers. Do not loop `Range.Information(3)` over every paragraph: it repaginates on each call and took over two minutes on a 5-page kit. `doc.ComputeStatistics(2)` returns the page count in one fast call — enough to confirm a cover change did not reflow the map.
- **Type-first box labels**, Zilla Slab (LABEL) 10pt slate caps, one per box: `COPY-PASTE ...` for paste-ready blocks; `WHY IT MATTERS` / `WATCH OUT` / `TRY THIS` / `NOTE` for callouts. The label tells the reader what to DO with the box before they read it.
- **Copy-paste blocks:** `box(doc, fill=GROUND, border=SLATE)`, body lines in IBM Plex Mono (MONO) at 9.5-10pt ink, `space_after=0` between lines. Mono carries paste-ready instructions and values only, never running prose.
- **Callouts:** `box(doc, fill=GROUND_TINT, border=SLATE)`, body 11pt Nunito Sans ink.
- **Keep-together:** `w:cantSplit` on the row of every single-cell box (the `no_split(cell)` helper in the exemplar script) so no box breaks across pages.
- **Numbered lists** via manual runs (the exemplar's `numbered()`), not python-docx List Number styles (numbering carries over between lists).
- **Worked example** somewhere in the kit: one artifact's journey through whatever the kit teaches.
- **AI-use disclosure paragraph**, exemplar wording from `build_three_agent_kit.py`, placed before the brand footer — on every kit, docx and workbook alike (the workbook carries it on the Read me sheet). This is a checklist item precisely because it once lived only in the exemplar's code and drifted the first time a generator was written from scratch (field note #03, 2026-08-05). A mandatory element belongs here, not in a script someone may not copy.
- **Footer:** `brand_footer(doc, closing=CTA)` — learning artefacts close with "Try. Measure. Share.", not the motto.
- **Afternoon-usable test:** a reader with no code, no budget, and no IT ticket can apply the kit the same day. Name the no-tool floor version where one exists.

## Outputs

1. `build_<slug>_kit.py` + `YYYY-MM-DD <Kit name> (article companion).docx` + `.md` mirror.
2. **PDF** for the LinkedIn document post, regenerated from whichever file is authoritative at that moment. **Ask Ane to export it from the Word UI; do not automate this step.** Word COM `ExportAsFixedFormat` and `SaveAs2(path, 17)` hang on these kits: three runs on 2026-07-27 each passed 25 minutes without writing a file, on the OneDrive path and on a local copy, while the same export by hand finished in seconds. Hand her the `.docx` and say plainly that the PDF is stale. Word COM stays fine for opening and page counts.
3. **Cover visual** PNG if the document post wants one, per `AG Business/Brand/BRAND-SPEC.md` (field-notebook motifs, `FIELD NOTE #NN` stamp, apricot on exactly one element). This is the LinkedIn post image and is separate from the title-page illustration inside the kit; they share the visual family, so build the kit cover from the same motifs.

4. **Document-post caption**, `YYYY-MM-DD LinkedIn DOC POST - field note NN - <slug> (DRAFT).md`. The PDF goes up as a LinkedIn *document* post and needs its own caption; without one the kit ships mute. Draft it in this stage, alongside the kit, and run the same ane-voice checklist as Stage 3.

   Shape, about 200 words and shorter than the ultra-short post because the PDF carries the content: (1) "Here is the kit I promised", naming what it is in one line; (2) one sentence tying back to the article's argument, no time claim ("in the last field note", never "last week", because the publish gap moves); (3) an "Inside:" list, one bullet per part, each stating what the reader gets rather than what the part is called; (4) the no-tool floor ("no code, no budget, no IT ticket"); (5) one instruction they can follow today, naming the single highest-value step in the kit; (6) "The full field note is in the article. Link in the first comment."; (7) the closing question, ideally asking readers to extend one specific thing in the kit; (8) compressed P.S. disclosure, then the series hashtags. Add the first-comment block with the article-link placeholder.

   Publishing order for a note: article, then short post plus first comment, then the kit document post the following Tuesday. The caption points back at the article, never forward at anything unpublished.

## Build route when the edit-preservation guard blocks the content folder

Once any hand-edited `.docx` from an earlier note is registered in the content folder, the guard blocks EVERY shell command that pairs a `.py` path (or a `.docx` copy) with that folder, including builds whose destination is a brand-new file (observed throughout the #04 build, 2026-08-05). Do not fight it call by call; use the proven route:

1. Write the generator/render script to the session scratchpad (keep a byte-identical canonical copy in the content folder via the Write tool, with output paths resolving to the content folder for images).
2. Run it in the scratchpad; verify there (page map via Word COM, content asserts via python-docx, PNGs by eye).
3. Deliver: PNG `Copy-Item` calls with explicit single-file destinations pass; `.docx` (and PNG overwrites of files the guard now tracks) go via the MCP sandbox (`ctx_execute`, `fs.copyFileSync`) **guarded by your own assert** — destination-does-not-exist for new files, or an mtime/size check proving the destination is still this session's own build. Never copy over a file you cannot prove Ane has not touched.

Word COM page verification gotcha: `Find` hits the "Inside this kit" page-map row before the real heading — take the SECOND occurrence of each anchor.

## After a Word save

Once Ane opens the `.docx` in Word and saves (which she does to export the PDF), her saved file is newer than the generator's output. Re-running `build_<slug>_kit.py` would overwrite it. Check timestamps before regenerating, and if hers is newer, ask what changed in Word and fold it into the generator first.

Present the rendered PDF to Ane page by page if she asks; iterate; record approval per artifact. Update the ledger.
