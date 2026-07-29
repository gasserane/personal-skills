---
name: donor-proposal-scoring
description: 'Score a written grant proposal against the donor published award criteria, and calibrate that scoring against the donor own Evaluation Summary Report (ESR) when one exists. Use whenever Ane says "score this proposal", "how would the donor score this", "assess our application against the call criteria", "will this pass the threshold", "where would we lose points", "review our CERV / Erasmus / Horizon application before resubmission", "compare my scoring with the donor evaluation", "how close was I to the donor score", or hands over a call document plus a submitted proposal. Two modes. SCORE extracts the criteria, weightings and every threshold from the call document only, lists them in full before scoring anything, then scores criterion by criterion with named evidence, a point estimate plus an honest range, a rights-holder coverage pass, a lens-substantiveness test applied to the proposal itself, and a fix list ranked by points recoverable against effort. CALIBRATE puts the scoring and the donor ESR side by side per criterion, tags every strong point and recommendation Donor / Mine / Both, never revises the original scores, and closes with a verdict on total error, range coverage, criterion ranking and the pass-fail call. Outputs markdown, with an optional IPPF-branded Word export. Distinct from /proposal (writes proposals TO donors, this scores one already written), procurement-offer-review and tor-procurement (the buying side, supplier offers against a ToR), accreditation-desk-review (Member Associations against IPPF standards, not applicants against donor criteria), and check-deliverable (a QA gate on a finished text, not a scored assessment against an external grid).'
model: opus
---

# /donor-proposal-scoring — score a proposal against the donor grid

One job: take a proposal that has already been written, and say what a donor evaluator would score it and why. Writing proposals is `/proposal`. Evaluating supplier offers is `procurement-offer-review`. This is the applicant side, looking at its own submission through the donor eyes.

## Mode routing

- **SCORE** (default) — a call document and a proposal exist; produce a criterion-by-criterion assessment with scores, evidence, a range, and a ranked fix list.
- **CALIBRATE** — the donor Evaluation Summary Report has arrived and a prior scoring exists; compare them and learn from the gap.

If both documents are present and Ane has not said which mode, ask in one line. Never run CALIBRATE material into a SCORE output: reading the donor first destroys the test.

## Two things to settle before anything else

**Is this a blind test or live advisory work?** They need opposite reading orders.

- **Blind test** (an ESR exists and the point is to check the method): do not open it. Do not open it to "just check the format". Write the scoring to disk, then compare.
- **Live advisory** (the proposal is being fixed before submission or resubmission): read every prior ESR from the same donor **first**. A donor evaluation house style is learnable and it is the cheapest accuracy available. What did this donor praise, what did it always ask for, which populations did it name unprompted, what did it never mention. Then score.

**Whose proposal is it?** If the applicant is IPPF or Ane own team, this is partly self-assessment and independence is limited by construction. Say so in the output, in the opening notes, not in a footnote. Search the proposal for Ane name and say whether she appears in it and in what role. Score from the call wording, not from what you know the organisation meant.

## Shared rules — both modes

- **Criteria come from the call document and nothing else.** Not from last year of the same call, not from the application form instructions, not from recall. Call documents change wording, weightings and thresholds between years, and a criterion carried over from memory is a fabricated criterion. If the call document is missing, say so and stop; do not reconstruct it.
- **Factual reliability.** Every score claim names the proposal section or page it rests on. Every criterion claim names the call page. A figure you cannot locate is a gap, reported as a gap. Never approximate a budget line, a threshold, or a date.
- **Never fabricate what a donor would think.** The output says what the call document scores and what the proposal contains. Where the leap to "an evaluator would therefore deduct points" is inference, mark it as inference.
- **Tier 1 working brief.** The reader is management or a proposal lead, not an evaluation specialist. BLUF, plain English, acronyms spelled out on first use, no framework name-dropping in the running text. Citations sit in an `**Evidence base:**` line at the end.
- **Edit-preservation.** Apply `mel_wiki/wiki/concepts/edit-preservation-protocol.md` whenever a target file already exists. Once Ane has hand-edited a scoring output or its Word version, the generator is stale: edit her file in place, never re-run the builder to "refresh" it.
- **OneDrive.** Write and commit in the same block in git folders; in plain OneDrive folders, re-read a changed line after writing to confirm it landed.

---

# SCORE mode

## Step 0. Blind-run hygiene

Before opening anything, list the folder holding the supplied documents and match every file against `*ESR*`, `*evaluation*summary*`, `*evaluation*report*`. If one is there, name it in the output, state that it will not be opened, and recommend moving it out of the run scope before scoring starts. Restraint is not a control. A reader cannot verify that a file sitting in scope went unread, and in a live demonstration that gap is the whole difference between a test and a claim.

## Step 1. Extract the grid, and list it before scoring anything

Read the call document award-criteria section. Produce, in the output, before any judgement appears:

- every criterion, with its **maximum points**
- every **individual pass threshold** and the **overall threshold**
- the **tie-break order** if the call states one
- the elements each criterion covers, **in the call own words**, quoted or closely paraphrased
- whether passing means funding, or only means being ranked inside a capped envelope

This is a hard sequence gate, and the reason is not bureaucratic. Scoring is easy to run backwards: once a total feels right, the per-criterion numbers bend to reach it. Writing the grid out in full, in public, before the first score exists, is what stops that. It also catches the case where the call scores something under a criterion you would have filed elsewhere, which is a common and expensive misreading.

State plainly which page of the call document each element came from.

## Step 2. Score the programme before you score the document

Two passes, in this order. The order is the single most consequential instruction in this skill.

**Pass A, programmatic substance.** What does this programme actually do, for whom, and is it worked through?

- Which rights-holders and populations are covered, and which are named but not served (Step 3).
- Do the declared approaches change the design, or only appear in it (Step 4).
- Who runs each mechanism, with what capacity, and what happens if they leave (Step 5).
- Is the stated pathway from activities to change credible, and does the measurement framework track any of it.
- Is the sustainability answer an answer, or a restatement of alignment.

**Pass B, document mechanics.** Internal consistency, arithmetic, section placement, literal compliance with checklists, missing annexes, undocumented budget lines.

Both passes produce real findings. But donor evaluators write about Pass A, and Pass A is what decides funding. Pass B findings are cheap to generate, feel rigorous, and were the bulk of what a real run got wrong (see `references/cerv-2026-worked-example.md`).

**Balance check before delivery.** Count your findings. If more than half sit in Pass B, you scored the document rather than the programme. Go back to Pass A. This check takes thirty seconds and is the highest-yield thing in the skill.

## Step 3. The rights-holder coverage pass

Run this against every proposal, whether or not the call names these groups. Donors in the rights and equality space apply them as standard, and several carry dedicated status fields on the evaluation form.

For each group: is it **named**, is the **approach specified**, does the **monitoring framework track it**, is there **specific outreach**. A group named in a target-population list and absent everywhere else is a finding, not coverage.

Children and the UN Convention on the Rights of the Child · age bands for adolescents · disability · refugees and migrants · rural populations · Roma and other minoritised ethnic groups · LGBTIQ people.

Full prompts per group, and which criterion each usually bites under, are in `references/rights-holder-coverage.md`. Read it during Pass A, not as a final check.

Child rights deserves separate emphasis because it is the most commonly missed and the most commonly scored. It appears under relevance (is the Convention cited, are age bands given), under quality (is child rights in the monitoring framework, is safeguarding enforced across partners rather than only adopted), and under impact (is there child-specific outreach). Missing it once usually means missing it three times.

## Step 4. The lens-substantiveness test, applied to the proposal

A lens that does not change the analysis is a failure equal to omission. That rule is already the standard applied to our own writing. Apply it to the artefact under review.

For each lens the proposal declares — intersectionality, gender-transformative, participatory, decolonial, rights-based, do-no-harm — find the sentence where it changes what the programme **does**. Not where it is named. Not where it is listed among principles.

The test question, in the donor own framing: does the proposal show **how intersecting identities affect access**, or does it say intersectionality is important. Does it place itself on the gender continuum with evidence, or does it call itself gender-transformative. Does it say who takes part in the evaluation and how, or does it call the evaluation participatory.

Where the lens appears without changing anything, that is a finding, and it usually costs points under the criterion that names gender perspective or inclusion as a scored element. Where the lens genuinely changes the design, say where, because that is a strong point worth defending.

Watch the opposite error too: crediting a framing at face value because it is well written. A well-written statement of intersectional commitment scores nothing if the needs assessment carries no disaggregated data and no evidence that the communities concerned were consulted.

## Step 5. The who-runs-this test

For each major mechanism — sub-granting, the evaluation, a pilot, a campaign, a capacity-building stream — ask three questions:

1. **Which named role delivers it?** Not which organisation. Which post.
2. **With what capacity?** Is the staffing proportionate to the money and the timeline. A sub-granting scheme worth a fifth of the budget, disbursed across many grants in a compressed window, needs named staffing.
3. **What is the contingency?** If a key person leaves, what happens.

This exists because a real run audited a sub-granting scheme control by control, in detail, and never asked who operates it. The donor two sub-granting concerns were both staffing. Controls without operators is the classic gap in an otherwise strong proposal, and it is invisible unless you ask the question directly.

## Step 6. Score criterion by criterion

For each criterion, in the call own order, write four things:

1. **The score**, out of the maximum, with the threshold result where one applies.
2. **What earned it.** The evidence in the proposal, with section or page numbers. Quote the load-bearing phrase where exact wording decides the judgement.
3. **What would have earned more.** Each gap as its own item, named plainly.
4. **Sections to fix.** The named proposal sections, so the fix list is actionable without re-reading.

Two disciplines while scoring:

**Search the whole document before calling anything absent.** Evaluators read across sections and credit material wherever it sits. Before writing "the proposal does not address X", search every part of the submission, including annexes, policies and the institutional description. An element the applicant covers through a standing institutional system described elsewhere will usually be treated as covered. This one habit would have prevented the largest cluster of errors in the worked example.

**Tag each finding with confidence.** High means an evaluator would almost certainly agree. Medium means defensible but arguable. Low means this depends on how literally the evaluator reads a checklist. Findings of the form "this is in the wrong section" or "this checklist item is not restated here" are **low confidence by default**, because evaluators form holistic judgements about competent applicants. Say so rather than ranking them first.

## Step 7. Give a range, not a number

Publish the point estimate and a realistic range side by side, and say what the bottom of the range means.

Expert evaluators scoring the same proposal routinely vary by five to ten points. A bare total is false precision, and false precision on a pass-fail decision is worse than no number. Where a threshold sits inside the range, say explicitly that the lower end fails.

Rank order matters more than the total. State which criterion you judge strongest and weakest, because that is the claim a fix list depends on, and it is the claim most often wrong.

## Step 8. Two registers, kept separate

Produce **two lists**, never one merged ranking. Merging them is how a zero-point item gets ranked as the top fix.

**Register A — scored findings.** Things that change the score. Ranked by points recoverable against effort. Each row: proposal section, the change, the criterion affected, estimated points, confidence, and whether it needs **new evidence** or is **rewriting work**. Rewriting-work items are the ones a proposal lead can act on this week.

**Register B — pre-signature and implementation items.** Things worth zero points that still matter: control gaps to close before grant preparation, ceilings with no headroom, compliance risks, arithmetic that will confuse an auditor later. Label the register plainly so nobody reads it as a score-loss list.

A literal reading of a call control checklist reliably generates Register B items that look like Register A items. In the worked example, seven such findings were ranked as the second-priority score fix and the donor scored that section as fully compliant. They were still worth fixing. They were worth zero points.

## Step 9. Say what you could not verify

Text extraction loses things. List them as check-the-original items, never as asserted findings:

- shaded or coloured timetables and Gantt grids
- organisational charts, diagrams and any figure submitted as an image
- budget tables whose column alignment does not survive extraction
- cross-references between a portal form (Part A) and the narrative (Part B)
- anything the call scores that you could not locate at all

For each, say what it would cost if the concern turns out to be real. An unverifiable item that would outrank every fix on the list deserves that sentence.

## Step 10. Deliver

BLUF: the verdict sentence, then the load-bearing reason. Then the five things to know. Then the notes on bias and uncertainty. Then the grid, the criterion scoring, the two registers, the unverified list, and the evidence base.

Write the file, then offer the Word export (see Outputs).

---

# CALIBRATE mode

The donor ESR has arrived. The value of this mode is entirely in its honesty, and the honesty is fragile.

## Rule zero

**Never revise the original scores.** Show both, unchanged. Quiet retrofitting destroys the only thing the comparison is for, and it is tempting precisely because it makes the output look better. Reproduce the prior scoring exactly as published and say in the header that nothing was revised.

**The ESR path is always supplied, never discovered.** Ane names the file. Do not scan a folder for it and do not open a candidate noticed while doing something else. Folder scanning is how an ESR ends up read during a SCORE run.

## Structure

1. **Headline scores table.** Criterion, maximum, threshold, my score, donor score, difference, and both as percentages of the maximum. Percentages matter: a three-point gap on a twenty-point criterion is a different failure from a three-point gap on forty.

2. **One section per criterion**, each with two tables and a short analysis:
   - **Strong points**, every row tagged `[Donor]` / `[Mine]` / `[Both]`
   - **Improvement recommendations**, same tags
   - **Why we differ here**, in prose: what kind of thing did the donor see that I did not, and what did I see that the donor did not care about

   Tag every row. An untagged table is just a merged list and it hides exactly the pattern the exercise exists to find.

3. **Where we agreed.** Convergent findings reached independently from the same documents are the ones worth trusting. Say which, and where each was filed.

4. **Where I was wrong, stated plainly.** Each contradicted finding, the priority it was given, and the donor verdict in the donor own words. Then one paragraph on the mechanism: were these fabricated, or real features of the document that were mis-weighted. Mis-weighting is the usual answer, and naming it is more useful than an apology.

5. **What I missed entirely.** Each donor finding absent from the scoring, which criterion it sat under, and **why it was missed**. This column is the point of the whole section. "Not considered" is an acceptable honest entry. Cluster the misses: if four of nine sit in one category, name the category as a systematic blind spot and say what would have caught it.

6. **Calibration verdict.** A table:
   - total score error, in points and as a percentage
   - whether the published range contained the true value, and where in the range
   - per-criterion direction, generous or harsh, one line each
   - **criterion ranking: right or wrong** — this matters more than the total, because the fix list is built on the ranking
   - pass or fail conclusion: right or wrong
   - counts: findings contradicted, substantive areas missed, findings independently confirmed

7. **The pattern in one line**, then **what this means for using the method**: what it is good for, what it must not be used for, and what to fix before the next run.

## What calibrate is for

Score prediction is not the deliverable and should be named as not the deliverable. A method that lands four points off, with seven contradicted findings and a wrong criterion ranking, is not a forecasting tool. The value is the fix list, the convergent findings, and the record of the blind spots. Say this in the output rather than letting a reader infer a precision that is not there.

Every calibration run should end by naming what changes in the next run. Feed those back into this skill.

---

# Outputs

**Markdown is canonical.** Write it first, to the folder holding the source documents unless Ane names another.

- SCORE: `<call-or-programme-slug>-proposal-scoring.md`
- CALIBRATE: `<call-or-programme-slug>-scoring-vs-donor-comparison.md`

**Offer an IPPF-branded Word export both times**, and pick the builder by shape. The two shapes need different tools and using the wrong one produces a cramped document:

- **Narrative scoring** → `write_word_report` from `ane_package.reporting.word_export`. BLUF bullets, sections with plain summaries and bullets, finding cards for the scores, method note, glossary.
- **Table-first calibration** → build directly on `_open_branded_base()` with python-docx. `WordReport` finding cards carry only two columns, and the comparison needs three to six.

Recipes, the exact import lists, the branded-table helper and the glossary pattern are in `references/word-export.md`. Brand values come from `ane_package.reporting.brand.IPPF_FORMAT_TEMPLATE`; hard-coding a colour, font or number format is a regression.

Every generator carries an edit-preservation staleness warning in its docstring, naming the .docx it builds and pointing at `mel_wiki/wiki/concepts/edit-preservation-protocol.md`. Apply that protocol whenever the target file already exists.

**AI disclosure.** Both outputs close with the disclosure line: the model, that scoring judgement and recommendations need human verification before use, and that AI is not an author and not a source. For a blind run, state that the donor evaluation was present and deliberately not opened, because that sequence is what makes the comparison a test rather than a reconstruction.

**Say which kind of blind.** The method note states either **structurally blind**, meaning the donor evaluation was absent from the run scope, or **blind by restraint**, meaning it sat in the folder and was not opened. These are not equally strong claims. The first a reader can verify; the second rests on the operator word, so name it as such rather than letting "blind" carry the stronger reading.

**Glossary.** Non-specialist readers get every term glossed: the call vocabulary (award criteria, threshold, call fiche, funding rate, work package, milestone, deliverable, dissemination level, sub-granting or FSTP, Declaration of Honour) and the MEL vocabulary (baseline, indicator, outcome, output, theory of change).

---

# Composing with specialists

Do not re-implement what the specialists already do. Spawn them where their judgement is the scoring judgement:

- `proposal-architect` — award-criterion mapping, logframe-budget-workplan coherence, donor compliance
- `safeguarding-reviewer` — child protection, the UN Convention on the Rights of the Child, do-no-harm, safeguarding enforcement across partners
- `intersectionality-analyst` — the lens-substantiveness test at Step 4, interaction effects rather than parallel disaggregation
- `srhr-indicator-designer` — indicator quality, disaggregation, whether the measurement framework tracks the outcomes the proposal promises

For a large or high-stakes proposal, run the coverage pass and the lens test as specialist spawns in parallel with the criterion scoring. For a quick check, run them inline.

---

# Scope boundary

- Writing a proposal is `/proposal`. Grading a Terms of Reference is `tor-procurement`. Reviewing an incoming supplier offer is `procurement-offer-review`. Scoring a Member Association against IPPF accreditation standards is `accreditation-desk-review`. A QA gate on a finished text is `check-deliverable`.
- This skill does not submit anything, does not decide funding, and does not sign off finance or legal positions.
- It does not predict the donor score, and any output that reads as a prediction has overstated itself. It predicts where the points are, which is a different and more useful claim.

**Evidence base:** `references/cerv-2026-worked-example.md` (the calibration record this method is built on), `references/rights-holder-coverage.md`, `references/word-export.md`.
