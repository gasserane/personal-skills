---
name: office-review-pass
description: 'Work on a Word deliverable inside the .docx itself: read and engage reviewer comments, apply real Word tracked changes a counterparty can accept or reject, make scoped formatting-preserving fixes via Word COM, or add a branded glossary and verified source annex. Use when Ane hands over a commented or hand-edited .docx for review, markup, or in-file edits. Distinct from ane-voice (prose voice only, never touches the file), localise (target-language work), check-deliverable (read-only QA verdict), and tor-procurement (builds ToRs).'
model: opus
---

# /office-review-pass — review and revise a Word deliverable without breaking it

One job: move a .docx through a review cycle and come out the other side with Ane's formatting intact and every change verifiable in the written file.

All Office surgery lives in `ane_package.officeops`. This skill contributes judgement, not plumbing. If a mode needs a capability officeops lacks, add it to officeops and test it there — that is what keeps this skill thin, and it is why the module was extracted first. `references/officeops-api.md` carries the exact call signatures; read it before writing any code.

## Mode routing

- **read** — a document carries comments, or needs an expert read. Read-only.
- **track** — edits must be visible and reversible by someone else. Writes a marked-up copy.
- **revise** — Ane has agreed the fixes and wants them applied in place. Edits her file.
- **annex** — the document needs a glossary and a source annex appended.

Modes chain: `read` produces findings, `track` or `revise` applies them. If the mode is ambiguous, ask in one line before working. The dividing question between `track` and `revise` is **who decides**: if a counterparty must be able to reject an edit, it is `track`; if Ane has already decided, it is `revise`.

## Shared rules — all modes

- **Ane's file is the baseline.** Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists. Read what is on disk, change only what was asked, leave everything else byte-identical. Never regenerate the document, and never rebuild it from what the chat says it contains — chat shows what the system produced, disk shows what Ane then did to it.
- **Verify on the written file, never on the call returning.** Reopen the saved .docx and assert with `officeops.verify`. A `save()` that returned proves nothing: six ToR versions shipped with the palette but no logo, and every one of those runs exited cleanly.
- **Never invent a fact.** Names, dates, figures, article numbers, URLs, MA names. If it is not in the document or in loaded context, ask. This binds hardest in `annex` mode, where a plausible URL is indistinguishable from a real one until someone clicks it.
- **Report in the EDIT-PRESERVATION DELIVERY format**: what changed, what was left alone, and out-of-scope observations listed but not acted on.

## read mode

The point is not to summarise the document. It is to give Ane a second expert opinion that has actually engaged with what she already noticed.

1. **Render the document with its comments in place.**
   `python scripts/review_pass.py read <path> --out review.md`
   This wraps `officeops.comments.render_review`, which walks the body in document order and prints each comment where its range opens, with the anchor words it covers, its author, its resolved state and any replies nested underneath. Read that file, not the raw .docx.
2. **Read the whole document first, then the comments.** Forming a view before absorbing hers is what makes the cross-read worth anything. A model that reads her comments first tends to agree with all of them.
3. **Cross-read every comment** and place it in one of three buckets, saying which:
   - **Agree** — and add what she did not say: the consequence, the fix, the clause it collides with.
   - **Push back** — with the reason. Her comments are a peer reviewer's input to engage with, not instructions to execute. A review that agrees with everything told her nothing she did not already know, which is the failure mode this mode exists to prevent.
   - **Reframe** — she is pointing at a real problem but has diagnosed it one level too shallow or too deep.
4. **Add findings she missed**, marked as such, each anchored to a block number from the rendering so she can go straight there.
5. **Deliver** BLUF first: the verdict on the document in one sentence, then the load-bearing reason, then the comment-by-comment cross-read, then your own findings. Tier 1 working brief unless the document's own audience says otherwise.
6. **Offer a transmittal email** to the document owner — do not write it unprompted. When Ane wants it, it is short, names the two or three things that matter, and attaches rather than recounts.

Tracked changes count as review input too: `render_review` shows insertions as accepted and deletions as gone, and marks those blocks `+ins` / `-del`. `officeops.tracked.read_revisions(path)` gives them individually with author and date when a change needs discussing on its own.

**On register.** A document under review usually has an author who is not Ane. Findings are about the text, never the person, and the collaborative voice holds — "the acceptance criterion is not stated" rather than "the author failed to state".

## track mode

For contractor proposals, partner documents and translation reviews: the counterparty opens the file in Word, sees each change attributed, and accepts or rejects it one by one.

1. Confirm the edit list and the author name that should appear on the changes. Attribution is the whole point — an unattributed tracked change reads as a system artefact.
2. Write the edits to a JSON file and run
   `python scripts/review_pass.py track <path> --edits edits.json --author "Ane Gasser" --out marked-up.docx`
   or drive `officeops.tracked.TrackedEditor` directly when the edits need logic. Either way this writes a COPY; the source stays untouched.
3. **Check the returned count for every edit.** `.replace()` returns how many it made. A `0` means the search string was wrong, not that the document was already correct — the two look identical in a success message and only one of them is true.
4. **Verify on the written file with `read_revisions`, never with `paragraph.text`.** python-docx does not read text inside `w:ins`, so after a tracked insertion the paragraph reads as though the new words are absent. Asserting on `paragraph.text` will tell you the edit failed when it succeeded. `python scripts/review_pass.py revisions marked-up.docx` prints what actually landed.
5. Report each edit with its count, and hand over the marked-up path plus a one-line note on what the recipient will see.

Comments and tracked changes travel well together: `officeops.comments.add_comments` adds margin comments to a copy, so a marked-up document can carry both the change and the reason for it. Match strings must be five or more consecutive words and hit exactly one paragraph — zero or several raise rather than guess, because a comment on the wrong paragraph reads as a review error rather than a tooling error. Catch that raise and re-pick the string; do not loosen the match.

## revise mode

Ane has hand-edited the document. Formatting is hers, and python-docx run edits are what break it — a phrase split across three runs comes back as one run with the first run's formatting, silently.

1. **Confirm the scope.** The agreed list, nothing more. Anything else you notice goes in the report, unapplied.
2. **The file must be closed in Word.** COM drives a live Word instance; an open handle gives `PackageNotFoundError`, which reads like corruption and is not.
3. Run `python scripts/review_pass.py revise <path> --edits edits.json`, wrapping `officeops.wordcom.find_replace`. A timestamped backup is written automatically before the first edit, because COM edits in place and there is no undo.
4. **Read the returned counts and report them.** The function reads them back out of Word rather than assuming. Any pair returning `0` is a wrong search string and must be raised with Ane, not quietly dropped. Pass `--headers` when the text also sits in the header or footer, which is where contact blocks and document titles hide.
5. **Verify the written file**: `python scripts/review_pass.py verify <path>` runs the branding, header/footer, stranded-hyperlink and word-count assertions. Stranded hyperlinks are the specific damage a text replacement does — the words go, the relationship stays, and the document ships with a link to nothing.

**The PDF.** `officeops.wordcom.export_pdf` refuses by default and it is right to. `ExportAsFixedFormat` hangs indefinitely on the Wine & Slate kit documents: page counts return, the export never does, and the Word process stays alive holding the file. So this mode does not produce the PDF. Finish by telling Ane, in one line, to export it by hand from Word — File, Save As, PDF. Only pass `allow_known_hang=True` if she confirms this specific document is unaffected, and treat that as her call rather than yours. Papering over a hang with a longer timeout wastes minutes and still fails.

## annex mode

Two appended sections, both of which exist so a reader outside the drafting team can follow the document without asking anyone.

1. **Glossary** — every acronym and technical term the document uses, expanded, with a plain-English gloss of six words or so where the expansion alone does not help. Read the document to build this; do not work from a standard list, because the standard list will contain terms this document never uses and miss the ones it invented.
2. **Source annex** — every referenced document, law, standard and framework, with a clickable hyperlink.
   - **Verification means WebSearch or WebFetch in this session.** A URL recalled from training data is a guess wearing a link, and it is the single most damaging thing this mode can ship.
   - Prefer the canonical publisher, then a direct PDF on that domain, then an institutional repository or DOI. Aggregators only alongside a canonical link.
   - Anything that will not verify is flagged `⚠️ URL unverified — confirm before publication` and left without a link. Never guess a plausible one.
3. Match the document's existing heading styles rather than introducing new ones, and keep the IPPF Visual Identity 2025 template intact.
4. **Verify**: `verify.hyperlink_targets` confirms each link resolves to the address intended, and `verify.stranded_hyperlinks` confirms none were orphaned. Report the count of terms, the count of sources, and every unverified item explicitly.

## Verification plan

Every mode states its check before it works, and the check reopens the written file:

| Mode | What gets asserted |
|---|---|
| read | Read-only — nothing written. Report the block count and comment count from the rendering. |
| track | `read_revisions` on the written copy: one insertion and one deletion per replacement, author and date set. |
| revise | Replacement counts read back from Word, then `verify` — branding, header/footer, no stranded hyperlinks, word count. |
| annex | `hyperlink_targets` plus `stranded_hyperlinks`, and the count of sources that failed verification. |

`python scripts/test_review_pass.py` checks the driver itself — that both edit-file shapes load, that a marked-up copy never overwrites its source, and that a search string matching nothing exits non-zero. That last one is the reason the driver exists rather than a hand-written snippet each time: a review round that applied none of its edits produces a file that looks exactly like one that applied all of them. Office behaviour itself is covered by `tests/test_officeops.py` in the work folder.

## Scope boundary

- English prose voice on its own, with no file surgery, is `ane-voice`. A read-only QA verdict on a finished brief is `check-deliverable`. Target-language work is `localise`. Building a ToR from a generator is `tor-procurement`.
- Excel repair and canonicalising a stale generator are `office-repair` (Wave 3), not this skill.
- COM modes need Windows, Word, and the file closed. On a web container the read and track paths still work — they are pure python-docx and lxml — and `revise` does not.
- A document that leaves IPPF after an AI-assisted pass is an AI-assisted publication: offer the colophon per `mel_wiki/wiki/concepts/ai-use-in-publications.md`. Routine grammar-only edits are exempt.
