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
   - `agent-improvements/cost-calibration-log.md` — estimate-vs-actual drift, AND the numbered **calibration-signal list inside each session row**, which is the richest correction channel the system has. Every row carries 5 to 9 numbered signals naming what went wrong, what was misdiagnosed, and what was fixed at source. Read the signal lists of every row appended since the last run, not just the cost columns. Run 5 (2026-07-31) evidence: the three listed direct-mode channels returned zero while 19 signals across 3 rows carried every pattern the run found. Note the rows are appended below the closing sections of that file, not under the `## Calibration table` heading.
   - `## Active Improvements` sections of `agent-improvements/{ann,vi,li,researcher}-overlay.md`.
   - `.remember/recent.md` and `.remember/today-*.md` — session-history proxy for corrections Ane made in conversation.
   - `agent-improvements/pre-flight/*-lessons-learned.md` — the **direct-mode** correction signal for the four classic deliverable classes. Most work is now solo/direct (no Ann/Vi orchestration), so the qa-rejection-log is starved by design; these logs are where direct deliverable corrections land. Read every `*-lessons-learned.md` under `agent-improvements/pre-flight/`.
   - **Feedback memories created or updated in the window** — the direct-mode signal for everything OUTSIDE the four class logs. Corrections to non-classic deliverables (Excel tools, ops docs, pilot plans, emails, skills) land as `feedback_*` memories in the session memory directory, not in a class log. List files by mtime (`ls -l --time-style=+%Y-%m-%d` on the memory dir) and read the in-window `feedback_*` entries. Run 2 (2026-07-17) evidence: 10 weeks of zero class-log entries while 3 real corrections sat in feedback memories.
   - `agent-improvements/improve-system-runs.md` — prior runs (avoid re-proposing rejected items).

2. **Trend the metric (four signals).**
   - **Orchestrated runs (qa-rejection-log).** Report: total orchestrated runs logged, share with re-delegations or non-PASS verdicts, top 3 recurring reasons, direction vs the previous run's figures. This log fuels ONLY on Ann/Vi orchestration. If it is empty after sessions that *clearly ran orchestration*, the finding is "the wrap-up 4b logging step is failing" — a logging gap. But if the window was direct-mode work, an empty log is **expected, not broken** — verify which before concluding (check the session history and cost-calibration-log for orchestrated runs in the window; confirm the log's creation date predates the runs you expected).
   - **Direct-mode corrections, classic classes (pre-flight lessons-learned logs).** For each `*-lessons-learned.md`, report the count of entries in the window and the recurring correction themes. These four logs (ToC, indicator framework, evaluation design, evidence brief) only populate when those deliverable classes actually ship — empty logs during a window with no such deliverables are expected, not broken. Trend it the same way: rising repeat-corrections of the same theme = a rule not being applied.
   - **Direct-mode corrections, everything else (feedback memories).** Report the count of `feedback_*` memories created or updated in the window and their themes. When the window's work mix falls outside the four class logs, this is the live direct-mode signal. Repeat themes across memories = a candidate pattern; a correction that matches an EXISTING feedback memory's rule = a rule-not-applied failure, weight it heavier.

   - **Direct-mode corrections, calibration signals (cost-calibration-log rows).** Report the count of rows appended since the last run and the count of numbered signals across them, then cluster the signals by theme. Weight a signal that names a rule which already exists as a rule-not-applied failure, exactly as for feedback memories. This channel does not go quiet when the work mix shifts, because `/wrap-up` writes a row for every session, which is the property the other three lack.

3. **Cluster patterns.** A pattern needs **2+ independent occurrences** across runs or logs. One occurrence is a watch item, listed but not actioned. Name each pattern in one sentence with its occurrences cited.

4. **Propose edits.** Per pattern: target surface (CLAUDE.md rule, skill edit, agent edit, checklist, feedback memory, or PreToolUse hook for never-do rules), draft wording, expected effect on the metric. Present all proposals as a numbered list and wait for Ane's per-item approve/reject/defer.

5. **Apply approved items only.** Use the Edit tool, scope-bounded. Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.

   **Edit the canonical file, never a generated mirror.** Several targets this skill writes to are mirrors that a sync script regenerates: `claude-ai-shareable-export/*` is generated from the repo-root file of the same name, `.claude/skills/<name>/SKILL.md` from the personal-skills clone, `.claude/agents/*` from `~/.claude/agents/`. An edit to the mirror survives until the next sync, then vanishes with no error. Before editing any file under an export, mirror, or cache directory, find what generates it (`grep` the sync scripts for the filename) and edit that instead. Evidence: Run 4 wrote the claude.ai scope-gate change into `claude-ai-shareable-export/` and `sync_shareable_export.py` overwrote it in the same turn.

   **When an approved item edits a skill or agent file, re-run the harness before closing the run.** Line budgets in `SKILL_BUDGETS` (tests/run_tests.py) gate those files, so adding a rule can breach one and the failure surfaces only at the final harness run. Read the current budget from that dict rather than assuming it; the figures move. Fix a breach by folding the addition into an adjacent paragraph, never by trimming content you did not write. Evidence: Run 3's vi one-retry rule took the file two lines over and cost a follow-up commit.

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
| "Empty log = clean record" | Empty qa-log = either broken logging OR a direct-mode window with no orchestration. Verify which (did orchestration run? does the log predate the expected runs?) before concluding, and read the lessons-learned logs and the cost-log calibration signals for the direct-mode signal. |
