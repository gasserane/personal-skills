---
name: system-audit
description: Run a comprehensive quality, sanity, and efficiency audit of Ane's MEL/SRHR system (Ann/Vi/Li/Researcher team + wiki + harness + three-repo architecture). Use whenever Ane types /system-audit, /audit, /system-check, /system-health, or asks "any issues with the system", "audit the agents", "check for drift", "system health", "check the team", "is anything broken". Surfaces drift, inconsistencies, hygiene issues, and architectural ceilings. Categorises by severity (medium documentation drift / low hygiene / decision-required architectural). Produces a Tier 1 working brief with sequencing. Does NOT auto-execute fixes. Run before any /li curate, after agent-improvement work, or as a periodic health check. Different from /test (harness only) and /li lint (wiki only) by covering CLAUDE.md, skills, registry, overlays, hygiene, and architecture in one pass.
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

### Step 2 — Documentation consistency (medium severity, high impact)

Read in parallel:
- `~/.claude/CLAUDE.md` — scan for self-contradictions. Common patterns: specialist count drift ("16" vs "20" in same file), version-number drift, layer-table drift.
- `<work folder>/CLAUDE.md` — scan for stale numbers (specialist count, harness check count, page count, agent-team member count).
- `~/.claude/skills/{ann,vi,li,researcher}/SKILL.md` — line counts vs budgets (Ann ≤ 300; Vi ≤ 250; Li ≤ 400; Researcher ≤ 200; authoritative source is `SKILL_BUDGETS` in `tests/run_tests.py`). Em-dash counts in body prose (per CLAUDE.md voice rule, which carves out list-item separators and frontmatter in skill files).
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
- `mel-framework-reference.md` size (claude-ai mirror) — flag if grown >200KB (baseline 117KB at 2026-04-28 audit; 174.7KB at 2026-05-10 with legitimate Tier 2 + Tier 3 expansion; threshold raised 2026-05-10 to accommodate documented wiki growth).
- Em-dash discipline across wiki body prose. Raw `grep -c "—"` over-counts: it catches section headers, the `title:` frontmatter, table rows, list-item `term — definition` separators, and em-dashes inside verbatim citation titles, none of which are violations. Filter the structural noise first: `grep -rnE "—" mel_wiki/wiki/ --include="*.md" | grep -vE ":[0-9]+:#|title:|\||\[\["`. Compare the filtered count to the most recent audit-drift baseline; trend matters more than absolute count. Inspect survivors by eye, since list-definition dashes and citation titles still pass through; apposition where a comma causes genuine ambiguity is allowed.

### Step 6 — Recent audit-drift carry-forward

If `agent-improvements/audit-drift-*.md` exists:
1. Read the most recent (sort by filename date).
2. For each previously-flagged item, check whether it has been resolved.
3. Carry-forward unresolved items into your findings, marked `[carry-forward from audit-drift YYYY-MM-DD]`.

This prevents the same issue from getting re-flagged as new each audit and from being silently dropped between audits.

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

End the brief with: "Want me to execute the quick-batch fixes now?" Then wait. Ane confirms before any execution.

If Ane confirms, execute the quick batch (mechanical edits). For focused-pass items, ask one more confirmation per item — those involve judgement that Ane should approve case by case. For strategic-decision items, never auto-execute.

## Cost band
~30-60k tokens for a clean audit pass. Larger if many findings need cross-reference verification. Within the 200k system-improvement cap with substantial headroom.
