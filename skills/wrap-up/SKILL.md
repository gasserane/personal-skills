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
