# Document marginalia mode

Turn decisions left as comments inside a reviewed Word document into a standard meeting note. The review cycle on a ToR or an implementation plan is a meeting that happened in the margins: people proposed, replied and agreed, and the record is `word/comments.xml` rather than a recording.

What makes this mode different from transcript mode is the anchor. Every comment is tied to the clause it annotates, and that tie is load-bearing twice. It is what makes several comments readable at all, and it is what lets the confirmed decisions be pushed back into the document set afterwards, because each one still knows which clause it changes.

## Flow

1. **Extract.** Run the driver; it does the reading so nothing is improvised:

   ```
   python scripts/read_marginalia.py "<path to the reviewed .docx>"
   ```

   Add `--out extract.md` to save it, `--json` for a machine-readable form, `--open-only` to drop comments Word marks resolved. Resolved comments are kept by default, because a point marked done in Word is still a decision the note has to record.

   The extract gives you, in document order and grouped under the heading each comment sits beneath: the comment text, its anchor, author, date, replies threaded onto their parent, and a flag on every date.

2. **Check the count before reading further.** The extract prints how many comments and threads it found. Open the document's review pane and confirm the number matches. Twelve comments in Word and eleven in the extract is a bug worth stopping for, and it is invisible once you are deep in drafting.

3. **Read each comment with its anchor, never alone.** This is the failure the mode exists to prevent. On 2026-07-24 a bare "Stef to discuss with Manuelle" was meaningless until it was read against the Follow-up-funding bullet it hung on. The extract puts the anchor above the comment for this reason; if you find yourself interpreting a comment without looking at the anchor line, stop.

4. **Classify each thread.** A comment is one of four things, and the note treats them differently:
   - a **decision** (the thread closes on an agreed change) — goes to `### Decisions`, numbered
   - an **action** (someone has to do something) — goes to the deadline-sorted tables with owner and deadline
   - a **question still open** — goes to `### Open / parked` with the trigger that should resurface it
   - **drafting comment** (typo, wording, formatting) — carries no decision and stays out of the note

   Threads matter here: a proposal with a reply agreeing to it is a decision; the same proposal with no reply is an open question. Do not promote an unanswered comment to a decision because it sounds confident.

5. **Confirm every flagged date with Ane. Never correct one silently.** The extract flags each date it finds and calls out any naming a month earlier than the comment itself. That specific shape is the 2026-07-24 slip: a comment reading "14-15 July" meant September, and a note that had quietly carried the July date would have been wrong and unremarkable. The script deliberately does not resolve the date or guess the year, because a plausible wrong date in a sent note is worse than a question.

   The guard reads English, French, Spanish and Romanian month names. It is a prompt to look, not a verdict.

6. **Interview.** Batch clarifying questions per the dictation-mode discipline: only what changes the note. Marginalia needs fewer questions than dictation, because the wording is written rather than spoken, but three things still need Ane:
   - the flagged dates
   - any thread whose outcome is genuinely ambiguous (proposal or decision)
   - the deadline and owner for actions, which comments almost never state

7. **Draft, confirm, write** per the shared note structure and milestone-write rule. Topics come from the document's own headings, which the extract already grouped by, so `## T1 - Budget` and `## T2 - Timeline` fall out of the document rather than being invented. Keep the tags stable if this document has been reviewed before.

8. **Keep the anchors.** In the `### Decisions` list, name the clause each decision attaches to (heading plus a few words, not the whole anchor). That is what makes the decision list usable as a change list afterwards. Handing that list to `/tor-procurement finalise` or `/office-review-pass` is the natural next step, and it only works if the anchors survived into the note.

9. **Tracker and memory** as in every note-producing mode: run `scripts/update_tracker.py` last, then offer the memory close-out.

## Things that will bite

**Tracked changes are shown accepted.** If a comment sits on a paragraph that also carries a tracked insertion or deletion, the extract marks it `±tracked` and the anchor text shows the change already applied. That is not what the commenter was looking at. When the reading turns on the exact wording, open the document with changes displayed before you trust the anchor.

**A comment can span several paragraphs.** It is reported once, at the paragraph where its range opens, which is where Word draws the balloon. If the anchor looks like it stops mid-thought, the comment covers more than the extract shows.

**Comments in tables are marked `in a table`.** Their anchor is a single cell, so the row context is missing. Read the table in the document before writing anything from a table comment.

**No comments found is usually the wrong input, not an empty meeting.** The driver exits with an error saying so. The common cause is that the reviewer left tracked changes rather than comments; `office-review-pass read` handles that document and shows both.

## Where this mode stops

It produces the note and the decision list, then hands off. Editing the reviewed document itself is a different job: `/tor-procurement finalise` for a ToR, `office-review-pass` for a general Word revision pass. Keeping those separate is deliberate, because a note written in the same breath as a document edit tends to record what was intended rather than what was changed.
