---
name: meeting-notes
description: "Turn Ane's meetings and 1-1s into structured, branded meeting notes from ANY capture method, and prepare the next one. Five modes, selected by input: (1) dictated notes - Ane dictates per topic, the skill runs a clarification interview, drafts per-topic sections and deadline-sorted action tables, writes .md + IPPF-branded .docx; (2) 1-1 prep - builds the prep sheet for the next biweekly manager 1-1 from the previous note's actions and parked items; (3) handwritten notes - converts photos or scans of handwritten meeting notes into verified notes using a project-context folder; (4) recordings and transcripts - processes voice/video recordings (via the local analyze-video pipeline) or platform transcripts (Teams .vtt/.docx) into notes; (5) learning document - derives a 1-2 page shareable learning document from finished notes. Other captures (chat logs, email threads, whiteboard photos) normalise to text and follow mode 4. Use whenever Ane says 'meeting note', 'meeting notes', 'minutes', 'I want to dictate my meeting', 'debrief my 1-1', 'prep my 1-1', 'prepare my meeting with Lena', 'draft notes from this photo or scan of my notebook', 'process this meeting recording', 'here is the Teams transcript', or 'learning document from these notes'. Not for importing typed claude.ai sessions (capture-desktop), options papers (decision-memo), personal reflection (journal-reflection), daily planning (daily-brief), or analysing FGD/research videos for MEL evidence (video-content-analysis directly)."
---

# Meeting Notes

One skill for the full 1-1 and meeting-note lifecycle: prep → meeting → dictated or photographed notes → shareable learning document → next prep. The modes share one file convention, so each meeting's outputs become the next meeting's inputs.

## Mode selection

| Signal from Ane | Mode | Read |
|---|---|---|
| "I want to dictate", "debrief my meeting/1-1", spoken-style topic summaries | Dictated notes | `references/dictation-mode.md` |
| "prep my 1-1", "prepare my meeting with [manager]", "what do I owe Lena" | 1-1 prep | `references/prep-mode.md` |
| Image or scan paths + "draft notes from this photo/scan", handwritten notes | Handwritten notes (photo/scan) | `references/photo-mode.md` |
| A voice/video recording file, or a transcript (Teams .vtt/.docx, txt) | Recordings and transcripts | `references/transcript-mode.md` |
| "learning document", "shareable summary of this meeting" + a finished note | Learning document | `references/learning-document-mode.md` |

Read only the reference file for the selected mode. If the mode is ambiguous, ask in one line; do not guess between prep and notes. Any other capture method (chat log, email thread as minutes, whiteboard photo) normalises to text and then follows `references/transcript-mode.md` from step 2, so every way a meeting gets captured has a route into the same note structure.

## Shared rules (all modes)

**Storage.** Recurring 1-1 notes and preps live in `C:/Users/AGasser/OneDrive/1. Ane's PROJECTS/Ane Plans/`. Project-meeting notes live in the project folder Ane names. Naming: `Meeting note - Ane-<counterpart> - YYYY-MM-DD.md` and `1-1 prep - Ane-<counterpart> - YYYY-MM-DD.md`. The `.md` is the source of truth; the `.docx` is generated from it, never dual-edited.

**Factual reliability.** Dictation and handwriting garble names, numbers and dates first (this is why the interview exists). Never guess or "correct" a name from a pattern: confirm it with Ane or verify it against a context document. Known-correct facts come from `~/.claude/CLAUDE.md`, memory, or the project folder; everything unverifiable gets flagged `⚠️` and asked.

**Milestone writes.** Draft and correct in conversation; write files only at confirmed milestones (all topics confirmed, prep sheet approved). One write, not one per message.

**Note structure** (the proven template, settled 2026-07-16):
1. Header: date, participants, type line, topic list with stable tags (T1, T2, ...). Keep tags stable across notes so T1 always means the same workstream for a given counterpart.
2. `## Next actions at a glance`: two deadline-sorted tables (Deadline | Topic | Action), one for Ane, one for the counterpart ("to chase"). Deadline-sorted because "what do I owe today" is the question the note gets reopened for. Actions owned by third parties go into the table of whoever chases them (Ane or the counterpart), with the actual owner named in the Action cell.
3. Per topic `## T<n> - <name>`, each with `### Key takeaways` (max 5 synthetic bullets), `### Decisions` (confirmed only), `### Next steps` (Ane / counterpart, with deadlines), `### Open / parked` (each item with the trigger date or event that should resurface it).
4. Footer: preparation provenance with AI-support disclosure.

**Register and voice.** Tier 1 working record: plain English, active voice, sentences under 25 words, no em-dashes anywhere in the output, numbers and dates explicit. Decisions are numbered so they can be cited later ("T3 decision 2, 16 Jul").

**Word output.** Generate the `.docx` from the `.md` via `ane_package.reporting.word_export.write_word_report(template="general")` when the note shape fits its layout; for table-heavy notes build directly with python-docx using `ane_package.reporting.brand.IPPF_FORMAT_TEMPLATE` constants (Barlow Medium, dream #00313C headings-on-red #EB3300 titles, dream header rows). Never hard-code off-brand colours or fonts.

**Edit preservation.** Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists. In particular: once Ane hand-edits a generated `.docx`, that `.docx` becomes authoritative; subsequent changes are targeted python-docx edits, never regeneration from the `.md`.

**Privacy.** Meeting notes are personal working records: names may appear in them. Anything shareable (the learning document, or a note Ane says she will send) follows summary-anonymisation: roles and organisation types, not names, and internal analysis sections dropped. Never quote `5 JURNAL` vault content.

**Centralised action tracker.** Every confirmed note also feeds one Excel workbook (`Ane Plans/Meeting actions tracker.xlsx`): one tab per person for actions with deadline and status, a Decisions log, and a Pending tab for parked items. Run `scripts/update_tracker.py` as the last step of any note-producing mode; it only appends (stable IDs, idempotent), so Ane's manual Status and Progress edits are never touched. Details: `references/action-tracker.md`. Prep mode reads this tracker for its status pass; the tracker's Status column beats the older note text.

**Memory close-out.** After a note is confirmed, offer to persist durable project facts (confirmed decisions, changed budgets, new deadlines) to auto-memory, updating existing project memories rather than duplicating. The note captures the meeting; memory carries what future sessions must know.
