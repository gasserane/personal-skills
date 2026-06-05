---
name: capture-desktop
description: Capture a claude.ai Desktop session into the MEL file system. Use when Ane finishes a session in the Claude Desktop app and wants the work captured on the device — triggered by "/capture-desktop", "capture this desktop session", "I did this on Claude desktop", "save my desktop work", "import from claude.ai". Paste-driven; no cloud API exists. Stages a local transcript, classifies content into deliverables, decisions/rules, project-knowledge changes, and full log, then files each to its home. Auto-files transcript + deliverables; confirms memory/wiki/CLAUDE.md writes one-by-one.
---

# Capture Desktop Session

The device-side mirror of `scripts/check_desktop_sync.py`. That script governs
device-to-cloud sync. This skill governs cloud-to-device capture. claude.ai has
no API, so capture is paste-driven: Ane pastes a finished Desktop session and
this skill routes its content to the right places on disk.

## Step 1 — Get the content

Ask Ane to paste the Desktop conversation, or accept a file path if she gives
one. If the paste is long, write it to a temp file first to avoid truncation.

## Step 2 — Stage the transcript

Run the helper to stage a verbatim, deduplicated transcript:

```
python scripts/capture_desktop.py stage --input <tempfile> --title "<short title>"
```

- Exit 0: prints the transcript path. Continue.
- Exit 3: `[DUP] already captured` — this session was captured before. Tell Ane
  and stop unless she confirms she wants to re-route it anyway.

Transcripts are local-only (gitignored, OneDrive-backed). The staged transcript
IS the "full log" bucket — no further action for that bucket.

## Step 3 — Classify the content

Read the staged transcript. Sort its substantive content into four buckets:

1. **Deliverables** — documents, analyses, tables, drafts Ane produced.
2. **Decisions / rules / lessons** — locked decisions, framework calls, guidance
   on how the system should work, feedback on your behaviour.
3. **Project-knowledge changes** — edits that belong in canonical sources
   (`mel_wiki/` pages, `~/.claude/CLAUDE.md`).
4. **Full log** — already staged in Step 2. No action.

If a bucket is empty, say so. Do not invent content to fill it.

## Step 4 — Route each bucket

**Deliverables (auto-file).** Propose a path under the work folder, save with the
Write tool, and name it in the summary. Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.

**Decisions / rules / lessons (confirm each).** For each item, propose the target
— a memory file under the memory dir, a wiki entry, or a feedback memory — and
show the exact content you will write. Get a yes/no from Ane before writing.
Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.

**Project-knowledge changes (confirm each).** For each item, propose the exact
edit to the canonical source and get a yes/no. Apply the change with the Edit
tool, scope-bounded. Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.
- For `mel_wiki/` edits: stage for the work-folder commit in Step 5.
- For `~/.claude/CLAUDE.md` edits: after applying, commit cross-repo by running
  `bash ~/.claude-config-clone/scripts/sync-from-local.sh --auto "capture-desktop: <one-line reason>"`.
  This copies live CLAUDE.md into the claude-config clone, reconciles, commits,
  and pushes. It exits 0 silently if nothing changed.

## Step 5 — Close the loop and commit

If any canonical source was edited (wiki or CLAUDE.md), run the sync check so the
re-upload flag for the Desktop project fires:

```
python scripts/check_desktop_sync.py
```

Report any `[DRIFT]` it surfaces. Then commit the work-folder changes (deliverables
and `mel_wiki/` edits only — transcripts are gitignored). Stage by name, never
`git add -A`:

```
git add <deliverable paths> <mel_wiki paths>
git commit -m "feat(capture): desktop session <slug> — <what landed>"
git push
```

## Step 6 — Report

Deliver a tight summary:

```
CAPTURE-DESKTOP — <date>
  Transcript: desktop-captures/<slug>/transcript.md (local)
  Deliverables: <list or none>
  Decisions/rules written: <list or none>
  Canonical edits: <list or none> (CLAUDE.md pushed to claude-config: yes/no)
  Sync check: <in sync / N drift flagged>
  Commit: <short-SHA> pushed / nothing to commit
```
