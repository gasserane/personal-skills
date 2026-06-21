---
name: wrap-up
description: Session wrap-up. Use when Ane types /wrap-up to close a session. Checks git, errors, and pending actions, delivers a concise status report, then commits and pushes any pending work.
---

# Session Wrap-Up

Run these checks in parallel, then deliver a single consolidated report.

## Preflight — is this a git repo?

Run `git rev-parse --git-dir 2>/dev/null`. If it fails (the current folder is not a git repository), skip the git, harness, and commit-and-push sections entirely. Run only checks 2 and 3 below, deliver a short report, and end with the line:

```
ℹ️  Not a git repo — git, harness, and commit checks skipped.
```

## Checks to run

**1. Git status**
Run `git status --short` and `git log --oneline "@{u}.." 2>/dev/null`.
Report: uncommitted files (count + list), unpushed commits (count + list).
If both are clean, state that clearly.

**1b. Test harness (project-aware)**
If `tests/run_tests.py` exists in the repo root AND there is at least one uncommitted text file (any file the harness might care about: markdown, code, config), run `python tests/run_tests.py` and include the result. If the harness passes, report `✅ Harness N/N`. If it fails, list each failure as `⚠️ HARNESS:` and recommend `/test` for full detail. If `tests/run_tests.py` does not exist, skip this check silently — most repos have no MEL harness.

**2. Recent errors**
Scan this conversation for any error messages, failed commands, or unresolved issues that were identified but not fixed. Look for: stack traces, "error:", "failed", "TODO", explicit "I'll fix this later" statements.

**3. Pending actions**
Identify anything Ane said she would do or that was left open:
- Files to review or send
- Follow-up tasks mentioned
- Decisions deferred
- Any explicit "next steps" not yet taken

**4. Uncommitted changes risk**
If there are uncommitted files, run `git diff --stat` to assess what is at risk of being lost.

**4b. QA rejection log (project-aware)**
If this session ran Ann/Vi orchestration (any qa_block was produced) AND `agent-improvements/qa-rejection-log.md` exists in the repo, append one row per orchestrated run to its table: Date, Task slug, overall_verdict, Re-delegations (count), Rejection/flag reasons (≤15 words each, semicolon-separated, `—` if verdict was clean PASS). This log is the improvement loop's metric — `/improve-system` reads it to detect recurring failure patterns and to trend the rejection rate over time. Skip silently if no qa_block was produced this session or the log file is absent.

**5. Desktop / claude.ai export drift (project-aware)**
If `scripts/check_desktop_sync.py` exists in the repo root, run `python scripts/check_desktop_sync.py`. This surfaces claude.ai Desktop project files that drifted since the last upload (the claude.ai project has no file API, so this surface is always a manual re-upload). If it reports `[DRIFT]`, list the export files Ane must re-upload to the claude.ai Desktop project, and the `--mark-synced` follow-up. If it reports no drift, or the script does not exist, skip this section silently.

## Report format

Deliver as a tight checklist. One line per item. No preamble.

```
SESSION WRAP-UP — [date]

GIT
  ✅ Nothing uncommitted          OR  ⚠️  N file(s) uncommitted: [list]
  ✅ All pushed                   OR  ⚠️  N commit(s) not pushed: [list]

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

## Commit and push

After delivering the report, if there are uncommitted files or unpushed commits, finish the work block by committing and pushing. Ane has a standing instruction to always commit and push at the end of a work block. Do not ask for permission — execute.

**Gate 1 — Harness must pass (if it ran).**
If check 1b ran and reported any `⚠️ HARNESS:` line, STOP. Do not commit. Tell Ane the harness is red and recommend `/test` for detail. The wrap-up ends here.

**Gate 2 — Sensitive-file scan.**
Before staging, scan the uncommitted file list against these patterns: `.env`, `.env.*`, `*credentials*`, `*secret*`, `*token*`, `*.key`, `*.pem`, `*.pfx`, `*api_key*`. If any uncommitted file matches, list the matches and ask Ane explicitly which (if any) to include before proceeding. Otherwise continue silently.

**Gate 3 — WIP exclusion.**
If any uncommitted file is unrelated to the current session's work and looks mid-edit (a single file the user was clearly developing in another window, e.g. a `TODO` marker or `None` placeholder added inline), exclude it from the commit. List excluded files in the report so Ane sees what was left behind.

**Stage explicitly.**
Add files by name (`git add path/to/file path/to/other`). Never use `git add -A` or `git add .` — these sweep gitignored runtime state, OS metadata, and unrelated WIP into commits.

**Draft the message.**
Match recent style: run `git log --oneline -10` and use the same conventional-commit prefix scheme (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, with optional scope like `docs(overlay):`). One-line title under 72 chars; one or two body sentences only when the why is non-obvious. Do not include a generated-by footer unless the project's CLAUDE.md asks for one.

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
Append a final line to the wrap-up report:
```
COMMIT & PUSH
  ✅ Committed <short-SHA> "<title>"
  ✅ Pushed to <remote>/<branch>
```
Or, if a gate stopped the commit:
```
COMMIT & PUSH
  ⚠️  Skipped — <reason>: [files]
```

If the working tree was already clean and there were no unpushed commits, omit this section entirely.

## Skill-improvement capture (session-end, opt-in)

A third learning loop, distinct from the other two. Check 4b feeds `/improve-system` with *recurring, cross-session* QA-failure patterns; the learning capture below feeds *Ane*. This step captures a **single-session, generalizable improvement to a skill that was actually used this session** — a gotcha that will recur, a missing step that caused rework, or a newly-proven capability the skill does not yet document. Run it after commit and push so it never blocks the safety-critical commit.

**When to offer.** Only when BOTH hold: (a) one or more skills were invoked this session, AND (b) a concrete, generalizable change to one of them would have saved time or prevented an error this session. Skip silently otherwise. Do NOT offer for project-specific facts (those go to auto-memory, not the skill), for trivia, or for recurring cross-session patterns (those are `/improve-system`'s job).

**What to do.**
1. **Propose, concretely.** List each candidate as one line: `skill-name — <the change> — <why, tied to what happened this session>`. No vague "could improve X".
2. **Ask once, default no.** `Apply these skill improvements? (per skill: y/n, or skip all)`. Wait for Ane. Edit nothing without her explicit yes.
3. **For each confirmed improvement:**
   - Edit the skill's **repo clone**, never the live `~/.claude/skills/<name>` junction (the SessionStart `npx skills add` overwrites the junction from the repo). For Ane's skills the clone is `~/OneDrive/GitHub/personal-skills/skills/<name>/SKILL.md`; for a third-party skill, its own repo.
   - Apply `edit-preservation`: scope-bounded, add rather than rewrite, every line outside the change byte-identical. Bump the skill `version`.
4. **Commit + push** that repo (single-quoted heredoc message, conventional prefix, `Co-Authored-By` footer per CLAUDE.md).
5. **Skills-lock.** For **non-core** skills, SKIP the lock-regen — it is the documented exception (the harness `check_skill_repo_chain` validates only clone-clean/synced + the core-agent names, not per-skill hashes; regenerating from the repo root turns `skills/<name>` into symlinks and dirties the clone). For **core agents** (ann/vi/li/researcher), run `npx skills add gasserane/personal-skills --all -y` (NO `--global`) from the repo root, then clean up the symlink churn with `git clean` — NEVER `rm -rf .agents` (it deletes through the symlinks).
6. The change goes live on the **next session start** (the `--global` install pulls the repo); say so.

**Confirm.** If any skill was updated, append to the report:
```
SKILL IMPROVEMENTS
  ✅ <skill> v<old>→<new> — <one-line change> (committed <sha>, live next session)
```
Omit the section entirely when not offered or declined.

## Skill-fit scan — should a skill exist for this work? (session-end signal, no writes)

Distinct from the inline loop above. *Skill-improvement capture* fixes a small, scoped gap in a skill that ran THIS session and applies the edit now. This scan looks one level up: did the *type of work* this session deserve a **skill that does not yet exist**, or a **substantial enhancement** to an existing skill that is too big for an inline tweak? It writes and builds nothing — it signals the opportunity and hands Ane a plan plus a copy-paste start prompt for a **separate** build session.

**When to offer.** Only when the session involved a structured, multi-step piece of work that will plausibly **recur** for Ane, AND one of:
- **NEW** — no existing skill targets that work; Ane did it ad-hoc, by hand, or through general orchestration that a dedicated skill would shortcut.
- **ENHANCE** — an existing skill applied (or should have) but a *structural* gap made the work harder than it should be, and closing it is bigger than a one-line tweak (a new mode, a new output type, a new branch of logic).

Skip silently when the work was one-off and unlikely to recur; trivial; pure conversation, debugging, or system plumbing; already well-covered by a skill that worked fine; or the gap is a small inline tweak (that belongs to *Skill-improvement capture* above, not here).

**Bias toward no.** Skill proliferation is a real cost — the project CLAUDE.md warns against competing skills and glossaries. Surface the **single** highest-value opportunity only. Allow a second one only when both are clearly distinct and genuinely strong. When in doubt, say nothing.

**Rule out duplication first.** Check the work against the installed skill list and the routing lanes in the project CLAUDE.md (§ Skill routing). If an existing skill already covers it and simply was not used, the signal is "use /<skill> next time", not a new build.

**What to do (no writes).**
1. **Signal** in one line: `[NEW: <proposed-skill-name> | ENHANCE: <existing-skill>] — <the recurring work> — <why a skill beats doing it ad-hoc>`.
2. **Plan** in 3 to 6 steps: scope and trigger phrases; which existing skills or agents it composes with or sits beside (name them, to prove it is not a duplicate); the build route (`skill-creator` for a focused skill, or `superpowers:brainstorming` → `writing-plans` → `writing-skills` for a larger build); where it lives (`~/OneDrive/GitHub/personal-skills/skills/<name>/`); and the close-out (run `/test`, commit and push the clone, live next session).
3. **Start prompt** — a fenced, self-contained prompt Ane can paste into a fresh session. It must name the skill and its one job, state the build skill to invoke first, give the clone path, state explicitly how it differs from the nearest existing skill so the new session does not rebuild something that exists, and end with "run /test, then commit and push".
4. **Optional stash.** Offer once, default no: `Save this to the skill-ideas backlog? (y/n)`. On yes, append the signal, plan, and start prompt to `agent-improvements/skill-ideas-backlog.md` (apply `edit-preservation`; create the file with an `# Skill ideas backlog` heading if absent). On no, it lives only in this report.

Do not edit or create any skill here. This step ends at the signal, the plan, and the prompt.

**Confirm.** If an opportunity was surfaced, append to the report:
```
SKILL OPPORTUNITY
  💡 [NEW <proposed-name> | ENHANCE <skill>]: <one-line opportunity> — plan + start prompt below
```
Then print the plan and the start prompt under the report. Omit the section entirely when no opportunity clears the bar.

## Post-deliverable learning capture (project-aware, vault-coupled)

This is the human-learning loop counterpart to check 4b (the system-learning loop). Step 4b feeds the *system*; this step feeds *Ane*. Run it LAST, after commit and push, so a skip or an unreachable vault never blocks the safety-critical commit.

**When to offer.** Only when this session produced a substantive deliverable (an analytic, evaluation, knowledge, SRHR, or structured output Ane will use or send) AND the Obsidian vault is reachable at `OBSIDIAN_VAULT_ROOT` (`C:/Users/AGasser/OneDrive/Ane Obsidian Vault`). Skip silently for pure maintenance, debugging, or system-plumbing sessions, and skip silently on web / off-device where the vault is not provisioned.

**What to do.** Offer once, in one line: `3-line learning capture? (enter to start / skip)`. Wait for Ane.
- If she skips, write nothing and end.
- If she starts, run the `journal-reflection` **Post-deliverable capture** mode (the three questions: what it taught you about the work; what you'd do differently; one thing to carry forward) and append the answers to `5 JURNAL/Learning/deliverable-learning-log.md` per that skill's File-placement rule (running log, edit-preservation, create with frontmatter if absent). Do not auto-answer the prompts; her words go in verbatim.

**Confirm.** If a capture was written, append to the report:
```
LEARNING CAPTURE
  ✅ Appended to 5 JURNAL/Learning/deliverable-learning-log.md
```
Omit the section entirely when not offered or skipped.
