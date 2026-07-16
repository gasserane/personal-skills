# Learning document mode

Derive a 1-2 page shareable, plain-English learning document from a finished meeting note. Inputs: the meeting-notes `.docx` or `.md`, the source documents shared for the meeting, and the audience (internal / federation / partner). Output: branded `.docx` via `ane_package.reporting.word_export.write_word_report(template="general")`.

Exemplar (build to this standard): `1. Ane's PROJECTS/AI in IPPF EN 2026/Rutgers model/Learning document - Rutgers AI exchange - IPPF EN (July 2026).docx`.

## Rules (proven 2026-07-13, Rutgers exchange)

**Page cap by measurement, not word count.** The brand template runs ~300 effective words per page, so word counts under-predict pages. After each build, measure real pages via Word COM `ComputeStatistics(2)`. To shrink: trade the glossary block for inline glosses; strip the writer's spacer paragraphs; set `keep_with_next` on headings. Render page previews (Word → PDF → PyMuPDF) for a visual pass before declaring the cap met.

**One explanatory visual by default.** A matplotlib flow diagram styled with `apply_ippf_style()`, inserted post-generation via python-docx. Non-depictive visuals are allowed by default under the AI-imagery rules; anything depictive follows the sign-off tiers.

**Link discipline.** Hyperlinks embedded as `w:hyperlink` runs. Every URL verified in the same session. Sources not published online get "available on request from <organisation>" with the organisation's canonical site linked. Never fabricate a document URL.

**Partner-facing redactions.** No participant names (summary-anonymisation: role, country, organisation type). Internal analysis and management-ask sections dropped. "To be confirmed" items excluded. Claims about a partner verified against the partner's own source documents, not against the meeting note's simplifications; notes shorthand real policies and the shorthand can contradict the policy's actual mechanism.

**AI-use disclosure.** This is an external-facing artefact: include the disclosure in the method note per the Use of AI in IPPF EN Publications standard.
