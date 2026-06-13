---
name: learned
description: Fast post-deliverable learning capture. Use when Ane types "/learned", or says "capture what I learned", "log a learning", "what did I learn from this", or wants a quick 3-line note after finishing a piece of work. Appends a dated entry to the running learning log in the Obsidian vault. The explicit-command sibling of journal-reflection's Post-deliverable capture mode; for end-of-day, weekly, decision-review, or new-framework reflection, use journal-reflection instead.
---

# /learned — post-deliverable learning capture

A 30-second human-learning loop: capture what a finished piece of work taught you, before it evaporates. This is the explicit-command entry point to the **Post-deliverable capture** mode defined in the `journal-reflection` skill — that skill holds the canonical procedure; this one is the fast `/learned` trigger. Origin: video-insights improvement #14.

## When to use

After finishing any substantive deliverable, when you want to bank the lesson. For a fuller reflection (end-of-day, end-of-week, a past decision, or a new framework), use `journal-reflection` instead — those are its other four modes.

/ wrap-up already offers this at session end; `/learned` is for any other moment.

## What to do

Ask these three, one at a time. Keep each answer to one line. Do not auto-answer; Ane's words go in verbatim.

1. What did this deliverable teach you about the work?
2. What would you do differently next time?
3. One thing to carry forward.

If Ane does not name the deliverable, ask for a 2–4 word label.

## File placement

Append to the single running log `5 JURNAL/Learning/deliverable-learning-log.md` in the Obsidian vault (`OBSIDIAN_VAULT_ROOT` = `C:/Users/AGasser/OneDrive/Ane Obsidian Vault`), exactly as the `journal-reflection` Post-deliverable capture mode specifies:

- If the file does not exist, create it with YAML frontmatter (`type: learning-log`) and an H1, then add the first entry.
- If it exists, append a new `## YYYY-MM-DD — <deliverable label>` section with the three answers as bullets, preserving all prior entries byte-identical (edit-preservation; apply `mel_wiki/wiki/concepts/edit-preservation-protocol.md`).

Local-only: if the vault path is not reachable (web session, other device), return the markdown in the reply and name the target path so Ane can save it manually.

## Limitations

Do not invent reflections. Do not lecture. One capture per invocation. This skill does not replace `journal-reflection` — it is the quick post-deliverable slice of it.
