---
name: implementation-pack
description: Generate a post-award implementation / project-management pack (CERV first) from a proposal baseline. Use when Ane asks to "build an implementation pack", "PM pack", "set up project tracking", "after award", "implementation tracker", or runs "/implementation-pack --donor cerv". Reads the proposal handback baseline, applies the awarded grant-agreement figures, then emits a six-tab branded Implementation_Tracker.xlsx (Guide, Dashboard, BudgetBurn, Milestones, RiskIssue, Indicators), a periodic technical-report scaffold, and a README. Donor is an argument so Gates/OSF/UN are later --donor values. Does not replace the finance system of record, portal reporting, or the authorising officer's sign-off.
model: opus
---

# /implementation-pack — post-award PM pack generator

You generate a standalone, IPPF-branded implementation pack a full project manager runs with no AI dependency. You are the front-half: load baseline, apply awarded figures, build. Vi executes any optional reporting spawns.

## Arguments
- `--donor <name>` (default `cerv`). Maps to `ane_package/proposals/donor_profiles/<name>.json`.
- Optional baseline path (a proposal `handback.json` or a proposal pack folder).

## Step 1 — Load the donor profile
```python
from ane_package.proposals.config import load_profile
profile = load_profile("cerv")  # or the --donor value
```
State the implementation config back to Ane: reporting periods, RAG thresholds.

## Step 2 — Load the baseline (never invent)
```python
from ane_package.proposals.baseline_io import load_baseline
baseline = load_baseline(handback_path_or_dict)
```
If no baseline is available, ask Ane for the proposal handback or a baseline brief. Do not invent any WP, indicator, figure, or partner (factual-reliability rule).

## Step 3 — Apply the awarded figures
Ask Ane for the signed grant-agreement budget, dates, and revised targets.
```python
from ane_package.proposals.baseline_io import apply_awarded
baseline = apply_awarded(baseline, awarded)   # raises BaselineError on unknown WP/indicator or incoherence
```
If the project is not yet awarded, skip this step; the pack flags "baseline = submitted" in the Guide and README.

## Step 4 — Build the pack
```python
from ane_package.proposals.implementation_pack import build_implementation_pack
manifest = build_implementation_pack(profile, baseline, out_dir)
```
Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists — if the output folder already holds an edited pack, treat Ane's content as canonical and edit scope-bounded, do not regenerate from scratch.

## Step 5 — Optional reporting cycle (only when Ane asks for a populated report)
Delegate to Vi to spawn `mel-report-writer` (draft the narrative from tracker status) and `contribution-plausibility-analyst` (judge whether indicator progress supports the outcome claims). Neither is needed for the pack to be usable.

## Step 6 — Disclosure and scope boundary
- The Word report carries the AI-disclosure colophon per `mel_wiki/wiki/concepts/ai-use-in-publications.md`. AI is never an author.
- State the scope boundary: the finance system of record, the official portal/grant-management reporting, and the authorising officer's sign-off are owned by finance, the portal, and the authorising officer — not by this skill.

## Output
Return the pack folder path and the manifest. Surface whether the baseline is awarded or submitted, and any `[PM: insert X]` the PM must still complete.
