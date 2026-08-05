# `ane_package.officeops` — the API this skill sits on

Read this before writing any code. Every name below already exists and is tested
(`tests/test_officeops.py`; run `python -m pytest tests/test_officeops.py -q` for the
current check count — a pinned number here went stale twice). Do not invent names, and do not re-implement
Office surgery inside the skill: a capability this skill needs and officeops lacks is
an addition to officeops, with its own test.

Import from the package root; the COM submodules are lazy so importing the package
on a machine without Word still works.

```python
from ane_package.officeops import (
    Checks, Comment, CommentRequest, ReviewBlock, TrackedEditor,
    add_comments, read_comments, read_review, render_review, review_blocks,
    read_revisions, assert_branded, docx_word_count, hyperlink_targets,
    stranded_hyperlinks,
)
from ane_package.officeops import wordcom          # Windows only
```

If the import fails from outside the work folder, call
`officeops.bootstrap.ensure_ane_package_importable()` first, or set `WORK_FOLDER_ROOT`.

## Contents

- [Reading a review](#reading-a-review) — read mode
- [Tracked changes](#tracked-changes) — track mode
- [Word COM](#word-com) — revise mode
- [Verification](#verification) — all modes
- [Traps](#traps)
- [Writing a branded document](#writing-a-branded-document) — not officeops, but check here before building one

## Writing a branded document

`officeops` reads, marks up and repairs Word files. It does not *author* them.
Anything that writes a branded document lives in `ane_package.reporting`,
reading `IPPF_FORMAT_TEMPLATE`. Two entry points, and they are not
interchangeable.

```python
from ane_package.reporting.word_export import (
    WordReport, Section, FindingCard, artifact_labels, write_word_report,
)
from ane_package.reporting.markdown_docx import (
    render_markdown, render_markdown_file, RenderReport,
)
```

`write_word_report` takes a fixed analytical shape: bottom-line-up-front
bullets, then sections with finding cards, then a method note and a glossary.
Right for a report or a brief.

`render_markdown` renders a markdown subset — headings `#` to `###`, `**bold**`,
`[text](url)` as real hyperlinks, lists to two levels, pipe tables, rules —
against the same brand. Right for an agenda, a run sheet, a note template or
anything whose structure *is* the content, where the report skeleton fights the
document. Markdown stays the source of truth and the `.docx` is regenerated.

It returns a `RenderReport`. **Read `report.unsupported` and surface it.**
Constructs it cannot render structurally (code fences, block quotes, images,
headings below `###`, lists nested deeper than two) are recorded there and their
text is still written, so a page can lose formatting but never content. A
renderer that swallows them silently produces a document that looks complete and
is not.

Both default to `template="general"` (logo header on every page, pillar footer).
Use `"letterhead"` only for memos and correspondence.

**The branded base carries no `List Bullet`, `List Number` or `Table Grid`
style**, so any list writes its glyph onto `IPPF Body` and indents, and any
table sets `tblBorders` XML directly. Asking python-docx for one of those styles
raises `KeyError` at render time. Both modules above already handle it; a new
builder has to.

## Reading a review

```python
render_review(path, include_resolved=True) -> str
```
The document as plain text with every comment at its anchor. This is what read mode
reads. Blocks are numbered `[n]` in document order so a finding can cite one.

```python
review_blocks(path, include_empty=False) -> list[ReviewBlock]
```
The structured form behind the rendering. `ReviewBlock` carries `.index .text .style
.in_table .comments .has_insertions .has_deletions .bold` and the two heading tests,
`.is_heading` and `.looks_like_heading`. A comment attaches to the block where its
range **opens**, so a comment spanning three paragraphs is reported once.

**Use `.looks_like_heading` on anything built on the IPPF letterhead.** The base
carries no `Heading` style, so `tor_docx.py` and its siblings write section headings
as direct bold formatting and `.is_heading` finds none at all: a first run over the
AI-for-Research ToR placed all 23 comment threads in section `""`.
`.looks_like_heading` falls back to a short fully-bold line (120 characters or less,
not a list style). `.is_heading` keeps its style-only meaning for callers that need
certainty.

```python
read_comments(path) -> list[Comment]
read_review(path)   -> {"comments": [Comment], "revisions": [Revision]}
```
`Comment` carries `.id .author .initials .date .text .anchor .parent_id .resolved`
and `.is_reply`. `.anchor` is the document text the comment range covers, read from
`commentRangeStart`/`End` — a finding never arrives without the words it is about.
Replies point at their parent through `.parent_id`.

```python
comment_threads(path, include_resolved=True) -> list[CommentThread]
same_person(left, right) -> bool
```
`read_comments` returns replies as siblings of what they answer, which is the wrong
shape for deciding what still needs a response. `CommentThread` groups a root comment
with its replies (following a nested reply up to its true root) and carries `.root
.replies .section .section_index .block_index .in_table .anchor .last_author`, plus
`.answered_by(author)` and `.is_open(author="")`. `.section` is the nearest preceding
heading, which is **not** the same question as `.anchor`: a reviewer selects a phrase
and writes about the clause behind it, and on the 2026-07-31 ToR round the objection
under discussion was anchored three sections away from the argument.

`same_person` compares two Word author strings by containment, because one person
appears under several profiles. That ToR carries `Ane Gasser`, `Ane Gasser PERSONAL`
and `Ane Gasser [2]`; exact matching reports a thread she has answered as still open.

**A reply is only threaded when the reply button was used.** An answer typed as a new
comment on the same paragraph is a root of its own, so `.replies` can be empty beside
an answer that plainly exists. Check for other threads sharing a `.block_index` before
concluding nobody replied.

```python
add_comments(source, requests: list[CommentRequest], out_path=None) -> Path
CommentRequest(match, text, author="Ane Gasser (MEL review)", initials="")
```
Writes anchored margin comments to a **copy**; refuses to comment in place. Matching
is paragraph-level and requires exactly one hit — see [Traps](#traps).

```python
add_comments_in_place(source, requests, backup=True) -> Path | None
```
The annotate-mode variant: comments land in ``source`` itself. Ordering is
verify-before-replace — the commented copy is written beside the original, asserted
on (every new comment present, every pre-existing comment preserved under its own
id, body word count unchanged), and only then is the original copied to a
timestamped ``_BACKUP_`` file and atomically replaced. Returns the backup path
(``None`` when ``backup=False``). A bad anchor or a failed assertion raises and
leaves the original byte-identical. Anchor matching and the exactly-one-hit rule
are ``add_comments``'s, including table paragraphs.

## Tracked changes

```python
from docx import Document
document = Document(str(path))
editor = TrackedEditor(document, author="Ane Gasser")
count = editor.replace(old, new, limit=None)   # -> int, how many were made
editor.delete(text, limit=None)
editor.insert_after(anchor, text, limit=1)
document.save(str(out))
```
Real `w:ins` / `w:del` / `w:delText` with run splitting, so a phrase split across
runs is matched. `w:id` allocation is document-wide, so a second review round does
not collide with the first. python-docx cannot author these; this is the only path.

```python
read_revisions(path) -> list[Revision]     # .kind ("insertion"|"deletion") .text .author .date
```
The only correct way to assert a tracked edit landed.

## Word COM

Windows, Word installed, and the file **closed in Word**. An open handle raises
`PackageNotFoundError`, which reads like corruption and is not.

```python
wordcom.word_available() -> bool
wordcom.find_replace(path, pairs, match_case=True, whole_word=False,
                     include_headers=False, track_changes=None,
                     backup=True, timeout=600) -> dict[str, int]
```
`pairs` is a dict `{old: new}` or a list of `Replacement(old, new)`. Returns search
string to the number of replacements **read back from Word**. A pair returning `0`
is a wrong search string, not a no-op. A timestamped backup is written before the
first edit; COM edits in place and there is no undo.

```python
wordcom.export_pdf(path, out_path=None, allow_known_hang=False, timeout=300) -> Path
```
**Refuses by default.** `ExportAsFixedFormat` hangs indefinitely on Wine & Slate kit
documents — page counts return, the export does not, and Word stays alive holding
the file. Export by hand from Word. Only pass `allow_known_hang=True` when Ane
confirms this document is unaffected.

## Verification

```python
assert_branded(path)                      # header + footer + logo, together
assert_header_footer_present(path)
assert_logo_present(path)
assert_markers_absent(path, markers)      # placeholder strings that must not ship
assert_no_alternate_content(path, where="header")
hyperlink_targets(path)    -> {rId: url}
stranded_hyperlinks(path)  -> {rId: url}  # relationships nothing in the body references
docx_word_count(path, include_tables=True) -> int
table_row_counts(path) / assert_table_covers_rows(path, table, expected)
```

`Checks` is the pass-fail collector: `checks.check(condition, label)`,
`checks.expect(label, fn, *args)` for a call that should not raise, then
`checks.report()` returns a process exit code.

Assertions run on the **written file**. A `save()` that returned proves nothing:
six ToR versions shipped with the palette but no logo, and each run exited cleanly.

## Traps

1. **`add_comments` matches at paragraph level and needs exactly one hit.** Zero or
   several raise rather than guess, and no half-written copy is left behind. Pick
   match strings of five or more consecutive words, and catch the raise rather than
   loosening the match — a comment on the wrong paragraph reads as a review error.

2. **`paragraph.text` does not include text inside `w:ins`.** After a tracked
   insertion the paragraph reads as if the new words are not there. Never assert on
   it after a tracked edit; assert on `read_revisions(written_path)`.

3. **`render_review` shows tracked changes as accepted** — insertions present,
   deletions gone — because reviewing the accepted state is the useful default.
   Blocks carrying changes are marked `+ins` / `-del` so the reading is visible.

4. **Word stores headers twice**, as an `mc:Choice` drawing and an `mc:Fallback` VML
   twin. Text removed from one survives in the other.
   `assert_no_alternate_content` catches it.

5. **`win32com` is not installed in this Python.** Both COM surfaces drive
   PowerShell 5.1 through an ASCII script file with a UTF-8 payload beside it. Do
   not reach for win32com, and do not switch to pwsh 7 — its null-method handling
   breaks the Excel path.

6. **TOC cached text lives in hyperlink runs `paragraph.runs` cannot reach.** A
   run-level replace over `p.runs` updates the body heading but leaves the stale
   wording in the TOC's cached entry, because TOC lines are hyperlinks and
   python-docx does not expose their runs. After heading renames, do an XML pass
   over every `w:t` in the document part for the old string, and tell Ane to
   refresh the TOC in Word (Ctrl+A, F9) so pagination regenerates. Proven
   2026-08-04 on the MELA framework five-CLQ alignment.

7. **.odt input: convert through Word COM first.** `Documents.Open` on the .odt
   then `SaveAs2(dst, 16)` yields a .docx that keeps formatting AND carries ODT
   annotations over as real Word comments (`read_comments` sees them), opening the
   whole officeops toolchain to OpenDocument files. Drive it through
   powershell.exe 5.1 per trap 5; keep the .odt untouched as the archive copy and
   treat the converted .docx as the new canonical. Proven 2026-08-04, three
   comments carried.
