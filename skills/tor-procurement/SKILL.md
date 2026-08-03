---
name: tor-procurement
description: 'Build, review and grade procurement Terms of Reference (ToRs) for consultancy and service contracts to open-market standard. Three modes: build (branded docx via a generator), review (two-lens analysis, strong and weak points, a 1-10 grade with a self-grading bias note), finalise (apply revisions with edit-preservation). Use when Ane asks to "draft a ToR", "write terms of reference", "procurement ToR", "review this ToR", "grade this ToR", "harden this ToR before publication", or is preparing to contract a consultant or service provider. Distinct from /proposal (writes funding proposals TO donors, this procures FROM consultants), implementation-pack (post-award tracking), and accreditation-desk-review (MA compliance). To evaluate incoming supplier offers against a ToR, use procurement-offer-review.'
model: opus
---

# /tor-procurement — build, review and grade procurement ToRs

One job: get a procurement ToR to open-market standard. The spine is `references/open-market-checklist.md` — 22 items that took the AI-for-Research ToR four revision rounds (v0.4→v0.7, July 2026) to reach by hand. A new ToR starts at that standard; an existing ToR is measured against it.

## Mode routing
- **build** — no ToR exists yet, or Ane wants a fresh start.
- **review** — a ToR exists; Ane wants strong/weak points and a grade. Read-only.
- **finalise** — a review happened or Ane brings agreed revisions; apply them, nothing else.

If the mode is ambiguous, ask in one line before working.

## Shared rules — all modes
- Read `references/open-market-checklist.md` before touching the ToR.
- **Factual reliability.** Never invent a budget figure, name, date, address, or funding source. Anything unconfirmed goes in square brackets AND into the "Internal preparation note — REMOVE BEFORE PUBLICATION" strip list (checklist item 21). A plausible placeholder in a published ToR can be acted on as if true.
- **Intake before building.** Confirm the critical facts with Ane before constructing anything; working files go stale (session-efficiency protocol).
- A published ToR is external-facing: Tier 1 plain English, translatability test (bidders are often non-native readers), acronyms spelled on first use.
- When the ToR carries MEL content (indicators, evaluation design, learning questions), citation standards apply via /mel-framework-citation.

## Build mode
1. **Intake** — one batched message asking the five critical facts: (a) what is procured and the deliverables; (b) budget ceiling, VAT treatment, funding sources, any donor spend deadlines; (c) timeline anchors — publish date, contract-by date, final acceptance date; (d) evaluation panel and who covers Q&A during any leave; (e) contract type — individual/team/firm, consultancy vs service, open market vs single-source waiver.
2. **Walk the checklist** — apply every item or record why it does not apply (adaptation notes cover service contracts and waivers). Sanity-check the ceiling against realistic senior days before drafting; if they are in tension, say so — underbidding is the main evaluation watch point.
3. **Emit** — copy `scripts/tor_docx.py` into the project as `<project>/generators/gen_tor_v01_docx.py`, keep the builder unchanged, write the ToR body as linear builder calls in the canonical section order, run it, confirm the docx renders. The generator next to the deliverable is the source of truth; never dual-edit the docx. Version filenames v0.1, v0.2, upward.
4. **Verify the written file, not the run** — reopen the saved docx and assert the header part, the logo relationship and the footer strip are present. A generator that exits cleanly proves nothing about branding: v0.4 to v0.9 of the AI-for-Research ToR all reported success and all shipped unbranded, because the builder started from a blank `Document()`. `python scripts/test_tor_docx.py` runs these assertions against both header modes.
5. **Deliver** — docx path, generator path, checklist items needing an Ane decision, and the open prep-note items.

**Why the builder opens the letterhead.** Fonts and colours can be set in code, but the logo, the header contact block and the pillar footer strip exist only inside `ippf_en_letterhead_base.docx`. So `TorBuilder` opens that asset and clears the body while keeping the section properties, and imports brand values from `ane_package.reporting.brand` rather than restating them — a mirrored colour in a builder cannot know when the template moves, which is why the project CLAUDE.md treats it as grounds for QA rejection.

**Header modes.** `TorBuilder(header="slim")` is the default and is what a multi-page ToR wants: brand band plus logo, with the contact block removed so it does not eat the top of every page. `header="full"` keeps the contact block, which suits a one-page cover note. Run the generator with `--header full|slim` to switch.

**Two traps the builder already handles** — leave them alone unless you have tested the alternative. The letterhead ships no `Table Grid`, `List Bullet` or `List Number` style, so tables draw their own borders and lists write their own glyphs; reaching for those style names raises `KeyError`, and catching it after the fact leaves an orphan paragraph behind, which is what once doubled every bullet. And the contact block is stored twice, as an `mc:Choice` drawing and an `mc:Fallback` VML twin, so slim mode removes the whole `mc:AlternateContent` parent — removing only the drawing leaves the text still rendering.

**If the generator cannot find `ane_package`**, set `WORK_FOLDER_ROOT` to the work folder. The builder resolves that variable first, then walks up from its own location. It refuses loudly rather than falling back to hard-coded brand values, because a silent fallback is how unbranded files shipped looking fine.

## Review mode
Read-only: this mode never edits the ToR. For docx input, extract the text first (python-docx read); for markdown or generator source, read directly.
1. Read the ToR and the checklist.
2. **Lens 1 — senior acquisition officer.** Process defensibility and money: checklist groups A, B, C, E. Would this survive a challenge from a losing bidder, an auditor, or the donor?
3. **Lens 2 — topic expert** in the assignment domain. Scope realism, acceptance criteria, day-realism against the ceiling, method fit, whether a strong consultant could price this correctly from the text alone.
4. **Output**, BLUF first: verdict sentence; strong points; weak points each mapped to a checklist item with proposed fix wording; grade 1-10; bias note.

Grade anchors: 5 or below = not publishable, structural gaps; 6-7 = publishable after the named fixes; 8 = open-market standard; 9-10 = reserved for ToRs that have survived an external read. Mandatory bias note, always:

> Self-graded N/10 by the same model that worked on this document — treat as an upper bound. External read of sections [weakest sections] by [named colleague] recommended before publication.

## Finalise mode
1. Confirm the agreed revision list (from the review or from Ane). Scope is that list, nothing more.
2. Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists — Ane's current content is the canonical baseline; read first, edit scope-bounded via the Edit tool, preserve everything out of scope byte-identical, report out-of-scope observations in the EDIT-PRESERVATION DELIVERY format. Never regenerate from scratch.
3. For docx deliverables, the edit target is the generator source: copy the current `gen_tor_v0N` to `v0N+1`, apply the agreed edits there, re-run, report the new docx path. Never edit the docx binary.
4. Close by listing each agreed item and where it landed, plus any prep-note items still open before publication.

## Scope boundary
- Publication on the procurement channel, finance and VAT confirmation, contracting entity, and legal sign-off stay with their owners — the ToR carries their placeholders until they confirm.
- Evaluating received offers and keeping a waiver pack consistent is the next lifecycle phase (`procurement-offer-review`, built 2026-07-22) — not this skill.
- A ToR published outside IPPF is an AI-assisted publication: offer the standard colophon per mel_wiki/wiki/concepts/ai-use-in-publications.md (routine grammar-only edits exempt).
