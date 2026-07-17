---
name: tor-procurement
description: 'Build, review and grade procurement Terms of Reference (ToRs) for consultancy and service contracts to open-market standard. Use when Ane asks to "draft a ToR", "write terms of reference", "procurement ToR", "review this ToR", "grade this ToR", "harden this ToR before publication", or is preparing to contract a consultant or service provider. Three modes: build (batched intake, then a branded docx ToR via a python-docx generator saved next to the deliverable), review (read-only two-lens analysis, senior acquisition officer plus topic expert, strong and weak points against the open-market checklist, a 1-10 grade with a mandatory self-grading bias note), finalise (apply agreed revisions to the generator source with edit-preservation). Encodes the open-market checklist proven on the AI-for-Research ToR v0.4 to v0.7 cycle of July 2026. Distinct from /proposal (writes funding proposals TO donors, this procures FROM consultants), implementation-pack (post-award tracking), and accreditation-desk-review (MA compliance). Evaluating incoming supplier offers against a ToR is the next lifecycle phase (procurement-offer-review, backlogged, not this skill).'
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
4. **Deliver** — docx path, generator path, checklist items needing an Ane decision, and the open prep-note items.

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
- Evaluating received offers and keeping a waiver pack consistent is the next lifecycle phase (`procurement-offer-review`, backlogged 2026-07-01) — not this skill.
- A ToR published outside IPPF is an AI-assisted publication: offer the standard colophon per mel_wiki/wiki/concepts/ai-use-in-publications.md (routine grammar-only edits exempt).
