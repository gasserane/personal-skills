# Image-based deck export mode

For a slide deck or e-learning module exported to Word, where the translatable
text is rasterised inside the slide images and the document body holds only
slide titles and layer labels. An Articulate Storyline export is the usual case.

An ordinary text review reads this document, finds three words per slide, and
reports it clean. Nothing in the body is the translation. So the mode reads the
images instead, hangs each comment on the slide title beside them, and delivers
a corrections sheet as the actionable worklist, because the fix happens in the
source deck and not in the Word file.

Two structural variants, both handled: the plain one (`word/document.xml` plus
`word/media/`) and the Storyline one (`word/document2.xml`, media at the package
root, images stored as `.bin`, an `afchunk.dat` alongside). The main part is
resolved through the package relationships, never guessed.

## Flow

**1. Confirm the input is a deck export and pull the slides.**

```
python scripts/extract_deck.py extract DECK.docx --out-dir slides/ [--en-offset N]
```

Prints the slide table: slide number, anchor paragraph, English page, image file,
size. `--en-offset N` maps slide *N* to English source page *N + offset*; leave
it off and the English page column stays empty rather than being invented. Add
`--json` for the machine-readable manifest.

If the verdict is `Deck export: NO`, stop and review the document as an ordinary
target-language draft (mode 3). The evidence behind the verdict is printed with
it, so a borderline document can be argued with.

**2. Read each slide image against the English source.**

Read the written images with the Read tool, one at a time, against the matching
pages of the English source. Apply the ordinary localise core unchanged: the
glossary in `mel_wiki/wiki/glossaries/srhr-terminology-<lang>.md`, controlled
terminology, register preservation, the safeguarding pass on sensitive terms.
Skip the images the extract marked as navigation chrome, after opening one to
confirm it holds no translatable text.

Write the findings to a JSON file:

```json
[
  {"slide": 7, "type": "Terminology", "en_page": 19,
   "en_source": "sexual and reproductive health and rights",
   "current": "santé sexuelle",
   "proposed": "santé et droits sexuels et reproductifs",
   "why": "Drops the rights half of the term, against the controlled glossary.",
   "severity": "High"}
]
```

`slide` is required and keys everything. `type` of `Data gap`, `Query` or
`Question` routes that finding to the sheet only, never to a comment. Severity
defaults to `Medium`; `High`, `Medium` and `Low` colour on the sheet and anything
else is written plainly rather than refused.

**3. Write the comments and the corrections sheet.**

```
python scripts/extract_deck.py comment DECK.docx --findings findings.json --out DECK_REVIEWED.docx
python scripts/extract_deck.py sheet   DECK.docx --findings findings.json --out corrections.xlsx --date DD/MM/YYYY
```

Comments are written to a copy; the original is never touched. Findings on one
slide merge into one balloon, because Word stacks separate comments on the same
paragraph into an unreadable pile. Every finding that could not be anchored is
printed to stderr with its reason, and it still reaches the sheet.

The sheet is IPPF-branded via `ane_package.reporting.excel_templates.build_review_worklist`:
Slide · EN page · Type · EN source · Current · Proposed · Why · Severity, frozen
header, autofilter, severity colour-coded.

## Things that will bite

**A comment cannot sit on text inside an image.** It hangs on that slide's title
paragraph instead, and `officeops.add_comments` matches paragraphs by text. A
title repeated across slides therefore cannot carry a comment at all. The extract
reports those collisions before anything is written; those findings go to the
sheet only. Do not work around it by matching a longer string that happens to be
unique, because the comment then lands on a paragraph the reader is not looking at.

**Slide numbers come from the deck's own labels, in the language under review.**
`Diapositive 7`, `Diapozitiv 7`, `Diapositiva 7`, `Слайд 7` and `Folie 7` all key
slide 7. Where a slide carries no label the manifest falls back to image order
and says so under "Slides keyed by image order" — check those against the deck
before keying the sheet, because one slide holding two images shifts every
number after it.

**Navigation chrome repeats and is set aside, not deleted.** An image whose bytes
appear on three or more slides is treated as furniture. It stays in the manifest,
marked, and is counted in the summary line.

**Comments are English; only the renderings are in the target language.** The
current and proposed strings sit in « guillemets »; everything around them is
English, because the comment addresses the reviewer. No per-comment boilerplate
about the image.

**Verify the written file, never the call.** After `comment`, reopen the copy and
check the comment count against Word before sending it, and confirm no package
parts were dropped on save. These exports have an unusual package and a naive
rewrite can lose the media.

## Where this mode stops

It does not edit the deck. Corrections are applied in the source Storyline or
PowerPoint file and re-exported by whoever owns it, which is why the sheet is the
deliverable that matters and the commented Word file is the supporting evidence.

It does not read the English source for you: pairing slides to English pages is a
judgement, and `--en-offset` only helps where the mapping is a constant shift.
