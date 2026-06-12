---
name: improve-system
description: Use when Ane types /improve-system, asks to "mine recent sessions", "what is the system getting wrong", "improvement loop", "trend the rejection rate" — or when the SessionStart maintenance nudge reports improve-system due (14-day cadence). Mines the QA logs and session history for recurring correction patterns and proposes system edits. Not for one-off bug fixes (/system-audit finds those) and not for wiki integrity (/li lint).
---

# Improve System — the measured improvement loop

Mine the system's own correction history for recurring failure patterns, trend the rejection-rate metric, and propose targeted edits. **Propose, never auto-apply.** This is the auto-research loop adapted for non-measurable work: chat-history corrections are the proxy signal, qa-rejection rate is the trend metric (video-insights improvement #5, 2026-06-12).

## Scope boundary

- `/system-audit` finds specific bugs and drift to fix once. `/improve-system` finds *recurring behavioural patterns* across runs and turns them into standing rules.
- `/li curate` consolidates agent overlays into skill diffs (3+ run threshold). Do not duplicate it: when a pattern's evidence lives only in overlays, note "route via CURATE" instead of drafting the diff here. This skill's distinct ground is the QA logs, the rejection-rate metric, and session-history corrections.
- An improvement loop without a metric is a ritual. Every run reports the metric, even when it proposes nothing.

## Steps

1. **Gather signals** (work folder, read in parallel):
   - `agent-improvements/qa-rejection-log.md` — verdicts, re-delegation counts, reasons (primary metric).
   - `agent-improvements/qa-disagreement-log.md` — where Ane or Ann overrode qa verdicts.
   - `agent-improvements/cost-calibration-log.md` — estimate-vs-actual drift.
   - `## Active Improvements` sections of `agent-improvements/{ann,vi,li,researcher}-overlay.md`.
   - `.remember/recent.md` and `.remember/today-*.md` — session-history proxy for corrections Ane made in conversation.
   - `agent-improvements/improve-system-runs.md` — prior runs (avoid re-proposing rejected items).

2. **Trend the metric.** Report: total orchestrated runs logged, share with re-delegations or non-PASS verdicts, top 3 recurring reasons, direction vs the previous run's figures. If the rejection log is empty after sessions that clearly ran orchestration, the finding is "the wrap-up 4b logging step is failing" — a logging gap, never "no learning".

3. **Cluster patterns.** A pattern needs **2+ independent occurrences** across runs or logs. One occurrence is a watch item, listed but not actioned. Name each pattern in one sentence with its occurrences cited.

4. **Propose edits.** Per pattern: target surface (CLAUDE.md rule, skill edit, agent edit, checklist, feedback memory, or PreToolUse hook for never-do rules), draft wording, expected effect on the metric. Present all proposals as a numbered list and wait for Ane's per-item approve/reject/defer.

5. **Apply approved items only.** Use the Edit tool, scope-bounded. Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.

6. **Close the run.** Append a dated summary (metric figures, patterns found, proposals + Ane's decisions) to `agent-improvements/improve-system-runs.md` (create with a `# Improve-System Run Log` header if absent). Then mark the cadence: `python ~/.claude/hooks/maintenance_due.py --mark improve-system 2>/dev/null || true`.

## Red flags — stop if you catch yourself doing these

- Applying any edit before Ane approved that specific item. "She'll obviously approve" is not approval.
- Promoting a single occurrence to a pattern because it "feels familiar".
- Re-proposing an item the runs log shows Ane rejected, without new evidence.
- Reporting "system healthy" without printing the metric figures.

| Excuse | Reality |
|---|---|
| "The fix is trivial, just apply it" | Trivial edits to standing rules compound; approval is the gate. |
| "Sparse data, but the pattern is obvious" | One data point is an anecdote. Log it as a watch item. |
| "Empty log = clean record" | Empty log = broken logging. Verify wrap-up 4b ran. |
