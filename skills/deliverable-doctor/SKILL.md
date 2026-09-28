---
name: deliverable-doctor
description: 'Review a draft document the way a careful advisor does: extract every checkable claim, send each to the checker that owns its evidence (numbers, sources, frameworks, contribution vs attribution, equity lens, recommendations, voice, references, brand), recompute figures from a supplied Excel file after approval, and return each finding as Why / Where / How, as Word margin comments in a COPY of the .docx plus a local HTML audit report. Four modes: others (MA case studies, consultant and partner deliverables), own (Ane''s drafts before sending), research (academic-style papers), proposal (donor proposals). Use on ''/deliverable-doctor <file>'' or any ask to doctor, diagnose or fully review a draft. Gives no overall score. Not a qa gate on a finished Ann brief (check-deliverable), a voice rewrite (ane-voice), donor award-criteria scoring (donor-proposal-scoring), or in-file edits (office-review-pass).'
model: opus
---

# /deliverable-doctor — claim-level review of a draft

A diagnostician, not a judge: every finding says what is wrong (Why), where (an exact quote), and the change (How), and the tool gives no overall score. Design borrowed from PaperDoctor (Lin et al. 2026), adapted to MEL/SRHR grey literature. The design passed a pre-registered trial on 2026-09-28. Spec and trial result: `agent-improvements/deliverable-doctor-spec.md` and § Result of `agent-improvements/paperdoctor-trial-preregistration-2026-09-28.md` (work folder).

**Split of work.** Agents make judgement calls. Everything exact runs in `ane_package.deliverable_doctor` and is tested there (`tests/test_deliverable_doctor.py`): routing, merging, the noise-control gates, the comment cap, anchors, recompute, rendering. Drive it with `python scripts/doctor.py <subcommand>` (below, `DD`). If a step needs new logic, add it to the package with a test, not to this file.

## Lane

- **This skill:** a claim-by-claim diagnosis of one draft, for the author (comments) and for Ane (HTML audit trail).
- `check-deliverable`: the qa-reviewer gate on a finished Ann deliverable. Pass/fail on the house standard, not a claim diagnosis.
- `ane-voice`: rewrites prose. This skill only *audits* voice.
- `donor-proposal-scoring`: scores a proposal against award criteria. Proposal mode hands award-criteria claims to it.
- `office-review-pass`: edits inside a .docx. This skill only adds comments to a copy.

## Step 0 — intake (one message, then wait)

Ask in ONE message, recommending an answer for each:
1. **Mode**: `others` | `own` | `research` | `proposal`.
2. **Genre profile**: `case-study` | `donor-report` | `brief` | `research` | `proposal` (`ane_package/deliverable_doctor/profiles/`).
3. **Comment author string**: default "Ane Gasser". Attribution is her call. A document that leaves IPPF after this pass is AI-assisted work (`mel_wiki/wiki/concepts/ai-use-in-publications.md`).
4. **Sensitive?** SOGIESC, GBV or service-seeker identifiers mean no HTML report. Comments go only into her local copy, and no web search is run on claim text.
5. **Data file** (.xlsx/.csv): if one is supplied, ask whether she **approves recompute (L3)** for this run. Never assume a yes.

Run folder: `<source folder>/_doctor/<source stem>-<YYYY-MM-DD>/`. Pass Windows paths (`C:/Users/...`) to every script, not Git Bash paths.

## Step 1 — prepare (local only)

`DD prepare <source> <run> --mode M --profile P [--sensitive] [--data <file>]`, then `DD prepass <run>`.
Local conversion only. **Never** upload to Mathpix, MinerU or any parsing service. Accepts .docx, .pdf, .md and .txt. Comments need a .docx; a PDF gets the HTML report only.

## Step 2 — L1 screen and claim extraction (parallel)

In ONE message, spawn `general-purpose` agents on `model: sonnet` (the trial's reviewers ran on Sonnet; Haiku stays pilot-gated). Build each prompt from `references/checker-contract.md` plus the checker's section of `references/checkers.md`:
- **extract-claims** → `claims.json`
- **voice** → `check_voice.json`

In the same turn, the main session itself runs:
- **references**: the saved `citation-verification` workflow on `<run>/document.md`, flags converted per `checkers.md` → `check_references.json`. Skip it when the document cites nothing.
- **brand** (.docx only): `review_pass.py verify --expect-branded`, converted per `checkers.md` → `check_brand.json`.

## Step 3 — route

`DD route <run>`. It prints per-checker queue sizes, hand-offs and the claims the profile exempted. Invalid claims make it exit non-zero: send them back to extract-claims, and never hand-edit claims into shape. In proposal mode, pass `handoffs.donor-proposal-scoring` to that skill. Tell Ane in one line; do not score them here.

## Step 4 — L2 checkers (parallel)

In ONE message, one agent per non-empty queue: number, source, framework, cause, equity, recommendation, and prior (research mode). Same model and prompt build as Step 2, plus the queue from `route.json`. The source and prior agents must fill `verified` for web evidence (contract rule 9). Sensitive run: tell source and prior agents to check only against sources in scope, with no web search of claim text.

## Step 5 — L3 recompute (only with Ane's yes)

If a data file was supplied and she approved in Step 0: `DD recompute <run> --approved`. The number checker wrote `recompute.json`, and the script evaluates it. Mismatches become `error` / `must` findings, and every figure's result goes to `recompute_log.json`. Without her yes the script refuses (exit 2), and that refusal is correct.

## Step 6 — validate, merge, challenge, finalise

1. `DD validate <run>`: any schema problem sends that checker back. Never delete a malformed finding by hand.
2. `DD merge <run>`: merges restatements (shared claim and shared reason) into one finding with `locations`.
3. Spawn the **challenger** (sonnet, `checkers.md` § challenger) on `merged.json` → `challenger.json`.
4. `DD finalise <run>` sorts each finding into commented, not commented (optional or over the cap), held (web evidence not verified in this run) or dropped (noise control, reason kept), and resolves anchors. Anchor problems exit non-zero. Fix each quote by copying the exact span from `document.md` into `merged.json`, then re-run `finalise`. Never loosen a quote.

Order matters. The challenger runs on merged findings (fewer calls), and the verified-source gate runs last, so a held finding has already survived the challenger.

## Step 7 — present, then render

Tell Ane, BLUF first: the verdict in one sentence (for example "three must-fix errors, two of them figures"), then counts per bucket, then every **held** finding by name. Held findings are often the valuable ones. The trial's femicide finding was right on substance and wrong in three details. They reach the author only after she or a re-run verifies them.

Then:
- `DD comments <run> --author "<string>"` writes the commented COPY `<stem>_DOCTOR_COMMENTS.docx` beside the source. The original is never written.
- `DD html <run>` writes `report.html` in the run folder. It is refused for a sensitive run, and it is never published as an Artifact.

## Verification (assert on written files)

| Step | Assertion |
|---|---|
| comments | The driver reopens the copy: new comments = commented findings, every pre-existing comment kept, each comment on a paragraph containing its anchor, source byte-identical. Report the counts it prints. |
| html | File exists; a sensitive run produced none. |
| recompute | Every spec has a result line in `recompute_log.json`; "could not compute" is reported, never dropped. |

The harness fixture (`tests/fixtures/deliverable_doctor/`) holds a document with four planted errors and a clean control. `DD fixture-check <planted_run> <clean_run> <expected.json>` must find each planted error under the right checker, and the clean control must return zero `error` findings.

## Noise controls, and the warning against over-tuning

Controls 1 to 6 in the spec are built in: genre profiles (Step 3), style only in voice, the challenger, merging, severity drives the default view, and the verified-source gate. The trial accepted 27 of its 41 findings. A control that halves the noise but loses one of the six substantive points (C08, C23, C25, C32, C33, C35) is worse than no control. The pre-registered regression test for exactly that: `agent-improvements/deliverable-doctor-regression-run-prompt.md` (work folder).

## Safeguards

- Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists. The source .docx is never edited. Comments go into a copy, and the run folder holds only generated files.
- Sensitive documents: no HTML report, no web search of claim text, comments into Ane's local copy only.
- No PaperDoctor code is copied until its repository carries a LICENSE file (README says MIT; no file as of 2026-09-28).
- Findings are about the text, never the person. In `others` mode, comments carry only URLs as evidence, never Ane's local paths.
