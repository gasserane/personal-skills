# Handwritten notes mode (photo or scan)

Turn photographed or scanned handwritten meeting notes into verified, structured meeting notes. Inputs: one or more image paths or scanned PDFs, plus a project-context folder when Ane names one.

## Flow

1. **Read every photo page** with the Read tool (it renders images). Read all pages before drafting anything: handwritten notes routinely continue a topic across pages.

2. **Verify against the context folder.** Scan the folder Ane names (documents, .eml files) to verify names, roles, dates and project facts appearing in the handwriting. Handwriting plus memory is not a source for a name or contact: never guess or reconstruct one. What the context folder cannot confirm gets asked or flagged.

3. **Interview on uncertain readings.** Batch ambiguous readings as clarifying questions (same discipline as dictation mode: max 5, only what changes the note) rather than silently interpreting. A misread "not" inverts a decision.

4. **Draft** in the shared note structure (header, deadline-sorted action tables, per-topic Key takeaways / Decisions / Next steps / Open-parked). Flag any remaining uncertain readings inline as `⚠️ Data gap: [unclear reading] - [why it matters] - [confirm with ...]`.

5. **Write** the `.md` and the branded `.docx` (word_export, template="general") after Ane confirms, per the shared rules.

6. **Hard rule, learned 2026-07-11:** once Ane hand-edits the generated `.docx`, that file becomes authoritative. Any later change is a targeted python-docx edit to her file, never a regeneration from the `.md`. Regenerating silently destroys her manual edits.
