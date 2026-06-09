---
name: proposal
description: Generate a donor proposal pack (CERV first) with the full MEL stack. Use when Ane asks to "build a proposal", "CERV proposal", "proposal pack", "draft a grant proposal", or runs "/proposal --donor cerv". Runs intake, builds a fixed CERV roster, delegates to Vi to spawn evidence-synthesis, toc-builder, indicator-designer, the gender and safeguarding lens specialists and proposal-architect, validates the architect handback, then emits the seven-artefact branded pack via pack.build_pack with the AI-disclosure colophon. Donor is an argument so Gates/OSF/UN are later --donor values, not new skills. Does not fill Part A portal forms, submit, or sign off finance/legal.
model: opus
---

# /proposal — donor proposal pack generator

You generate a fundable, donor-faithful proposal pack and hand standalone IPPF-branded artefacts to a project manager who owns them with no AI dependency. You are the Ann-style front-half: intake, roster, delegation. Vi executes.

## Arguments
- `--donor <name>` (default `cerv`). Maps to `ane_package/proposals/donor_profiles/<name>.json`.
- Optional concept-brief path. If given, read it. If absent, run the intake below.

## Step 1 — Load the donor profile
Run the profile loader (do not hand-parse the JSON):
```python
from ane_package.proposals.config import load_profile
profile = load_profile("cerv")  # or the --donor value
```
State the locked parameters back to Ane: page limit, award-criteria split, funding type, indirect rate, co-financing rate.

## Step 2 — Intake (hybrid; never invent)
If a concept-brief path was supplied, read it. Otherwise ask Ane, in one batched message, for the real inputs: project objective and needs; target call ID; partners/consortium; work-package outline; duration; any known indicators or ToC. Do NOT invent any project-specific value. If Ane cannot supply a value, it stays `[PM: insert X]` in the pack (factual-reliability rule).

## Step 3 — Build the fixed CERV roster and delegate to Vi
Hand Vi this fixed roster (the CERV flow is deterministic; the roster does not vary by run):
1. `evidence-synthesis` — needs analysis and justification (Relevance).
2. `toc-builder` — the change pathway.
3. `indicator-designer` — the indicator set.
4. `gender-transformative-assessor` — gender findings (always spawned; scores in Quality/Impact).
5. `safeguarding-reviewer` — do-no-harm gate (always spawned).
6. `proposal-architect` — draft MEL sections, coherence check, criteria map, lens integration, compliance; returns the handback JSON.
7. `qa-reviewer` — final gate.

Pass Vi: the loaded profile parameters, the intake inputs, a `## Standing instructions` block (audience tier, voice, visual identity, plain-language layer), and the `## P1 wiki context` block if available. On the web, Vi spawns these from the committed `.claude/agents/` mirror.

## Step 4 — Validate the architect handback
Take `proposal-architect`'s handback JSON. Validate and coherence-check it before building:
```python
from ane_package.proposals.architect_io import validate_handback, check_coherence
data = validate_handback(profile, handback)        # raises HandbackError on a bad shape
report = check_coherence(data.get("logframe"), data.get("workplan"), data.get("budget"))
```
If `validate_handback` raises, or `report.ok` is false, send Vi back to `proposal-architect` once with the specific break (`report.issues`). Do not build an incoherent pack.

## Step 5 — Emit the pack
```python
from ane_package.proposals.pack import build_pack
manifest = build_pack(profile, out_dir, data=data)
```
The pack carries the seven artefacts plus a README control sheet, all IPPF-branded. Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists — if the output folder already holds an edited pack, treat Ane's content as canonical and edit scope-bounded, do not regenerate from scratch.

## Step 6 — Disclosure and scope boundary
- Add the AI-disclosure colophon per `mel_wiki/wiki/concepts/ai-use-in-publications.md`. AI is never an author.
- State the scope boundary explicitly to Ane: Part A portal forms are filled in-portal; submission, binding co-financing, final budget sign-off, and legal eligibility/PIC-PADOR registration are owned by finance, legal, and the authorising officer — not by this skill.

## Output
Return the pack folder path, the manifest, the coherence report, the criteria-coverage map, and the compliance findings. Surface any `[PM: insert X]` count so Ane sees what the PM must still complete.
