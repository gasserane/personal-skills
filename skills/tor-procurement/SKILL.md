---
name: tor-procurement
description: 'Build, review, grade and defend procurement Terms of Reference (ToRs) for consultancy and service contracts to open-market standard. Four modes: build (branded docx via a generator), review (a 1-10 grade with strong and weak points), respond (answer a named reviewer who objected to a ToR Ane wrote), finalise (apply revisions with edit-preservation). Use when Ane asks to "draft a ToR", "write terms of reference", "procurement ToR", "review this ToR", "grade this ToR", "harden this ToR before publication", "answer this comment on my ToR", "a reviewer objects to", "how do I respond to this comment", "is this objection fair", "reply to the comments on my terms of reference", or is preparing to contract a consultant or service provider. Distinct from /proposal (writes funding proposals TO donors, this procures FROM consultants), implementation-pack (post-award tracking), and accreditation-desk-review (MA compliance). To evaluate incoming supplier offers against a ToR, use procurement-offer-review. When Ane is the reviewer commenting on someone else drafted, that is the opposite direction and not this skill.'
model: opus
---

# /tor-procurement — build, review and grade procurement ToRs

One job: get a procurement ToR to open-market standard. The spine is `references/open-market-checklist.md` — 22 items that took the AI-for-Research ToR four revision rounds (v0.4→v0.7, July 2026) to reach by hand. A new ToR starts at that standard; an existing ToR is measured against it.

## Mode routing
- **build** — no ToR exists yet, or Ane wants a fresh start.
- **review** — a ToR exists; Ane wants strong/weak points and a grade. Read-only.
- **respond** — a named reviewer has commented a ToR Ane wrote and she needs to answer *them*. Produces reply text, not document edits. Hands to finalise only where a concession is agreed.
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

## Respond mode

The stage between review and finalise. A named reviewer has objected to a clause, and the job is to answer the person. **The correct outcome is usually no change to the document**: three of the four verdicts leave the ToR exactly as published.

| Verdict | What it says | Does the ToR change |
|---|---|---|
| **defend** | The clause is right as written, and here is what it actually says. | No |
| **concede** | The reviewer is right. Name the minimal edit, nothing wider. | Yes |
| **defer** | The point is legitimate and does not fit this contract. Size the follow-on. | No |
| **escalate** | This is a governance question the ToR cannot settle. Name the owner. | No |

A compound answer takes a primary verdict plus one secondary. **defend + defer** is the reference case: the clause stands, and the work the reviewer wants gets sized as a separate contract. **defend + concede** is refused, because a clause cannot be both right as written and in need of an edit.

### Steps

1. **Read the ToR and `references/open-market-checklist.md`.** An objection is often the checklist arriving from outside.
2. **Extract the objections.** `python scripts/tor_respond.py extract "<ToR>.docx" --json round.json`. It reports each thread, the section it sits in, and whether it is already answered. Three things it tells you that a comment list does not:
   - **The anchor is not the clause.** A reviewer selects a phrase and writes about the argument behind it. Read the section, not only the highlighted words, before drafting.
   - **Her own margin notes are separated out.** They are working notes, not objections; nobody is waiting on a reply.
   - **`also commented here`** names anyone who commented on the same paragraph in a separate thread. Word records a reply as a reply only when the reply button was used, so an answer she already typed can sit beside the objection looking like a new comment. Read it before answering twice.
3. **State the strongest version of the objection before answering it** (challenge-by-default). Answering the weakest reading is how one objection becomes four rounds. Where the reviewer is right, concede; a defence of everything convinces nobody.
4. **Answer from what the documents say** (factual reliability). Every defence cites the ToR section or the governance document it rests on. Never assert an institutional fact you cannot source: a 2026-07-31 draft reply carried a "we may not have a DPO" aside that was never checked and would have gone to an external reader as fact. The guard refuses a defence that cites nothing.
5. **Draft the reply at two lengths.** Full for an email or a meeting; compact for the Word comment pane, where a reply that does not fit on a glance does not get read. Ceilings default to 500 and 180 words and are settings, not constants.
6. **Where the verdict defers, size the follow-on.** Scope options, how the consultant profile differs, indicative bands marked uncosted, and the trigger condition that would justify commissioning it. Answering a legitimate point with a prohibition invites the next round; answering it with a plan closes it.
7. **Compile.** `python scripts/tor_respond.py compile round.json --out <dir> --docx`. Writes `replies.md` (both lengths per objection, with the sizing sketch) and `response-register.md` (one row per objection, plus the revision list finalise mode takes). `--docx` renders both as branded Word.

### What the guards refuse

`compile` runs every guard before writing and **refuses a round that contradicts itself**, because finalise mode would act on it. Blocking: a contradictory verdict pair, an edit attached to anything but a concession, a concession naming no edit, a deferral that never sizes its follow-on, a defence citing no source, an empty reply, an option estimated at zero days. Warning only, and still written: an overlong reply, a missing steelman, and the standing prose findings (hedging, filler, em-dashes) from `ane_package.qa.prose_lint`.

The line sits where a mistake reaches someone other than Ane. Length and voice are craft she can fix in the pane. A contradiction or an unsourced claim goes to a named external reviewer and costs more to retract than to catch. `--force` overrides, and says so.

**Nothing is invented in a sizing sketch.** An option nobody estimated stays uncosted rather than costing zero, and the procurement route is assessed only against a threshold that was supplied. The skill holds no threshold of its own.

### After responding

Conceded objections, and only those, become finalise mode's revision list. Everything else closes with the reply. If Ane sends the replies as Word comment replies, she pastes them; this mode does not write into her document.

## Finalise mode
1. Confirm the agreed revision list (from the review or from Ane). Scope is that list, nothing more.
2. Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists — Ane's current content is the canonical baseline; read first, edit scope-bounded via the Edit tool, preserve everything out of scope byte-identical, report out-of-scope observations in the EDIT-PRESERVATION DELIVERY format. Never regenerate from scratch.
3. For docx deliverables, the edit target is the generator source: copy the current `gen_tor_v0N` to `v0N+1`, apply the agreed edits there, re-run, report the new docx path. Never edit the docx binary.
4. Close by listing each agreed item and where it landed, plus any prep-note items still open before publication.

## Scope boundary
- Publication on the procurement channel, finance and VAT confirmation, contracting entity, and legal sign-off stay with their owners — the ToR carries their placeholders until they confirm.
- Replying to a reviewer who commented Ane's own ToR is respond mode, above. **Reviewing a third party's draft that Ane has commented runs the opposite direction** and is not this skill: there she is the reviewer, here she is the author answering inbound comments. Do not rebuild either from the other.
- Evaluating received offers and keeping a waiver pack consistent is the next lifecycle phase (`procurement-offer-review`, built 2026-07-22) — not this skill.
- A ToR published outside IPPF is an AI-assisted publication: offer the standard colophon per mel_wiki/wiki/concepts/ai-use-in-publications.md (routine grammar-only edits exempt).
