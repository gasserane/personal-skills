---
name: system-audit
description: 'Run a quality, sanity and efficiency audit of Ane''s MEL/SRHR system (Ann/Vi/Li/Researcher team, wiki, harness, three-repo architecture): surfaces drift, inconsistencies, hygiene issues and architectural ceilings, categorised by severity, as a Tier 1 working brief with sequencing. Does NOT auto-execute fixes. Use when Ane types /system-audit, /audit, /system-check, /system-health, or asks whether anything is broken or drifting; run before any /li curate and after agent-improvement work. Different from /test (harness only), /li lint (wiki only), and /grade-system (overall quality posture rather than specific issues).'
---

# System Audit

You are running a quality / sanity / efficiency audit on Ane's MEL/SRHR system. Output is a Tier 1 working brief listing issues with file paths and a sequencing recommendation. You do NOT execute fixes. Ane reviews and confirms each.

## When to use this
- Ane types /system-audit, /audit, /system-check, or asks for a system health read
- Before any /li curate (audit surfaces issues curate should consolidate)
- After substantive agent-improvement work to verify nothing drifted
- Periodically as a backstop against silent drift

This skill complements rather than duplicates `/test` (harness only) and `/li lint` (wiki only). It is the broader pass that catches inconsistencies between layers.

## Workflow

### Step 1 — Harness state (fast, mechanical)

Run in this order:
1. `python tests/run_tests.py` (static; expect 78/78 or higher as system grows)
2. `python tests/run_tests.py --output` (fixture mode; some fixtures may be deliberately uncaptured)

Parse failures. Each `[FAIL]` line goes into the findings list with file:line as shown. Do NOT re-run the failures or attempt fixes; just record.

3. **Resolve `SKILLS_DIR` before measuring anything against it, and report which root it returned.** Run `python -c "import sys; sys.path.insert(0,'tests'); import run_tests as rt; print(rt.SKILLS_DIR, len(list(rt.SKILLS_DIR.glob('*/SKILL.md'))))"`. Several install roots hold `SKILL.md` copies and they drift from each other, so a line count, a budget check, or a coverage claim measured against the wrong root is simply wrong. **Never infer the root from a path written in CLAUDE.md or in this skill; ask the harness.** A flat check count across two runs does NOT prove a skills change had no effect, because the glob-based sweeps report one aggregate check each regardless of how many files they cover.

   Then compare that root against the personal-skills clone, listing skills **absent** from the root as well as skills whose content differs. On 2026-07-29 the resolved root was missing 7 first-party skills outright and held stale copies of 6 more while the harness reported green, and the audit brief initially named the wrong directory because it assumed rather than resolved. When the two differ, **diagnose which side is older before copying anything** (compare line counts and `diff` direction): the newer side is not always the installed one, and the copy overwrites whichever side you point it at.

### Step 2 — Documentation consistency (medium severity, high impact)

Read in parallel:
- `~/.claude/CLAUDE.md` — scan for self-contradictions. Common patterns: specialist count drift ("16" vs "20" in same file), version-number drift, layer-table drift.
- `<work folder>/CLAUDE.md` — scan for stale numbers (specialist count, harness check count, page count, agent-team member count).
- `{ann,vi,li,researcher}/SKILL.md` **under the `SKILLS_DIR` you resolved in Step 1**, not a hardcoded path — line counts vs budgets (read the current numbers from `SKILL_BUDGETS` in `tests/run_tests.py`, which is the authoritative source; do not trust any figure quoted here, they go stale). Report headroom, not just pass or fail: a skill within 5 lines of its budget is a finding, because the next edit fails the harness on arithmetic rather than on substance. Em-dash counts in body prose (per CLAUDE.md voice rule, which carves out list-item separators and frontmatter in skill files).
- `agent-improvements/agent_registry.md` — count `### ` entries. Cross-reference with Vi taxonomy table for completeness. Cross-reference each name with `~/.claude/agents/<name>.md` existence.

For each finding, capture: file path, line number where shown, what's wrong, suggested fix from the failure-fix table below.

### Step 3 — Overlay and CURATE state (medium severity)

Read in parallel:
- `agent-improvements/{ann,vi,li,researcher,community}-overlay.md` — file sizes (cap 35KB) and Active-entries count (cap 10). If either breaches: flag for compression CURATE, not just archive-only CURATE. The `community-overlay.md` (claimed-space feedback log, created 2026-05-06) is monitored for the same caps.
- `agent-improvements/coordination-log.md` — count entries with `STATUS: OPEN`.
- `agent-improvements/_pending-ingest.md` — count rows with `Status: PENDING`. Surface to Ane for action.
- `agent-improvements/PROPOSED-*.md` — `Status:` field on each. Flag any `AWAITING APPROVAL` older than 7 days.

### Step 4 — Hygiene (low severity, visible clutter)

Check:
- `agent-improvements/_temp_*.md` — any files older than 7 days are stale candidates. Use `ls -la` to get dates.
- `agent-improvements/proposed-agents/*.md` — for each `.md` (excluding README), check whether `~/.claude/agents/<same-name>.md` exists. If yes, the staging copy should have been removed when deployed. Use `diff -q` to confirm divergence.
- `agent-improvements/SESSION-STATE-*.md` — read each; check for internal contradictions (table cells contradicting bullet points, or progress-status fields disagreeing).
- `mel_wiki/wiki/raw/` size — should not be empty (the immutability rule says Li reads but never modifies; if it's empty, ingestion has stopped).

### Step 5 — Architectural ceilings (decisions, not bugs)

Read:
- `agent-improvements/qa-disagreement-log.md` — count rows. If 0, the Vi/Li elevation watch-trigger has not fired. Note as "ceiling unmonitored except via watch".
- `agent-improvements/cost-calibration-log.md` — count rows with observed actuals vs `not observed`. If less than 30% have actuals, observability remains weak.
- claude.ai mirror size — the mirror is now two files, `mel-framework-reference.md` (core: standing rules, quick-reference table, lenses, ECA calibration) plus `mel-framework-appendix.md` (numbered framework entries), split 2026-07-30 at 194KB. **Do not re-raise a combined size threshold.** The threshold moved three times (117KB baseline 2026-04-28, 174.7KB 2026-05-10, 200KB) and each raise bought about a week, because size was never the cost: the cost is that claude.ai has no file API, so any edit forces a manual re-paste of everything in the edited file. The split addresses that directly, since a standing-rule edit now re-pastes 30KB rather than 194KB. The size question is no longer yours to judge: `/test` enforces it on every pass via `claude-ai:framework core ≤ 50KB`, which fails when framework entries drift back out of the appendix, and via `claude-ai:framework mirror build stamp current in both halves`, which fails when the two halves fall out of step. A judgement check here only fired when Ane invoked the audit; the harness fires always. What remains yours: run `python scripts/check_desktop_sync.py` and report whether either half is stale against claude.ai, since no script can see what actually landed in project knowledge.
- Em-dash discipline across wiki body prose. Raw `grep -c "—"` over-counts: it catches section headers, the `title:` frontmatter, table rows, list-item `term — definition` separators, and em-dashes inside verbatim citation titles, none of which are violations. Filter the structural noise first: `grep -rnE "—" mel_wiki/wiki/ --include="*.md" | grep -vE ":[0-9]+:#|title:|\||\[\["`. Compare the filtered count to the most recent audit-drift baseline; trend matters more than absolute count. Inspect survivors by eye, since list-definition dashes and citation titles still pass through; apposition where a comma causes genuine ambiguity is allowed.

### Step 6 — Recent audit-drift carry-forward

If `agent-improvements/audit-drift-*.md` exists:
1. Read the most recent (sort by filename date).
2. For each previously-flagged item, check whether it has been resolved.
3. Carry-forward unresolved items into your findings, marked `[carry-forward from audit-drift YYYY-MM-DD]`.
4. **Verify numeric budgets against their authoritative source before re-flagging.** When a carried item's finding cites a numeric budget (a line cap, file-size cap, token cap), locate the cap's authoritative definition first: `SKILL_BUDGETS` or `P1_SECTION_TOKEN_CAP` in `tests/run_tests.py`, or the named config the finding cites. Confirm the metric still exists and still uses that number. If the cap was retired or changed, downgrade the finding to `[stale heuristic, not a live breach]`, name the real governing metric, and do not re-flag the old number. Motivating case: an "index.md > 200 lines" breach was carried forward as live although the harness replaced total-line caps with a per-section token cap (`P1_SECTION_TOKEN_CAP`) on 2026-04-30. This sub-step does not re-implement the harness: `/test` enforces the budgets; the audit only stops re-flagging retired ones.

This prevents the same issue from getting re-flagged as new each audit and from being silently dropped between audits.

### Step 7 — Skill trigger and steering integrity (skill-quality)

Apply the four-part skill rubric: trigger, structure, steering, pruning. Three of the four are already covered elsewhere. Trigger quality is checked by skill-creator evals; structure by superpowers:writing-skills; pruning by Steps 3 to 4 and the harness budgets. This step adds the axis those miss: **steering**, whether a skill that fires actually constrains what the agent does.

Read the first-party skills under the personal-skills `skills/` tree plus the `{ann,vi,li,researcher}` team skills. For each, check three things:

- **Trigger collision.** Two model-invocable skills whose `description` trigger phrases overlap without either naming the other as a deferral. Grep the `description:` frontmatter lines for shared trigger verbs (grill, review, plan, debate, design) and inspect the overlapping pairs by eye. A skill with `disable-model-invocation: true` is user-invoked only and cannot collide, so exclude it. A collision is resolved when the more specific skill names its lane and routes the neighbours away in its description (see grill-mel as the worked example).
- **Steering strength.** Does the body give the agent concrete, ordered actions, a numbered workflow, decision rules, an output template, or a "what NOT to do" list? Or does it only name a topic and leave the agent to improvise? A skill that fires but does not constrain behaviour is a steering failure. Flag any skill whose body has no imperative workflow, no decision rule, and no output section.
- **Steering leakage.** Does the body let the agent do something the description forbids? Example: a "does not write files" or "no-write" skill whose body carries no guard against writing, or a "does not decide" skill whose body drifts into deciding. Flag description-body contradictions.

- **Listing reachability — observe this FIRST, before reading any file.** Look at your own available-skills listing as loaded at session start and record which skills show only a name with no description. A skill whose description never reaches the listing cannot be selected by trigger match, so it is user-invoke-only without having asked to be, and every routing word in its description does nothing. This axis is invisible to file inspection: on 2026-07-30 nine first-party skills showed name-only while all 54 installed skills parsed cleanly with a healthy `description` in all four install roots, and no on-disk attribute separated the affected from the unaffected (same install batch, same mtime, no BOM, overlapping description lengths). It is also unrecoverable later, because the listing is fixed when the session starts and cannot be re-observed. So capture it in the first turn, before opening a single file. **Do not edit skill files to fix it**: the loss is in the listing, not in the files, and the 2026-07-30 pass established that no file edit addresses it.

Record each as a finding with the skill path and the failing axis (listing-unreachable, trigger-collision, steering-weak, or steering-leak). This rubric is adapted from Pocock (2026) *Building Great Agent Skills: The Missing Manual*; the steering axis is the contribution this step adds to the audit, and the listing-reachability axis was added 2026-07-30 after a sweep graded five skills' routing as correct while one of them could not be reached by routing at all.

### Step 8 — Conflicting-instruction audit (loaded-surface lint)

Overlapping and contradictory directives consume the model's judgment before any task begins; on Claude 5 generation models this failure mode outranks missing rules (Shihipar 2026, Anthropic context-engineering guidance). Audit the surfaces that load into every session: `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, the output-style block, and the model-invocable skill descriptions in the session listing.

1. **Duplicate-drifted directives.** The same rule stated on two surfaces with different wording, scope, or numbers. Grep both CLAUDE.md files for shared anchor phrases (rule names, thresholds, file paths) and diff the matching passages. The governance-marker regions are duplicated ON PURPOSE for web parity: for those, compare the shared-rule text between matching `governance:*` marker pairs and flag only drift, never the duplication itself.
2. **Contradictions.** One surface requires what another forbids, or sets a different threshold for the same act (permission modes, length caps, citation placement). Read candidate pairs by eye; report file and line for both sides.
3. **Trigger ownership.** The same behaviour claimed by two surfaces, such as a skill description and a CLAUDE.md rule both claiming one trigger. Resolve per the trigger-discipline rules in the project CLAUDE.md skill-routing section.

Classify each finding: contradiction (medium), duplicate-drifted (medium), or benign duplicate outside a governance region (low, candidate for goal + pointer). The fix lane for governance content is `governance-rules.md` + `sync_governance_rules.py`, never a hand edit between markers.

## Failure-fix mapping (your quick reference)

| Issue category | Most likely fix |
|---|---|
| Specialist count drift in CLAUDE.md | Replace stale number with current `agent_registry.md` count |
| Vi taxonomy table missing specialist | Add row matching `agent_registry.md` entry |
| Vi model rule conflict with registry | Align Vi to registry's `model_default` field; registry is authoritative |
| Skill file over budget | Compress narrative; move detail to wiki; edit Ann/Vi/Li/Researcher skill cap in `tests/run_tests.py` only as last resort |
| Em-dash in body prose | Convert per mel-report-writer's worked patterns (apposition → comma; list introducer → colon; sentence break → period) |
| Stale `_temp_*.md` file | `git rm` if older than 7 days and not currently referenced |
| Deployed agent in `proposed-agents/` | `git rm` the staged copy; live in `~/.claude/agents/` is canonical |
| Overlay over 35KB cap | Run substantive CURATE (compress entries, not just archive); Li's archive-only pass is insufficient at this size |
| qa_block schema-vs-skill mismatch | Schema is authoritative; align skill text to schema field names |
| Trigger collision between two model-invocable skills | Name the lane in the more specific skill's description and route the neighbour away; or set `disable-model-invocation: true` on the one Ane always calls by name |
| Steering-weak skill (fires but does not constrain) | Add a numbered workflow, decision rules, or an output template to the body; a description alone does not steer |
| Steering leak (body allows what description forbids) | Add an explicit guard in the body matching the description's constraint (e.g. a no-write skill states it must not use Write/Edit) |
| Conflicting or duplicate-drifted directive across loaded surfaces | Keep one canonical statement and replace the copy with a pointer; governance regions regenerate via `governance-rules.md` + `sync_governance_rules.py`, never hand-edited apart |

## Output format

Tier 1 working brief. BLUF in first sentence. No em-dashes (you are auditing for em-dash discipline; do not violate the rule you are checking). Plain English. Active voice. Sentences ≤ 25 words. Per CLAUDE.md "Tier 1 working brief" rules.

Use this template:

```
# System audit — YYYY-MM-DD

**BLUF: [N issues found, M severity-medium, P severity-low, Q architectural decisions. None blocking. X are quick fixes.]**

## Tests run
- python tests/run_tests.py: N/N
- python tests/run_tests.py --output: M/N (deferred fixtures noted)
- Manual audit of: [list]

## Documentation drift (medium severity)

| # | Issue | File | Fix |
|---|---|---|---|

## Skill trigger and steering (medium severity)

| # | Skill | Axis (trigger-collision / steering-weak / steering-leak) | Fix |
|---|---|---|---|

## Conflicting instructions (medium severity)

| # | Directive | Surfaces (file:line vs file:line) | Class (contradiction / duplicate-drifted / benign duplicate) | Fix |
|---|---|---|---|---|

## Hygiene (low severity)

| # | Issue | Evidence | Fix |
|---|---|---|---|

## Architectural ceilings (decision points)

| # | Issue | Implication |
|---|---|---|

## What is working

- [5-8 bullet items: harness clean, qa_block schema operational, P1 triple-load fix landed, etc.]

## Recommended sequencing

- Quick batch (~30 min): [issue numbers; mechanical edits]
- Focused pass (~1 hour): [issue numbers; need judgement]
- Strategic decision: [issue numbers; require Ane's call]

**Evidence base:** [inline file paths]
```

## What NOT to do

- Do not auto-execute fixes. Ane reviews and runs each one.
- Do not flag known deferred items as new issues. Cross-check `agent-improvements/system-audit-*.md` and `audit-drift-*.md` for what is already documented and accepted.
- Do not duplicate the harness output. If `python tests/run_tests.py` covers a check statically, just report the harness result; do not re-derive the finding.
- Do not produce a grade. That is `/grade-system`.
- Do not flatter the system. Honest finding count, honest severity.

## Closing

Mark the maintenance cadence before delivering the brief: `python ~/.claude/hooks/maintenance_due.py --mark system-audit 2>/dev/null || true` (no-op on machines without the hook, e.g. web containers).

End the brief with: "Want me to execute the quick-batch fixes now?" Then wait. Ane confirms before any execution.

If Ane confirms, execute the quick batch (mechanical edits). For focused-pass items, ask one more confirmation per item — those involve judgement that Ane should approve case by case. For strategic-decision items, never auto-execute.

## Cost band
~30-60k tokens for a clean audit pass. Larger if many findings need cross-reference verification. Within the 200k system-improvement cap with substantial headroom.
