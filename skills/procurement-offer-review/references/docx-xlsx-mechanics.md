# Extraction and editing mechanics — docx, PDF, xlsx

Working notes for the three modes. Everything here was proven in production (Abortion Dashboard Phase II reviews, July 2026; MA Dashboard 19-bidder evaluation, July 2026).

## Extracting a docx offer or pack document

Plain text via python-docx (`Document(path).paragraphs` + tables), or directly from the XML when python-docx is unavailable:

```python
import zipfile, xml.etree.ElementTree as ET
NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
with zipfile.ZipFile(path) as z:
    root = ET.fromstring(z.read("word/document.xml"))
paras = []
for p in root.iter(NS + "p"):
    t = "".join(n.text for n in p.iter(NS + "t") if n.text)
    if t.strip():
        paras.append(t)
```

Note `w:t` excludes deleted text (`w:delText`) — the plain extraction gives you the accepted view.

## Extracting the negotiation history (tracked changes + comments)

A resubmission review needs Ane's prior asks. They live in two places:

- **Tracked changes:** `w:ins` / `w:del` elements in `word/document.xml`, each with `w:author` and `w:date`. Collect the text of `w:t` (insertions) and `w:delText` (deletions) per element.
- **Margin comments:** `word/comments.xml`, `w:comment` elements with `w:author`; text via the `w:t` descendants. The document body carries the anchors (`w:commentRangeStart/End`).

Each tracked insertion and each comment is one "ask" for the taken-up check. A run may be fragmented (one logical insertion split across several `w:ins` elements) — reassemble by adjacency before listing.

## Extracting a PDF offer

`pypdf` (`pip install pypdf` if absent):

```python
from pypdf import PdfReader
text = "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
```

PDF extraction mangles list numbering and table layout. Before flagging a "broken a)–f) list" or a column mismatch as a document defect, check whether it is an extraction artefact: consistent mid-sentence letters (e.g. "all production b) infrastructure accounts") indicate a genuine broken list; ragged table cells usually indicate extraction.

## Writing anchored margin comments (OFFER-REVIEW step 8)

Use `scripts/add_offer_comments.py`. It copies the vendor file to `<stem>_COMMENTS.docx`, then anchors each comment to the first paragraph containing a given match string. Requirements:

- python-docx ≥ 1.1.1 provides `Document.add_comment(runs, text, author, initials)`; anchor by passing the runs of the matched paragraph.
- Match strings must be unique enough to hit the intended paragraph — 5+ consecutive words from the target paragraph. The script errors on zero or multiple matches rather than guessing; tighten the match string and re-run.
- Author string: `"Ane Gasser (MEL review)"` for process/compliance comments, `"Ane Gasser PERSONAL"` for judgement questions — this mirrors how Ane separates them by hand.

## In-place docx edits that preserve hand edits (PACK-PROPAGATE step 3)

Ane takes ownership of pack documents: renames them, hand-edits phrasing, adds disclosure lines. Regenerating from a generator script destroys that. The proven pattern:

1. Re-list the folder immediately before editing (filenames drift mid-session).
2. Read the document, find the paragraph by matching its current text (not the text from an earlier session).
3. Rewrite `runs[0].text` with the corrected full paragraph text and clear the remaining runs — this keeps the paragraph's style but flattens character-level formatting, so prefer editing the single run containing the old value when the value sits in its own run.
4. **Sentence-count guard:** count sentences in the paragraph before and after the edit. A drop means the replacement swallowed content — a real incident dropped two compliance sentences silently. Restore and retry with a narrower span.

## Workbook mechanics (SCORE-COMPARE)

- **Formula linking:** point the official form's score cells at the working Evidence Matrix by cross-sheet reference (`='Evidence Matrix'!D7`). One edit point; form, benchmark and comparison tabs all follow.
- **Pre-link diff:** before landing the links, compare current form values against the matrix values cell by cell. Any divergence means the working sheet was revised after the form was filled — surface it (a real case: a bidder's score silently revised 89→75) and copy the workbook to a dated backup before linking.
- **`TEXTJOIN` in openpyxl** must be written with the `_xlfn.` prefix (`=_xlfn.TEXTJOIN(...)`) or Excel shows `#NAME?`. Same for other post-2013 functions (`IFS`, `XLOOKUP`).
- **Conditional formatting:** `openpyxl.formatting.rule.CellIsRule` / `FormulaRule` on the Diff and rank-shift columns. Red fill = diff ≥ 20% of criterion max or ≥10 total points; amber = 10–19% or 5–9 total. Derive the 20% from the template's own rating bands, not a hard-coded number.
- **`Criterion cards` sheet:** one row per criterion, columns `Criterion ID | What this asks for | Why it matters | What the bidder offered | Missing or unclear | Judgement | What would change it`. Set `alignment = Alignment(wrap_text=True, vertical="top")` on the text columns, column widths around 45 for fields 1 to 4 and 60 for field 3, and freeze panes at `B2`. Row heights: leave them unset so Excel autofits wrapped text; an explicit `row_dimensions[n].height` clips the card and hides evidence. Match `Criterion ID` to the comparison tab exactly so a red diff cell is one lookup from its card.
- **Bulk writes to locked ranges fail silently** under COM automation; openpyxl does not have that problem, but if a step must run through Excel COM (slicers, .osts), use Windows PowerShell 5.1 (`powershell.exe`, not pwsh 7) and verify each write landed.

## Verification block (all modes)

Every mode ends with a re-read: extract the written artefact fresh (comments copy, edited pack file, workbook) and confirm the intended change is present and nothing else moved. In OneDrive non-git folders also re-read after ~10 seconds — sync-revert shows up in that window.
