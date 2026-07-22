---
name: procurement-offer-review
description: 'Review an incoming supplier technical/financial offer against an IPPF ToR, and keep the internal procurement pack consistent. Use when Ane asks to "review this offer/proposal against the ToR", "is the final proposal aligned with the ToR and my comments", "check their revised offer", "add my comments to the offer", "propagate [a decision] across the procurement/waiver docs", "sweep the new figure across the pack", or "compare my scores with the AI scores" in a multi-bidder evaluation. Three modes: offer-review (clause-by-clause gap table vs the ToR and vs Ane''s prior comment round, arithmetic and VAT checks, residual issues ranked by cheapest fix, anchored Word margin comments on a _COMMENTS copy — never the vendor original), pack-propagate (apply one procurement decision across ToR, waiver justification, best-value note and acquisition checklist, with a residual scan and ⚠ Finance-to-confirm flags for compliance calls it never decides itself), score-compare (evaluator-vs-AI comparison tab and formula-linked single-source scoring workbook). Distinct from tor-procurement (drafts and grades the ToR itself, upstream of offers), /proposal (writes funding proposals TO donors), implementation-pack (post-award tracking), and accreditation-desk-review (MA compliance).'
model: opus
---

# /procurement-offer-review — review supplier offers, keep the pack consistent

One job: the receiving side of procurement. A supplier's technical and financial offer arrives against an IPPF ToR; this skill checks it, comments on it, keeps the internal pack (ToR, waiver justification, best-value note, acquisition checklist) internally consistent when a decision changes, and compares scores in multi-bidder evaluations. The drafting side (writing the ToR) is `tor-procurement`, upstream.

## Mode routing
- **OFFER-REVIEW** — an offer or revised offer arrived; Ane wants alignment checked against the ToR and, when one exists, against her prior comment round. Read-only on the vendor file; optionally writes a `_COMMENTS` copy.
- **PACK-PROPAGATE** — one procurement decision changed (contracting entity, budget figure, structure, dates); apply it consistently across every pack document.
- **SCORE-COMPARE** — a multi-bidder evaluation with a scoring workbook; build or link the evaluator-vs-AI comparison.

If the mode is ambiguous, ask in one line before working.

## Shared rules — all modes
- **Never edit the vendor's file.** The offer is the supplier's document. Comments go on a copy named `<original>_COMMENTS.docx`; analysis goes in chat or internal notes. If the offer is a PDF, comments go in the chat report (a PDF is the vendor's frozen record — that is a feature, not a problem: it also freezes out any stale margin comments).
- **Factual reliability.** Never invent or approximate a figure, entity name, SIREN/VAT number, date, or approval. Every figure in the report traces to a named document or a named confirmation. A gap is reported as a gap.
- **⚠ Finance-to-confirm convention.** This skill never asserts CERV, VAT, subcontracting, or procurement-manual compliance. It states what the documents say, names the tension, and flags `⚠ Finance to confirm: [question]`. Compliance calls belong to Finance and the waiver signatory.
- **Preserve originals.** Before touching any internal pack document, note its timestamp; write versioned or suffixed copies where the pack convention uses them. Ane hand-edits and renames pack files mid-session — re-list the folder and re-read each file immediately before editing it, never from an earlier read.
- **OneDrive revert hazard.** In non-git OneDrive folders, sync can silently revert a fresh write within seconds. After any file write, verify the content landed (re-read a changed line). In git folders, write and commit in one block.
- Extraction mechanics (docx text, tracked changes, comments XML, PDF text, openpyxl formulas) live in `references/docx-xlsx-mechanics.md`. Read it before writing any comment, in-place docx edit, or workbook formula.

## OFFER-REVIEW mode

Inputs: the offer (docx or PDF), the ToR it answers, and — when this is a resubmission — Ane's prior comment round (margin comments and/or tracked changes; extract both from the docx XML, they carry the negotiation history).

1. **Extract all three sources** before judging anything. For a resubmission, build the list of Ane's prior asks: each margin comment and each tracked insertion is one ask.
2. **Walk the ToR clause by clause.** For every ToR requirement (scope items, deliverables, budget lines, IP and handover, VAT declaration, safeguarding, reporting), classify the offer's response: **met / partial / missing / diverges**. Note offer content with no ToR basis separately — new scope items need a deliberate accept, especially anything touching security or access models.
3. **Check the arithmetic yourself.** Recompute every total: days × rate, VAT (net × rate = gross), sum of budget lines, and every ceiling figure against the approved amount. Figures that agree in the table but disagree on a cover page are a classic drift — check every occurrence of every figure, not the first.
4. **Verify the prior round.** For each of Ane's prior asks: taken up / partially / not taken up. Not-taken-up items are findings, not footnotes — they are the negotiation's open positions.
5. **Watch the known traps** (each cost a real review round): licence granted where the ToR requires assignment; a licence quietly narrowed ("within X network"); advance-payment trigger named differently in ToR and offer; deliverable timing moved without the payment schedule moving; a deferred component whose safety consequence is unstated (e.g. submissions with no approval gate); hosting/maintenance implied but never committed.
6. **Rank residual issues by cheapest fix**, in this order: (a) contract precedence — the contract states which document governs, no reissue; (b) one-line written confirmation by email; (c) vendor reissue — reserve for errors that would mislead a signatory or auditor. Minimising reissue rounds is a feature: every reissue costs a week.
7. **Deliver BLUF:** verdict sentence first (aligned / aligned with N residuals / not aligned), then what was taken up (confirmed line by line), then residual issues numbered with severity and fix route, then good news (scope gained, items resolved). Offer to draft the reply that carries the fix routes.
8. **Margin comments (on request, docx offers only).** Write anchored comments on the `_COMMENTS` copy via `scripts/add_offer_comments.py`. Anchor each comment to the specific paragraph it concerns; a comment anchored to the wrong paragraph is worse than none.

## PACK-PROPAGATE mode

One decision, many documents. The failure mode this mode exists for: a figure or entity changed in three files and silently survived in the fourth, or a whole-paragraph replacement dropped two sentences nobody noticed.

1. **State the decision as one line** before editing: old value → new value, and which documents carry it. Confirm with Ane if the decision was implied rather than stated.
2. **Inventory the pack.** List the folder fresh (filenames drift), then search every pack document for every occurrence of the old value — including derived forms (a VAT-inclusive figure derived from a net figure, a renamed entity's old abbreviation, an old date in a footer).
3. **Edit in place, smallest possible span.** Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when the target file exists: read first, edit scope-bounded, preserve everything outside the change byte-identical. For docx: match the paragraph text, rewrite the minimal run, keep Ane's hand edits. Never replace a whole paragraph to change one number — count sentences before and after; a mismatch means content was dropped.
4. **Residual scan.** After all edits, re-extract every pack document and search again for the old value and its derived forms. Report per file: changed (N occurrences) / already current / ⚠ residual found. The scan is the deliverable — an edit without the scan is half the job.
5. **Flag, don't decide.** Any edit that touches a compliance-bearing statement (procurement band, waiver ground, VAT treatment, donor rule) gets a `⚠ Finance to confirm` flag in the report, even when the edit itself is mechanical.

## SCORE-COMPARE mode

For multi-bidder evaluations with a scoring workbook (evaluator's working matrix + official evaluation form). Proven pattern; formulas and gotchas in `references/docx-xlsx-mechanics.md` § Workbook.

1. **Single source of truth first.** Link the official form's score cells (and any benchmark-duplicate sheet) by formula to the evaluator's working Evidence Matrix, so scores are edited once and every dependent sheet follows. **Before linking, diff the sheets** — a silent revision in the working sheet changes official scores the moment the link lands. Surface any divergence and back up the workbook first.
2. **Comparison tab:** side-by-side evaluator / AI / Diff per criterion, plus totals, ranks, and a threshold-agreement column. Flag rule anchored to the template's own rating bands: red = diff ≥ 20% of the criterion max (a full band) or 10+ total points; amber = 10–19% (or 5–9 total); separate flags for threshold divergence and rank shifts of 3+ places. Live formulas and conditional formatting, not pasted values.
3. **The comparison informs, the evaluator decides.** AI scores never overwrite evaluator scores; the tab exists so divergences get looked at, and the look is Ane's.

## Scope boundary
- Drafting or grading the ToR itself is `tor-procurement` (upstream). Post-award tracking is `implementation-pack`. Donor-facing proposals are `/proposal`.
- Contract drafting, signature routing, and the compliance calls behind every ⚠ flag stay with Finance, the budget holder, and the waiver signatory.
- Internal pack documents are internal: Tier 1 register, but no external-publication colophon needed. If a review output is sent to the supplier (comments copy, reply email), it is Ane's voice — collaborative, specific, no hedging.
