# Reliability playbook — accreditation desk review

Every item below is a failure that occurred in a real review and the fix that resolved it.
Read this before touching the template. These are what separate a reliable run from a
corrupted document.

## 1. Word silently merges tables on save

**Symptom.** You record cell coordinates (table 31, row 0). Ane opens the file in Word,
reviews, saves. Next run, the coordinates point at the wrong cell, or a script throws
`IndexError`. The table count drops (e.g. 40 → 17) with no content change.

**Cause.** When Word saves a `.docx`, it concatenates consecutive tables that have no
paragraph between them into one table. Row indices shift; some standards' checks end up inside
a neighbouring table.

**Fix.** Never store or reuse table/row indices across runs. Locate every cell by **content**
on each run: track the current standard from `Standard X.Y` header text, match the standard
DESCRIPTION cell by `"comply with this Standard"`, and match check rows by a `^\d+\.\d+\.\d+`
regex on the first cell. `deskreview.py locate` does exactly this.

## 2. lxml `id()` is unreliable for cell dedup

**Symptom.** A verification that counts "distinct cells with a block" returns nonsense
(e.g. 14 when there are 100). Merged-cell iteration visits the same underlying cell many times.

**Cause.** `cell._tc` returns a fresh lxml proxy each access; Python reuses `id()` values after
garbage collection, so an `id()`-based `seen` set both over- and under-counts.

**Fix.** Verify by content. For each cell you *located* (by the content rules above), count
occurrences of the literal `"REVIEWER CONCLUSIONS"` in that cell's `.text`; assert exactly one.
Do not count over the whole-document string (column-merged cells repeat their text 2–6×, which
inflates the count). `deskreview.py verify` does the per-located-cell count.

## 3. Encoding — Romanian/French diacritics crash the console

**Symptom.** `UnicodeEncodeError: 'charmap' codec can't encode character 'ă'` when
printing `ă`, `ș`, `ț`, etc.

**Fix.** Run Python with `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8`. Read and write files with
`encoding="utf-8"`. When extracting to intermediate `.txt`, always specify the encoding.

## 4. Evidence that cannot be machine-read

**Reality of the inputs.**
- **Scanned PDFs** (compressed convocations, signed minutes, signed agreements) have no text
  layer → `pypdf` returns ~0 characters.
- **Legacy `.doc`** (old Word) is unreadable by `python-docx`.
- **Images** (`.png/.jpg/.jfif`), **archives** (`.rar/.zip`) carry no extractable text.

**Fix.** Treat each as a **data gap**, not as absent evidence: record that the document was
submitted but could not be verified at desk stage, and add an interview request to provide it
in readable form or to confirm its content. Never infer what a scanned constitution or an
unreadable contract says. Often the English version of a key document lives in a different
principle's folder (e.g. an English statute under "Well Governed") — look there before giving up.

## 5. Never write to a file open in Word

**Symptom.** `PackageNotFoundError` or `The process cannot access the file … because it is
being used by another process.`

**Fix.** Before any write, test the lock by opening the file for `ReadWrite` with no sharing.
If locked, stop and ask Ane to close it — do not retry blindly. The toolkit checks this.

## 6. Inserting vs replacing reviewer text

- **First pass (insert).** Append a new `REVIEWER CONCLUSIONS:` block below the MA text.
- **Enhance/elaborate pass (replace).** Remove the existing block (from the first paragraph
  starting `REVIEWER CONCLUSIONS` to the end of the cell) and append the new one. Keep all
  paragraphs *before* the block (the MA self-assessment) untouched.

Always re-read the cell first: on a second pass, Ane's manual edits to the reviewer text are
the authoritative base. Preserve her judgements; do not revert a verdict she sharpened or drop
a missing-document flag she added.

## 7. Backups and provenance

- Make a timestamped/labelled backup before every edit pass
  (`..._BACKUP-before-P4-revision.docx`).
- A shrinking file size between backups is a red flag that content was lost in a Word session
  (a whole principle's section can be deleted). Compare check-row counts per principle across
  backups to detect it, and offer to restore from the largest intact backup.

## 8. Two-level output, because the IPPF reader reads only the standard cell

The final IPPF reader typically reads only the **standard DESCRIPTION cell**, not the check
rows. So the standard-level conclusion must stand alone: synthesise every check beneath it,
pull the load-bearing evidence up, and consolidate the interview questions. The check-level
text is the supporting audit trail.

## 9. Cross-cutting findings

The highest-value findings cross standards. Watch for:
- The constitution describing service delivery (clinics/offices) the MA says it no longer runs
  → changes the **applicability** of the service-quality principle; do not accept "Not
  Applicable" at face value.
- A strategy with no results framework / no baselines-targets → recurs across the strategic-plan
  standard and the M&E standard; flag once and cross-reference.
- A policy cited in the self-assessment but absent from the evidence package → a pre-interview
  document request, not a pass.

## 10. House style

Tier 1 working brief: actor-first, active voice, sentences under 25 words, no em-dashes in body
prose (use hyphens in status labels), plain English, spell out acronyms on first use. Reviewer
text in purple `RGB(0x70,0x30,0xA0)`; status labels and headings bold.

## 11. A reviewer block that names another standard breaks cell location

**Symptom.** `apply` or `verify` mis-attributes cells: a Standard 4.1 conclusion lands under, or
is counted against, Standard 2.3. The content scan looks correct but the standard tracker jumped.

**Cause.** Cell location tracks the "current standard" by matching `Standard X.Y` in the first
cell of each row. A reviewer conclusion legitimately names other standards (for example "filed
under the strategy-and-policy standard 2.3"). Because the block is appended into the same cell,
the matcher read that 2.3 as a new header and reset the tracker for every cell after it.

**Fix.** Only honour a `Standard X.Y` match when it sits in the original cell text, before any
appended `REVIEWER CONCLUSIONS` marker. `deskreview.py` now guards both `iter_cells` (locate) and
`_scan_template` (verify/standalone) with this rule, so reviewer prose can safely name any
standard. You do not need to avoid naming standards in your conclusions. If you ever hand-roll a
locator, replicate the guard: `hp = text.find("REVIEWER CONCLUSIONS"); honour only if the match
starts before `hp`, or `hp == -1`.
