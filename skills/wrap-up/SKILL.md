---
name: wrap-up
description: Session wrap-up. Use when Ane types /wrap-up to close a session. Gathers git, errors, and pending actions, delivers a concise status report, then commits and pushes pending work, and offers opt-in post-commit follow-ups (skill improvements, skill-fit signals, learning capture). Pass "report" for a read-only status with no commit.
---

# Session Wrap-Up

A session-end workflow in phases, not a single parallel check. Run them in order:

1. **Preflight** — confirm the repo and capture the branch.
2. **Gather** (read-only checks 1 to 6) — collect status; write nothing.
3. **Report** — deliver one consolidated status checklist.
4. **Commit and push** (gated, autonomous) — record side-effects, then commit pending work.
5. **Optional follow-ups** (opt-in, batched into one prompt) — skill and learning loops.

**Report-only mode.** If Ane invokes `/wrap-up report`, `/wrap-up --report-only`, or asks for status only, run phases 1 to 3 then STOP. Do not write, commit, or run any follow-up.

**Date.** Use the current date from the session environment. Never guess it.

## Phase 1 — Preflight

Run `git rev-parse --git-dir 2>/dev/null`. If it fails (not a git repository), skip the git, harness, and commit sections. Run only checks 3 and 4, deliver a short report, and end with:

```
ℹ️  Not a git repo — git, harness, and commit checks skipped.
```

Otherwise capture the branch once: `git branch --show-current`. Hold it as the **expected branch** for the branch guard in Phase 4, and show it in the report header.

## Phase 2 — Gather (read-only checks)

**1. Git status**
Run `git status --short`. For unpushed commits, run `git log --oneline "@{u}.." 2>/dev/null`. If the branch has **no upstream** (`git rev-parse @{u}` fails), say so explicitly: nothing is pushed yet, and the push step will set `-u`. Do not report "all pushed" when there is no upstream. Report uncommitted files (count + list), unpushed commits (count + list), and the current branch. If both are clean, state that clearly.

**2. Test harness (project-aware)**
If `tests/run_tests.py` exists in the repo root AND there is at least one uncommitted text file (markdown, code, config), run `python tests/run_tests.py` and include the result. If it passes, report `✅ Harness N/N`. If it fails, list each failure as `⚠️ HARNESS:` and recommend `/test` for detail. If the harness file does not exist, skip this check silently — most repos have no MEL harness.

**3. Recent errors**
Scan this conversation for error messages, failed commands, or unresolved issues identified but not fixed: stack traces, "error:", "failed", "TODO", explicit "I'll fix this later" statements.

**4. Pending actions**
Identify anything Ane said she would do or left open:
- Files to review or send
- Follow-up tasks mentioned
- Decisions deferred
- Any explicit "next steps" not yet taken

**5. Uncommitted changes risk**
If there are uncommitted files, run `git diff --stat` to assess what is at risk of being lost.

**6. Desktop / claude.ai export drift (project-aware)**
If `scripts/check_desktop_sync.py` exists in the repo root, run `python scripts/check_desktop_sync.py`. This surfaces claude.ai Desktop project files that drifted since the last upload (the claude.ai project has no file API, so this surface is always a manual re-upload). If it reports `[DRIFT]`, list the export files Ane must re-upload and the `--mark-synced` follow-up. If it reports no drift, or the script does not exist, skip this section silently.

## Phase 3 — Report

Deliver as a tight checklist. One line per item. No preamble.

```
SESSION WRAP-UP — [date] — branch [branch]

GIT
  ✅ Nothing uncommitted          OR  ⚠️  N file(s) uncommitted: [list]
  ✅ All pushed                   OR  ⚠️  N commit(s) not pushed: [list]   OR  ⚠️  No upstream — nothing pushed yet

HARNESS (only when relevant files were touched)
  ✅ N/M checks passed            OR  ⚠️  N harness check(s) failing — /test for detail

ERRORS
  ✅ No unresolved errors         OR  ⚠️  [description of unresolved issue]

PENDING ACTIONS
  ✅ Nothing open                 OR  ⚠️  [action]: [what Ane committed to]

DESKTOP SYNC (only when scripts/check_desktop_sync.py exists and reports drift)
  ⚠️  Re-upload to claude.ai Desktop: [export file(s)] — then run check_desktop_sync.py --mark-synced

RECOMMENDATION
  [One sentence: either "Safe to close" or specific action to take first]
```

In report-only mode, stop here.

## Phase 4 — Commit and push

After the report, if there are uncommitted files or unpushed commits, finish the work block by committing and pushing. Ane has a standing instruction to always commit and push at the end of a work block. Do not ask for permission to commit pending session work — execute. The gates below still apply.

**Gate 1 — Harness must pass (if it ran).**
If check 2 ran and reported any `⚠️ HARNESS:` line, STOP. Do not commit. Tell Ane the harness is red and recommend `/test` for detail. The wrap-up ends here.

**Gate 2 — Branch guard (checkout + content).**
First, compare the current `git branch --show-current` to the expected branch captured in Phase 1. If they differ, a background process may have checked out another branch mid-session and hijacked the working tree (the documented ralph-loop hazard). STOP and ask Ane before committing.

Then guard against the *content* hijack the branch-name check misses (a loop committing its own commits onto the matching branch). If `scripts/check-branch-integrity.sh` exists in the repo root, run it. It exits non-zero (SUSPICIOUS) on loop-authored commits or commits sitting directly on `main`. On SUSPICIOUS, STOP: surface its findings and ask Ane whether every commit ahead of `origin/main` is hers before committing or pushing. If the script is absent (most repos), skip this part silently. Report:
```
BRANCH INTEGRITY
  ✅ Branch matches + commits ahead of origin/main verified
  OR  ⚠️  SUSPICIOUS — [findings]; commit/push held pending Ane's confirmation
```
If both checks pass, state the branch you are about to commit to and continue.

**Gate 3 — Sensitive-file scan.**
Before staging, scan the uncommitted file list **case-insensitively** against these patterns: `.env`, `.env.*`, `*credentials*`, `*secret*`, `*token*`, `*.key`, `*.pem`, `*.pfx`, `*api_key*`. This is a filename scan, not a content scan: it will not catch a secret hardcoded inside a normally-named file, and it may flag innocent names (e.g. `token_utils.py`). If any file matches, list the matches and ask Ane explicitly which (if any) to include. Otherwise continue silently.

**Gate 4 — WIP exclusion.**
If any uncommitted file is unrelated to the current session's work and looks mid-edit (a single file the user was clearly developing in another window, e.g. a `TODO` marker or `None` placeholder added inline), exclude it from the commit. List excluded files in the report so Ane sees what was left behind.

**Side-effect write — QA rejection log (project-aware).**
Run this only after the gates pass, just before staging. If this session ran Ann/Vi orchestration (any qa_block was produced) AND `agent-improvements/qa-rejection-log.md` exists, append one row per orchestrated run: Date, Task slug, overall_verdict, Re-delegations (count), Rejection/flag reasons (≤15 words each, semicolon-separated, `—` if the verdict was a clean PASS). `/improve-system` reads this log to detect recurring failure patterns and trend the rejection rate. Stage the file you just wrote with the rest of the commit. Skip silently if no qa_block was produced or the log file is absent.

**Stage explicitly.**
Add files by name (`git add path/to/file path/to/other`), including the QA log if you just wrote it. Never use `git add -A` or `git add .` — these sweep gitignored runtime state, OS metadata, and unrelated WIP into commits.

**Draft the message.**
Match recent style: run `git log --oneline -10` and use the same conventional-commit prefix scheme (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, with optional scope like `docs(overlay):`). One-line title under 72 chars; one or two body sentences only when the why is non-obvious. Add the `Co-Authored-By` footer only when the active CLAUDE.md or the harness asks for one.

**Commit.**
Pass the message via a single-quoted HEREDOC so PowerShell/bash do not expand `$` or backticks:
```
git commit -m "$(cat <<'EOF'
<title>

<optional body>
EOF
)"
```

**Push.**
Run `git push`. If the branch has no upstream, set it: `git push -u origin <branch>`. If push is rejected because the remote is ahead, run `git pull --rebase` then `git push` — never `--force` from this skill.

**Confirm in the report.**
Append:
```
COMMIT & PUSH
  ✅ Committed <short-SHA> "<title>" to <branch>
  ✅ Pushed to <remote>/<branch>
```
Or, if a gate stopped the commit:
```
COMMIT & PUSH
  ⚠️  Skipped — <reason>: [files]
```
If the working tree was already clean and there were no unpushed commits, omit this section entirely.

## Phase 5 — Optional follow-ups (opt-in)

Four independent loops can run after the commit. None of them blocks the commit. Evaluate each loop's trigger below; for every loop that genuinely triggers, **batch them into ONE prompt** so Ane answers once:

```
Optional follow-ups (enter to skip all):
  [1] Skill improvement — <skill>: <one-line change>
  [2] Save skill idea to backlog — <NEW|ENHANCE> <skill>
  [3] 3-line learning capture → journal
  [4] Log token cost actual → cost-calibration-log
Reply with the numbers to run, or enter to skip.
```

If only one loop triggers, ask its own one-line prompt directly. If none trigger, say nothing and end the wrap-up. Run accepted loops in the order 1, 2, 4, 3. Loop 3 runs last by design (the vault may be unreachable and it is the least critical); Loop 4 writes only to the work-folder repo, so it is safe to run before Loop 3.

### Loop 1 — Skill-improvement capture (inline fix, this session)

Captures a **single-session, generalizable improvement to a skill that was actually used this session**: a gotcha that will recur, a missing step that caused rework, or a newly-proven capability the skill does not yet document.

**Trigger.** A skill ran this session AND a concrete, generalizable change to it would have saved time or prevented an error this session. Do NOT trigger for project-specific facts (those go to auto-memory, not the skill), for trivia, or for recurring cross-session patterns (those are `/improve-system`'s job).

**On accept, per confirmed skill:**
1. Edit the skill's **repo clone**, never the live `~/.claude/skills/<name>` junction (the SessionStart `npx skills add` overwrites the junction from the repo). For Ane's skills the clone is `~/OneDrive/GitHub/personal-skills/skills/<name>/SKILL.md`; a third-party skill lives in its own repo.
2. Apply `edit-preservation`: scope-bounded, add rather than rewrite, every line outside the change byte-identical.
3. Commit + push that repo (single-quoted heredoc message, conventional prefix, `Co-Authored-By` footer per CLAUDE.md).
4. **Sync the work-folder mirror** when one exists at `.claude/skills/<name>/SKILL.md`: copy the new content over it and commit it in the work-folder repo, so web sessions are not left stale.
5. **Skills-lock.** For **non-core** skills, SKIP the lock-regen — it is the documented exception (the harness `check_skill_repo_chain` validates only clone-clean/synced + the core-agent names, not per-skill hashes; regenerating from the repo root turns `skills/<name>` into symlinks and dirties the clone). For **core agents** (ann/vi/li/researcher), run `npx skills add gasserane/personal-skills --all -y` (NO `--global`) from the repo root, then clean up the symlink churn with `git clean` — NEVER `rm -rf .agents` (it deletes through the symlinks).
6. The change goes live on the **next session start** (the `--global` install pulls the repo). Say so.

**Confirm.** If any skill was updated, append to the report:
```
SKILL IMPROVEMENTS
  ✅ <skill> — <one-line change> (committed <sha>, live next session)
```

### Loop 2 — Skill-fit scan (should a skill have done this work?)

Looks at the *type of work* the session contained, classifies it into one of three outcomes, and hands Ane the matching follow-up. It writes nothing except an opt-in backlog line.

**Trigger.** The session involved a structured, multi-step piece of work that will plausibly **recur** for Ane. Skip for one-off bespoke work, trivia, pure conversation, debugging, or system plumbing. First, check the work against the installed skill list and the routing lanes in the project CLAUDE.md (§ Skill routing). Then classify into exactly one:

- **ALREADY COVERED** — an existing skill already does this work, and Ane did it **manually without invoking it**. The win is the time she will save next time. This is a first-class signal, not an aside: surface it even when there is nothing to build.
- **NEW** — no existing skill targets this work; Ane did it ad-hoc, by hand, or through general orchestration a dedicated skill would shortcut.
- **ENHANCE** — an existing skill fits the work but needed improvement to do it **perfectly** this session: a missing mode, a missing output type, an absent branch of logic, or a gap that forced manual rework.

**Bias toward no.** Skill proliferation is a real cost — the project CLAUDE.md warns against competing skills and glossaries. Surface the **single** highest-value outcome only; a second only when both are clearly distinct and strong. When in doubt, say nothing. If the ENHANCE gap is small and Ane already accepted an inline fix in Loop 1, do not raise it again here — Loop 2 ENHANCE is for an improvement she would rather scope into its own session.

**What to produce.**
- For **ALREADY COVERED**: the pointer only — name the skill, its trigger phrase, and the one line Ane should type next time. No plan, no prompt. Stop there.
- For **NEW** and **ENHANCE**, produce all of:
  1. **Signal** in one line: `[NEW: <proposed-skill-name> | ENHANCE: <existing-skill>] — <the recurring work> — <why a skill or the improvement beats doing it by hand>`. For ENHANCE, also state the precise gap: what the skill does now, what it failed to do this session, and what "perfect fit" would look like.
  2. **Plan** in 3 to 6 steps: scope and trigger phrases (NEW) or the exact change and where it lands in the skill file (ENHANCE); which existing skills or agents it composes with or sits beside, named, to prove it is not a duplicate; the build route (`skill-creator` for a focused skill or change, or `superpowers:brainstorming` → `writing-plans` → `writing-skills` for a larger build); the clone path `~/OneDrive/GitHub/personal-skills/skills/<name>/`; and the close-out (run `/test`, commit and push the clone, sync the work-folder mirror at `.claude/skills/<name>/`, live next session).
  3. **Start prompt** — a fenced, self-contained prompt Ane can paste into a fresh session. It names the skill and its one job (NEW) or its one improvement (ENHANCE), states the build skill to invoke first, gives the clone path, states explicitly how it differs from the nearest existing skill so the new session does not rebuild or duplicate, and ends with "run /test, then commit and push both surfaces".

**Optional stash (NEW and ENHANCE only).** This is the one write in Loop 2, and it lands *after* the Phase 4 commit, so it must commit itself rather than be left orphaned. Offer once, default no: `Save this to the skill-ideas backlog? (y/n)`. On yes: append the signal, plan, and start prompt to `agent-improvements/skill-ideas-backlog.md` (apply `edit-preservation`; create with an `# Skill ideas backlog` heading if absent), then stage, commit, and push that one file in the work-folder repo. Do not leave it uncommitted.

**Confirm.** Append only the line(s) that apply to the report:
```
SKILL OPPORTUNITY
  💡 ALREADY COVERED: /<skill> does this — trigger "<phrase>"; use it next time
  💡 NEW <proposed-name>: <one-line opportunity> — plan + start prompt below
  💡 ENHANCE <skill>: <gap in one line> — improvement + plan + start prompt below
```
For NEW and ENHANCE, print the plan and start prompt under the report.

### Loop 3 — Post-deliverable learning capture (human learning, runs last)

Feeds *Ane*, not the system. Runs last because the vault may be unreachable and it is the least critical loop; a skip or an unreachable vault must never affect the safety-critical commit, which already completed in Phase 4.

**Trigger.** This session produced a substantive deliverable (an analytic, evaluation, knowledge, SRHR, or structured output Ane will use or send) AND the Obsidian vault is reachable at `OBSIDIAN_VAULT_ROOT` (`C:/Users/AGasser/OneDrive/Ane Obsidian Vault`). Skip for pure maintenance, debugging, or system-plumbing sessions, and skip on web / off-device where the vault is not provisioned.

**On accept.** Run the `journal-reflection` **Post-deliverable capture** mode (the three questions: what it taught you about the work; what you would do differently; one thing to carry forward) and append the answers to `5 JURNAL/Learning/deliverable-learning-log.md` per that skill's File-placement rule (running log, edit-preservation, create with frontmatter if absent). Do not auto-answer the prompts; her words go in verbatim.

**Confirm.** If a capture was written, append to the report:
```
LEARNING CAPTURE
  ✅ Appended to 5 JURNAL/Learning/deliverable-learning-log.md
```

### Loop 4 — Token-cost actual capture (closes the calibration gap)

Graduates this session's `cost-calibration-log.md` row from an estimate to a firm actual. The agent cannot read its own token count (Claude Code does not expose per-run counts to the agent), so an Ane paste is the only capture path, and it must run before the terminal closes or the row graduates to `not observed` after 14 days.

**Trigger.** The session appended, or should have appended, a row to `agent-improvements/cost-calibration-log.md`: a COMPLEX `/ann` run, or a system-improvement session (`/grade-system`, `/system-audit`, wiki expansion, specialist deployment, harness or P1/P2 budget work). Skip for conversation, trivia, light edits, and any session with no calibration row.

**On accept.** Ask Ane to paste the `/cost` block (context tokens used, `$` cost, cache %, duration). Then:
1. Identify the cost-calibration row(s) this session opened, matched by task slug and today's date.
2. **One row:** write the pasted figure to that row's `Actual`, then compute `Variance` against its `Estimated band` (flag `⚠️ over-band` at actual ≥ 1.5× the upper bound). Update the row in place with Edit (apply `edit-preservation`; touch only that row).
3. **More than one row:** the `/cost` total is the session sum, not per-task. Ask Ane for the rough split. If she gives one, write each row. If not, record the total against the largest-scope row, annotate the others `[shared session total — see <slug>]`, and never write a fabricated per-row figure (factual-reliability rule).
4. Refresh the log's variance-summary counts if the file maintains them (total rows, firm-observed count, over-band count).
5. Stage, commit, and push this one file in the work-folder repo. It lands after the Phase 4 commit, so it commits itself (single-quoted heredoc message, conventional prefix, `Co-Authored-By` footer per CLAUDE.md).

**On skip.** Leave the row(s) as `[pending — Ane: paste from terminal]`; the 14-day rule graduates them to `not observed` at the next Li CURATE.

**Confirm.** If an actual was written, append to the report:
```
COST ACTUAL
  ✅ <task-slug> — actual <Nk> vs est <band> (<variance>); committed <sha>
```
