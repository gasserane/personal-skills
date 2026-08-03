---
name: wrap-up
description: Session wrap-up. Use when Ane types /wrap-up to close a session. Gathers git, errors, and pending actions, delivers a concise status report, then commits and pushes pending work, and offers opt-in post-commit follow-ups (skill improvements, skill-fit signals, learning capture). Pass "report" for a read-only status with no commit. Writes a continuation handoff prompt for the next session whenever named work is still open, one file per workstream so parallel sessions cannot overwrite each other; pass "continue" to force one.
---

# Session Wrap-Up

A session-end workflow in phases, not a single parallel check. Run them in order:

1. **Preflight** — confirm the repo and capture the branch.
2. **Gather** (read-only checks 1 to 6) — collect status; write nothing.
3. **Report** — deliver one consolidated status checklist.
4. **Commit and push** (gated, autonomous) — record side-effects, then commit pending work.
5. **Optional follow-ups** (opt-in, batched into one prompt) — skill and learning loops.
6. **Continuation handoff** (automatic, gated on open work) — write the prompt that starts the next session.

**Report-only mode.** If Ane invokes `/wrap-up report`, `/wrap-up --report-only`, or asks for status only, run phases 1 to 3 then STOP. Do not write, commit, or run any follow-up, and do not write a handoff.

**Date.** Use the current date from the session environment. Never guess it.

## Phase 1 — Preflight

**The thread is now closed.** From this point, park every new question, explainer request and follow-up ask in the Phase 6 handoff rather than answering it in-session. Say so in one line when it happens: `Parked for the next session: <ask>.` Ane can override by repeating the ask, and then you answer it. Reason (2026-07-30 /improve-system Run 4): across five consecutive logged sessions the thread itself closed at 190k–227k and the whole overage came from post-decision Q&A, one extra check, and the wrap-up loops. Closing costs about 50k; answering new asks inside the close-out is what doubles it.

Run `git rev-parse --git-dir 2>/dev/null`. If it fails (not a git repository), skip the git, harness, and commit sections. Run only checks 3 and 4, deliver a short report, and end with:

```
ℹ️  Not a git repo — git, harness, and commit checks skipped.
```

Otherwise capture the branch once: `git branch --show-current`. Hold it as the **expected branch** for the branch guard in Phase 4, and show it in the report header.

**Capture every repo the session wrote to, not only the working directory.** Before moving to Phase 2, list the repos this session actually touched: the working directory, plus any other repo a file was written or committed to. Hold that set as the **repo set**, and run check 1, the Phase 4 gates, and the commit against each repo in it, labelling each block with its repo name in the report. `git status` reads the current directory only, so a session that produced its deliverables in a project repo and then wrapped up from the work folder reports a clean tree while real work sits exposed somewhere else. Evidence (2026-08-01, `it-demo-followup-and-system-synthesis`): the whole session's output landed in `1. Ane's PROJECTS/AI in IPPF EN 2026/MY MEL AI SYSTEM DEMO`, including Ane's hand-edited canonical .docx sitting untracked and one file the agent had written that existed nowhere else; the work folder repo was clean and would have reported "safe to close" on its own. A repo with **no remote is not a defect to fix**. The three local-only repos guarding `1. Ane's PROJECTS` exist to survive OneDrive reverts, so report `no remote by design`, skip the push, and never offer to add an origin.

**Resume check — never run a full wrap-up twice.** If a wrap-up already ran in this session and stopped at the Phase 4 harness gate, this invocation is a RESUME, not a fresh close-out. Say `Resuming wrap-up at the harness gate.` then run ONLY: the harness (Phase 2 check 2), the Phase 4 gates, commit and push, and Phase 6. Skip Phases 2 and 3 otherwise, and skip Phase 5 unless Ane asks for it. Their findings have not changed, and re-deriving them is the largest avoidable cost in the close-out: the 2026-07-28 `local-analyst-mirror-freshness-check` row logged two wrap-up passes plus the cost-log reconciliation, which almost exactly doubled the session spend. A resume is one harness run and a commit, not a second session review.

## Phase 2 — Gather (read-only checks)

**1. Git status**
Run `git status --short`. For unpushed commits, run `git log --oneline "@{u}.." 2>/dev/null`. If the branch has **no upstream** (`git rev-parse @{u}` fails), say so explicitly: nothing is pushed yet, and the push step will set `-u`. Do not report "all pushed" when there is no upstream. Report uncommitted files (count + list), unpushed commits (count + list), and the current branch. If both are clean, state that clearly.

**A clean tree does not prove no hijack happened.** The Phase 4 branch-integrity gate runs only when there is something to commit, and `check-branch-integrity.sh` inspects only commits *ahead* of `origin/main`. A background loop that commits **and pushes** in one motion defeats both at once: nothing is uncommitted, nothing is ahead, and the gate reports `Clean` while never running. On 2026-07-28 commit `622325d` landed on `main` at 21:16:57 unauthored by that session, and pushed the session's own two commits to origin as a side effect; at wrap-up the tree was clean and 0 commits were ahead, so nothing flagged it. So in this check, always list the commits dated inside the session window regardless of push state (`git log -10 --format="%h | %ad | %s" --date=format:"%H:%M:%S"`) and mark any whose subject the session does not recognise as `⚠️ Unattributed commit` under ERRORS. Report it, do not act on it: the commit is already on origin and reverting it from a wrap-up is more dangerous than surfacing it. See the `reference_loop_guard_gap_markerless` memory.

**2. Test harness (project-aware)**
If `tests/run_tests.py` exists in the repo root AND the session **touched** a text file the harness covers (markdown, code, config), run `python tests/run_tests.py` and include the result. "Touched" means edited at any point this session, whether the change is still uncommitted or already committed. If it passes, report `✅ Harness N/N`. If it fails, list each failure as `⚠️ HARNESS:` and recommend `/test` for detail. If the harness file does not exist, skip this check silently — most repos have no MEL harness.

**Do not gate this check on a dirty working tree.** A clean tree means the work is committed, not that it is correct. On 2026-07-28 the tree was clean at wrap-up and the harness was red: an edit had gone into `claude-ai-shareable-export/` (a generated mirror) instead of the canonical root file, and `check_claude_ai_sync` caught the divergence. Gating on uncommitted files would have closed the session with a red harness and a broken claude.ai export already pushed to origin.

**Re-run a failed sync or mirror check once before acting on it.** Checks that compare two copies of a file (skill cache against clone, generated mirror against canonical) fail transiently when a parallel process is mid-write. On 2026-07-28 `skill-repo:local cache content matches clone` reported `drifted: ann, vi` while a background `npx skills add` was propagating a just-pushed commit; the two files were already byte-identical and the clone was already pushed. Acting on that check's own failure advice, "push to personal-skills", would have been the wrong move. Re-run the harness once: if the failure clears, it was a race. If it persists, diagnose which side is stale BEFORE copying anything, because the copy overwrites the newer side (see the `reference_skills_mirror_stale_clone_gotcha` memory).

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

**Name the resume path in the same breath**, or the stop costs a second full pass: `Fix, then re-run /wrap-up — it resumes at the harness gate and will not repeat the session review.` Without that line Ane re-invokes a fresh wrap-up and pays Phases 2, 3 and 5 twice for findings that have not changed.

**Gate 2 — Branch guard (checkout + content).**
First, compare the current `git branch --show-current` to the expected branch captured in Phase 1. If they differ, a background process may have checked out another branch mid-session and hijacked the working tree (the documented ralph-loop hazard). STOP and ask Ane before committing.

Then guard against the *content* hijack the branch-name check misses (a loop committing its own commits onto the matching branch). If `scripts/check-branch-integrity.sh` exists in the repo root, run it. It exits non-zero (SUSPICIOUS) on loop-authored commits or commits sitting directly on `main`. On SUSPICIOUS, STOP: surface its findings and ask Ane whether every commit ahead of `origin/main` is hers before committing or pushing. If the script is absent (most repos), skip this part silently. Report:
```
BRANCH INTEGRITY
  ✅ Branch matches + commits ahead of origin/main verified
  OR  ⚠️  SUSPICIOUS — [findings]; commit/push held pending Ane's confirmation
```
**SUSPICIOUS is not a verdict — inspect before you repeat the script's advice.** The script's own recovery text (`cherry-pick`, `reset --hard`, `push --force-with-lease`) is written for a loop hijack and is destructive. Two of its three symptoms fire just as readily on a second Claude Code session committing the repo's own work, and on a repo that commits to `main` by design, which this one does. So before surfacing anything, run `git show --stat <sha>` on every commit it flagged and say plainly whether the content is work this session recognises. Never pass the reset advice through to Ane as the recommendation unless the script reports loop markers. Evidence (2026-07-31): commit `29d2a31` landed on `main` mid-wrap-up, unauthored by the session; it held exactly the six files sitting uncommitted moments earlier, so it was a parallel session, and `reset --hard` would have destroyed an evening of real work that was never at risk.

If both checks pass, state the branch you are about to commit to and continue.

**Gate 3 — Sensitive-file scan (filename, then content).**

*3a — Filename scan.* Before staging, scan the uncommitted file list **case-insensitively** against these patterns: `.env`, `.env.*`, `*credentials*`, `*secret*`, `*token*`, `*.key`, `*.pem`, `*.pfx`, `*api_key*`. It may flag innocent names (e.g. `token_utils.py`), so treat matches as a question, not a verdict: list them and ask Ane explicitly which (if any) to include.

*3b — Convention and content scan.* The filename scan reads names only, and names are exactly what personal data hides behind. On 2026-07-03, six documents holding two people's national-register numbers, identity-card numbers and an IBAN, plus three identity-card scans, passed the filename scan in the Personal-project-a repo and were staged against a **public GitHub remote**. Every filename looked ordinary. Only manual judgement caught them, which is not a control.

So after 3a, run the content scan over what is actually staged:

```
python <skill-dir>/scripts/scan_staged_privacy.py --repo .
```

It checks two things the filename scan cannot. First, the **repo's own convention**: if `.gitignore` declares a privacy family (`*.local.*`, `**/*private*`), any staged file carrying personal data without the marker is breaking a rule the repo already set. Offer the rename rather than the commit — renaming to `*.local.*` does not merely label the file, it drops it from the commit entirely, because the repo already ignores that family. Second, the **content**: Romanian CNP, Belgian rijksregister and IBAN, each confirmed by its own checksum rather than by digit count, plus image filenames that look like identity documents.

Read the exit code, not the prose:

| Exit | Meaning | What to do |
|---|---|---|
| `0` | nothing matched | continue silently — say nothing |
| `1` | ADVISORY: personal data, but the remote is private or not a public forge | report the findings in the wrap-up, then continue committing |
| `2` | HOLD: personal data **and** a public-forge remote | do not commit or push; surface the findings and ask Ane to confirm or rename |

**The bias is deliberately toward not blocking.** A gate that interrupts clean sessions gets clicked through, and then it protects nothing. Only the co-occurrence of personal data and a publicly-reachable remote is worth stopping for — that is the one combination where a mistake is irreversible, because a push to a public forge is public the instant it lands and stays so in clones and caches after any deletion. Everything else is a note in the report.

Two things to know before you trust or doubt a result. Findings are **masked by design**: the scanner prints a file, a line and a type, never the number, because its output flows into the transcript and from there into the handoff file. And it validates by checksum, so a 13-digit epoch-millisecond timestamp or an 11-digit order ID does not match — measured at zero matches across 3,546 files of Ane's working corpus. A match therefore means something. If the script is missing (older install), say so in the report and fall back to 3a alone rather than skipping the gate silently. This covers staged content only; `/li lint` covers the wiki.

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
Run `git push`. If the branch has no upstream, set it: `git push -u origin <branch>`. If push is rejected because the remote is ahead, run `git pull --rebase` then `git push` — never `--force` from this skill. If push hangs (times out) or fails with a credential/authentication prompt error — Git Credential Manager cannot prompt in a Claude Code session — retry through the GitHub CLI's stored token — but **reset the helper chain first**: `git -c "credential.helper=" -c "credential.helper=!gh auth git-credential" push`. The empty `credential.helper=` is load-bearing. `-c` APPENDS to the inherited chain rather than replacing it, so the plain `git -c "credential.helper=!gh auth git-credential" push` form leaves Git Credential Manager first in line and hangs on GCM exactly as the unmodified push did (observed twice, 2026-07-27, each hanging past a 2-3 min timeout; the reset form then pushed in seconds). Confirm the token exists before blaming the network: `gh auth status` should show a `gho_` token carrying the `repo` scope. Diagnose fast rather than waiting on a timeout: `GIT_TERMINAL_PROMPT=0 git -c credential.interactive=never push` fails immediately with "cannot prompt" when credentials are the cause. A timed-out push never loses the commit; check `git log "@{u}.."` before re-committing (see the `reference_git_push_credential_hang` memory, 2026-07-16). **Before any retry after a timeout, kill the stale `git.exe` processes the timed-out attempt left behind** — they hold the connection/lock and block every retry until cleared (proven 3x on 2026-07-16/17): `for pid in $(tasklist //FI "IMAGENAME eq git.exe" //FO CSV | tail -n +2 | cut -d',' -f2 | tr -d '"'); do taskkill //PID $pid //F; done`, then push again.

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
5. **Skills-lock.** For **non-core** skills, SKIP the lock-regen — it is the documented exception (the harness `check_skill_repo_chain` validates only clone-clean/synced + the core-agent names, not per-skill hashes; regenerating from the repo root turns `skills/<name>` into symlinks and dirties the clone). For **core agents** (ann/vi/li/researcher), run `npx skills add gasserane/personal-skills --all -y` (NO `--global`) from the repo root, then clean up the symlink churn with `git clean` — NEVER `rm -rf .agents` (it deletes through the symlinks). For a **description-only** core-agent edit at session end, the `npx` regen is optional: `check_skill_repo_chain` compares the local `.agents/skills/<agent>/SKILL.md` (a real copy, not a symlink) to the clone, so a single `cp <clone>/skills/<agent>/SKILL.md .agents/skills/<agent>/SKILL.md` clears the harness in-session and the next SessionStart `--global` pull makes it fully live. Run `npx` only when you will re-invoke that core agent later in the same session and need the live global install refreshed (verified 2026-07-06; see the `reference_clone_edit_cache_drift` memory).
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

**It re-triggers on every wrap-up, not only the first.** A figure pasted mid-session goes stale the moment work continues. On 2026-07-29 the row was written at 210k, then the session ran on to 269k through a branch move, a script fix and a second wrap-up, so the log understated that run by about a quarter and nothing flagged it. When a row for this session already carries a firm actual, do NOT treat the loop as done: offer it again, naming the figure already captured and the work done since, and on accept overwrite that row's `Actual` and `Variance` in place. Never append a second row for the same run. The last paste before the terminal closes is the true one.

**A row dated today is not necessarily THIS session's row.** Ane runs parallel sessions and each wraps up independently, so a same-day row may belong to a different slice of work entirely. Before updating any row, read its Notes cell and confirm it describes what this session actually did. On 2026-07-31 a parallel session appended `session-economy-rule-then-wrap-up-tail` at $3.02, whose own note says it covers only the post-`/clear` tail; overwriting it with this session's much larger figure would have destroyed one real measurement and mis-stated another. **The test is the slice, not the date.** Same slice: update in place. Different slice: append a new row, and note in both Notes cells that they are siblings from concurrent sessions. When you cannot tell which, ask Ane rather than guess — the factual-reliability rule covers cost figures too.

**On accept.** Ask Ane to paste the `/cost` block (context tokens used, `$` cost, cache %, duration). Then:
1. Identify the cost-calibration row(s) this session opened, matched by task slug and today's date. A row that already holds a firm actual from an earlier wrap-up in the same session is updated, not duplicated.
2. **One row:** write the pasted figure to that row's `Actual`, then compute `Variance` against its `Estimated band` (flag `⚠️ over-band` at actual ≥ 1.5× the upper bound). Update the row in place with Edit (apply `edit-preservation`; touch only that row).
3. **More than one row:** the `/cost` total is the session sum, not per-task. Ask Ane for the rough split. If she gives one, write each row. If not, record the total against the largest-scope row, annotate the others `[shared session total — see <slug>]`, and never write a fabricated per-row figure (factual-reliability rule).
4. Refresh the log's variance-summary counts if the file maintains them (total rows, firm-observed count, over-band count).
5. Stage, commit, and push this one file in the work-folder repo. It lands after the Phase 4 commit, so it commits itself (single-quoted heredoc message, conventional prefix, `Co-Authored-By` footer per CLAUDE.md).

**OPEN MEASUREMENT QUESTION — run this once, then delete this block (/improve-system Run 5, 2026-07-31).** Does `/cost` reset across `/clear`? Two rows contradict each other: `improve-system-run-4` says the panel reports the terminal session and `/clear` does NOT reset it, so its figure may cover a prior thread; `session-economy-rule-then-wrap-up-tail` a day later saw the figure fall from $16.87 to $3.02 across one `/clear`. Every firm row's attribution depends on the answer. **The test:** the next time a wrap-up is followed by a `/clear` in the same terminal, ask Ane to paste `/cost` immediately before and immediately after. Write the pair into the cost log as a dated note, add a one-line resolution pointer to both contradicting rows, and delete this block. If the terminal was restarted between the two observations, the test is void and must be re-run.

**On skip.** Leave the row(s) as `[pending — Ane: paste from terminal]`; the 14-day rule graduates them to `not observed` at the next Li CURATE.

**Confirm.** If an actual was written, append to the report:
```
COST ACTUAL
  ✅ <task-slug> — actual <Nk> vs est <band> (<variance>); committed <sha>
```

## Phase 6 — Continuation handoff (automatic)

Writes the prompt that starts the next session. Runs last because it must describe the final state, including what Phase 4 committed and what the Phase 5 loops left open.

**Why this exists.** A fresh session loads Ane's standing files and her memory index and has zero conversation. `remember:remember` writes a *log* of what happened, injected at SessionStart as background context; it does not produce an *instruction* that sets the new session's task. So splitting a long session has meant rebuilding context by hand, which is part of why the `~/.claude/CLAUDE.md` item 8 scope gate keeps failing: the gate asks Ane to split, and splitting was expensive. This makes it cheap.

**Trigger — automatic, do not ask.** Run when either holds:
- Phase 2 check 4 found a **named workstream still open** — a piece of work with a name, a next step, and a file it lives in. Loose ends, someday-maybes, and "I should look at that" do not qualify.
- Ane invoked `/wrap-up continue`.

Stay silent on a finished session. A handoff describing completed work is a stale-instruction hazard, and the next session may act on it.

**When the next session is a BUILD, write a spec, not a status note.** A handoff that describes state leaves the next session an exploration phase to pay for. A handoff that specifies the build removes it. Evidence: `donor-proposal-scoring-skill-build` closed at $6.38 against $18.28 and $20.59 for comparable builds the same week; the one isolated difference was that the preceding session wrote a complete paste-ready spec and handed over instead of building in place. So when the open workstream is a build whose shape is already known, the handoff names the files to read, the exact change in each, the acceptance test, and the close-out. Then tell Ane in the report to `/clear` and paste it rather than continue here. Building at high context measured roughly three times the cost.

**Storage — one file per workstream.** Write to `agent-improvements/handoffs/<workstream-slug>.md`. Create the directory if absent.

NOT one file per session, and NOT a single overwritten file. Ane runs parallel sessions (local plus web, or two terminals). A single shared file means the second session to wrap up destroys the first one's handoff with no warning — silent loss, the worst kind.

**Slug stability.** Before writing, list the existing files in `handoffs/` and reuse a matching slug rather than minting a neighbour (`routing-layer.md` beside `prompt-routing.md`). Continuing work must overwrite its own handoff, not accumulate near-duplicates.

**Same-workstream race guard.** If the target file already exists AND its modification time is later than this session's start, another session got there first. Do NOT overwrite. Write to `<slug>-2.md` instead (the `-2` convention `.remember/` archive rotation already uses) and flag it:
```
⚠️  handoffs/<slug>.md was updated by another session at <time>.
    Yours written to <slug>-2.md — reconcile before continuing.
```

**Content.** Fill every section from this session. Omit a section only when it is genuinely empty.
```
## NEXT SESSION — paste this to continue
<!-- written by /wrap-up on <date> <time>, session "<short session name>" -->

Workstream: <name>. Status: <one line>.

Where it stands
  Done      : <what shipped, with commit sha>
  In flight : <the half-built thing, and which file holds it>
  Not started: <the rest>

Decisions already locked — do not reopen
  1. <decision> — because <reason>

Files, and how to treat them
  <path> — Ane hand-edited. Edit in place, never regenerate.
  <path> — generated by <script>. Safe to rerun.

Next step
  <one concrete action>

Open questions for Ane — ask before building
  1. <question>

Start in: <mode>. Lane: <Claude directly | /ann | /skill-name>.
```

**The decisions section carries the most value.** Ane's session efficiency protocol names re-deriving settled decisions as a top waste category, and a fresh session re-derives by default because it cannot see the conversation. State each locked decision WITH its reason: a decision without its reason gets re-argued the moment it looks inconvenient.

**The dated HTML comment is load-bearing.** It is how a later session detects staleness. Keep it.

**Redaction — same rule as any continuity note.** Never quote or paraphrase recognisably any `5 JURNAL` journal content. Never write SOGIESC, GBV, or SRH service-seeker identifiers into a handoff. Reference sensitive material by path, not by content.

**Retirement — run the scan, do not rely on memory.** Run `python scripts/handoff_status.py` if it exists in the repo. It prints every handoff with its age, status, and staleness flag, read fresh off the directory. Do NOT skip it because you think you know what is there.

This step is scripted for the same reason `cap_status_hook.py` exists. A "delete the handoff when the workstream finishes" instruction depends on the model remembering, which is the failure class that killed the item 8 scope gate twice. And it misses abandoned workstreams entirely: nothing ever finishes them, so nothing ever fires. Only a scan catches those.

Act on the output in two ways:
1. **Finished this session.** If this session closed a workstream that has a handoff, delete that file (`git rm`) and report it. A handoff for completed work is a stale-instruction hazard.
2. **Flagged stale (7 days or older, no activity).** Do NOT delete it. Show Ane the line and ask once: `close it? (y/n)`. On yes, `git rm` it. On no or no answer, leave it and move on.

**Never auto-delete on age.** Ane's decision, 2026-07-30. An age rule cannot tell an abandoned workstream from one waiting on a partner, and several of her real workstreams run with multi-week gaps. Deleting the wrong one loses context that cannot be rebuilt, and silent loss is the failure class this system has already paid for twice.

The listing is generated from the directory at every run and is never stored as an index file. This system has twice been bitten by an index drifting from reality — the pinned harness count went stale within hours, both times — and a list read off the directory cannot drift.

**Commit.** This lands after the Phase 4 commit, so it commits itself, the same way the Loop 2 stash and the Loop 4 cost row do. Stage the handoff file (and any deletion), commit, and push, using a single-quoted heredoc message and the conventional prefix per CLAUDE.md.

**Confirm.** Print the handoff fenced under the report so Ane can copy it without opening the file, then append:
```
CONTINUATION HANDOFF
  ✅ handoffs/<slug>.md written (committed <sha>) — next session: "continue from the handoff"
  🗑  handoffs/<finished-slug>.md removed — workstream closed
```

**Resuming.** When Ane opens a session with "continue from the handoff" or similar: one open file, read it and proceed. Several open, show the listing and ask which. Older than 7 days, say so before acting on it, because the decisions in it may have moved on.
