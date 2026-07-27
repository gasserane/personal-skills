---
name: linkedin-field-note
description: "Produce and publish the next entry in Ane's personal AI Field Notes series on LinkedIn, end to end in five stages: (1) propose the next topic from the series ledger, (2) run a one-question-at-a-time voice/dictation interview to extract the lessons and story, (3) draft the article (.md canonical + Wine & Slate .docx) and the short post in the proven series format (BLUF by sentence three, P.S. AI-disclosure, series hashtags), (4) build the companion toolkit the article promises to the Start-with-three quality bar, (5) after Ane's per-artifact approval, publish on her LinkedIn via claude-in-chrome on the agreed calendar. Use whenever Ane says 'next field note', 'field note 04', 'AI Field Notes', 'new LinkedIn article', 'LinkedIn post about my AI work', 'draft the toolkit for the article', 'publish my field note', 'stage my LinkedIn post', or wants any personal AI/MEL thought-leadership piece for LinkedIn. Runs on Ane's personal brand (Wine & Slate via personal-brand/generators/pb.py), never IPPF branding. Not for IPPF-branded MA-facing learning products from an Evidence Brief (use learning-product), not for meeting notes (meeting-notes), not for a voice audit of existing text (ane-voice), not for LinkedIn profile edits."
---

# LinkedIn Field Note

One job: take the next AI Field Notes entry from "what should I write about?" to published on LinkedIn, reproducing the pipeline proven by hand on field note #01 (33-agent article + ultra-short post, 2026-07-21/22) and the Start-with-three toolkit (2026-07-26).

This is personal thought-leadership on Ane's personal brand. Wine & Slate tokens, warmth-inside-structure voice, self-irony allowed once per piece. It is not IPPF work: never use `ane_package.reporting.brand`, never the IPPF template.

## The hard rule

**Never publish, schedule, or stage anything Ane has not approved in the current session.** Approval is per artifact (article, post, first comment, toolkit PDF, visuals) and does not carry across sessions: if publishing happens in a later session, Ane re-confirms the final file with a one-line go before anything touches LinkedIn.

## Paths

| What | Where |
|---|---|
| Content folder | `C:/Users/AGasser/OneDrive/2. Ane's AREAS/AG Business/LinkedIn content/` |
| Series ledger | `<content folder>/field-notes-ledger.md` (create at first run: see `references/ledger.md`) |
| Brand tokens (canonical) | `C:/Users/AGasser/OneDrive/5 ANE CLAUDE work folder/personal-brand/brand-tokens.md` |
| docx/pptx helpers | `C:/Users/AGasser/OneDrive/5 ANE CLAUDE work folder/personal-brand/generators/pb.py` (+ `gen_report.py`, `gen_article.py`) |
| Visual spec (LinkedIn) | `2. Ane's AREAS/AG Business/Brand/BRAND-SPEC.md` |
| Quality-bar exemplars | `2026-07-26 Three-Agent Starter Kit (article companion).docx` and `Start-with-three.docx` (Ane's hand-edited final), `build_three_agent_kit.py`, `2026-07-22 LinkedIn POST v3 ULTRA-SHORT - 33-agent AI system.md` |

## Five stages

Run the stages in order for a new field note; enter mid-pipeline when Ane resumes one (the ledger records where every note stands). Read only the reference file for the stage you are in.

| Stage | What it produces | Read |
|---|---|---|
| 1 TOPIC | The next topic, chosen by Ane from 2-3 ledger-grounded proposals | `references/ledger.md` |
| 2 INTERVIEW | Lessons, story, numbers, toolkit promise — extracted one question at a time | `references/interview.md` |
| 3 DRAFT | Article `.md` + branded `.docx`, short post `.md`, first-comment text | `references/draft-formats.md` |
| 4 TOOLKIT | The companion artifact the article promises: generator script, `.docx`, `.pdf`, cover illustration, cover visual, and the caption for the document post | `references/toolkit.md` |
| 5 PUBLISH | The posts live on LinkedIn per the agreed calendar; ledger updated | `references/publish.md` |

After every stage: update the ledger entry for the note (status, paths, decisions). Milestone writes — draft and correct in conversation, write files at confirmed decision points, not per message.

## Standing rules (all stages)

- **Factual reliability.** Never invent facts, numbers, names, or quotes about Ane, her system, or her work. Every number in a draft (agent counts, check counts, page counts, dates) is verified against source in the drafting session or flagged `⚠️ verify before posting`. If a needed fact is not in loaded context, ask.
- **Voice.** Warmth inside structure: a two-sentence concrete story may open a piece, the finding lands by sentence three. Address the reader as "you". Plain English, translatability (a Romanian, Tunisian, Ethiopian, or Vietnamese English-speaking reader understands on first read), sentences under 25 words, active voice. No em-dashes in any prose Ane will publish. Self-irony at most once per piece, and the P.S. is usually where it lives.
- **AI-use disclosure.** The P.S. disclosure line is mandatory on every article and post: the piece is written with help from the system it describes, in Ane's drafts-verifies-decides framing. This is the series' credibility signature, not boilerplate.
- **Edit preservation.** Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists. Once Ane hand-edits a generated `.docx`, that `.docx` is authoritative: subsequent changes are targeted edits (docx-revision-pass method if that skill exists, else Word COM / python-docx scoped fixes), never regeneration from the `.md`.
- **Composition.** Before showing Ane a final draft, run the ane-voice checklist over it (Tier 1 register, personal warmth preserved). Her Word revisions route through docx-revision-pass when built. The dictation intake follows the meeting-notes charitable-transcription rules; the interview follows the grill-mel recommend-then-ask pattern.

## Close

End any working session on a note by telling Ane exactly where the note stands (stage, what is approved, what is pending) and what the next session starts with. The ledger carries the same state in writing.
