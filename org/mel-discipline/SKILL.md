---
name: mel-discipline
description: Use when producing any MEL/SRHR analytical deliverable (brief, evaluation design, indicator set, ToC, evidence review, data analysis), especially under deadline pressure, on Opus/Sonnet/Haiku-class models, or when tempted to cite a source without opening it, skip a verification pass, or deliver in one draft. Also use when a task or prompt asks for "working discipline" or "five gates".
---

# MEL Working Discipline (Five Gates)

## Overview

Rigour is a procedure, not a talent. This skill encodes the working discipline that top-tier models apply by default, so any model produces deliverables that survive a demanding reviewer's quality gate. Every analytical deliverable passes five gates, in order. Skipping a gate under deadline pressure is the failure mode this skill exists to prevent: a wrong citation in front of a Director costs more than the two minutes verification takes.

**Violating the letter of a gate is violating its spirit.**

The five gates below stand on their own in any setting, including a plain chat. Whenever you can run code or save a file, every mechanical Gate 4 check (em-dash search, word count, number recompute) uses that tool. Checking by eye is the fallback only when no tool can run, and the Gate 5 report names each check done by eye. Where your setup offers more (standing instructions, a knowledge wiki, a resource library, an orchestration command, a quality gate), the "If available" section at the end says how to use it. Use it if it's there; otherwise the built-in standards here apply.

## Gate 1 — SCOPE before working

State in your first lines of work (not in the deliverable):
1. The task in one sentence, and the decision it drives.
2. Audience tier and register. Default: Tier 1 working brief for colleagues who are not MEL specialists, 500–2500 words, verdict first, sources listed in an `**Evidence base:**` line at the end of each section rather than inside sentences. Use the Tier 2 publication register (inline citations, no length cap) only when the task names a publication, journal article, peer-reviewed paper, or externally released report. If your standing instructions define audience tiers, they take precedence.
3. **Verification plan:** one line naming which facts, citations, or numbers you will check, and how.
4. **Pre-mortem:** the single most likely way this deliverable misleads its named reader.

## Gate 2 — EVIDENCE before reasoning

- Materials you were given, then your own knowledge sources (any wiki, library, or team documents you can reach), BEFORE web search.
- Search-effort ladder: 1 search for a single fact; 3–5 for a medium task; 5–10 for deep research or comparison. State when you stop and why.
- **Citation rule: no source enters the deliverable unless you opened it this session.** A citation you recall but did not open is either deleted or flagged `⚠️ URL unverified — confirm before publication`. Partial recognition from training is not current knowledge.
- For any claim about what a source says, open the document itself, not a news item or summary page. If only a summary is reachable, cite it at that level and say so.
- Every kept citation: author + year + title + venue, plus a canonical link (publisher, institution, or repository; never an aggregator as sole link).
- Recency: check for a superseding edition; if citing an older source deliberately, say why in the standard form: `(no superseding edition as of [date])` for an older source cited because nothing newer exists, or `(canonical reference; subsequent literature builds on but does not supersede)` for a foundational text.

## Gate 3 — REASON adversarially

- Name the strongest objection to your own recommendation IN the deliverable, and answer it or concede it.
- For causal or contribution claims: list the rival explanations and what the evidence says about each. For each rival, name the cheapest observation that would tell it apart from your explanation, and state the result that would change the recommendation.
- Agreement is a finding, not a reflex: if the obvious answer survives the objection, say why.

## Gate 4 — VERIFY before declaring done

Run this checklist on the finished draft. **Perform each check physically; never report a result you did not produce.** In this skill's own wording test, a model reported "em-dash sweep: zero ✅" over a body containing five em-dashes. A claimed PASS without the performed check is itself a Gate 4 violation. Rows 2, 5 and 6 use code or a tool whenever one can run.

| # | Check | How |
|---|---|---|
| 1 | Every citation opened this session or flagged unverified, walked source by source through the Evidence base line, including frameworks, tools, and commissions named as design anchors; "well-known" grants no exemption | Trace each named source to the fetch/read that opened it, or attach the ⚠️ flag to that specific source. Observed failure (2026-07-07): a draft verified 1 of 4 Evidence-base sources and batch-passed the rest as canonical |
| 2 | Em-dash sweep: zero U+2014 in body prose (two literal flag formats exempt: the data-gap separator `⚠️ Data gap: [what] — [why] — [action]` and the unverified-URL flag `⚠️ URL unverified — confirm before publication`) | Save the draft and search it for U+2014 with code or a text search on the draft. With no tool, re-read paragraph by paragraph and say so at Gate 5. Rewrite each hit as a comma, colon, or two sentences |
| 3 | BLUF: sentence 1 of the deliverable is the verdict or answer, with no preamble, aside or note box above it | Read sentence 1 |
| 4 | Data gaps flagged in the standard format, never papered over | Scan for asserted-but-unsourced claims |
| 5 | Numbers recomputed once from source, not carried forward on trust | Recompute with code when it can run, and state both values |
| 6 | Tier register: length 500–2500 (Tier 1), citations off the running prose, acronyms spelled on first use, plain-English verbs | Count the words in the deliverable body with a tool; with none, count by hand section by section and report a hand count. Never estimate. Scan the rest |

## Gate 5 — REPORT faithfully

- State what you verified and what you could not. An unverified item reported plainly beats a confident guess.
- Name each Gate 4 check done by eye, not with a tool.
- No hedging in the verdict; no overclaiming in the findings. "Will" for commitments, "should" for recommendations.
- If the deliverable cannot reach standard with available information, say so with a data-gap flag instead of filling the gap with generic content.

## Rationalizations — all mean STOP

| Excuse | Reality |
|---|---|
| "No time to verify, they need it in 20 minutes" | Gate 4 takes 2 minutes. A fabricated citation in a management meeting costs the deliverable's credibility entirely. |
| "I remember this source, the link looks right" | Plausible-but-unchecked is the signature failure. Open it or flag it. |
| "It's only a working brief, not a publication" | Rigour is constant across tiers; only citation placement moves. |
| "The draft is clearly good, checks are overkill" | The baseline test for this skill produced a good-looking brief with a likely-fabricated citation and four em-dashes. Good-looking is not verified. |
| "I'll note the caveats mentally" | Unwritten caveats do not exist. Gate 5 puts them in the deliverable. |
| "I checked it while writing, no need to sweep again" | The with-skill test asserted a clean em-dash sweep over five em-dashes. Checks done "while writing" are assertions. Perform the literal search on the finished draft. |

## Red flags — stop and run the gate you skipped

- Pasting a URL you did not open this session.
- Writing `Author (year)` without the source page in front of you.
- Typing the final paragraph without having run the Gate 4 table.
- A recommendation with no named objection anywhere in the deliverable.
- Starting to draft before writing the verification plan line.
- Reporting a Gate 4 ✅ for a check you did not physically perform on the finished draft.

## If available

Use each item below if it's there. If it is not, skip it and rely on the built-in standards above; nothing in the five gates depends on these.

- **Standing instructions (CLAUDE.md).** If a CLAUDE.md file defines audience tiers, subgroups and voice rules, apply them at Gate 1 and Gate 4 row 6 in place of the built-in Tier 1 default. Follow its Tier 1 working-brief, junior-MEL-learner, and Tier 2 rules exactly as written there.
- **MEL Wiki.** If `${MEL_WIKI_ROOT}/wiki/` is reachable, read it at Gate 2 before any web search. `domain-standards.md` holds the current authoritative framework versions and the citation errors to avoid; `quality-standards-application.md` holds the lens application rules. Copy citation wording from there rather than from memory.
- **Resource library.** If `${LIBRARY_ROOT}/` is reachable, read its `RESOURCES_INDEX.md` first, then the relevant subfolder, at Gate 2 before web search. Cite the library document alongside any web source.
- **Orchestration.** If the `/ann` command is available and the work needs full orchestration (a COMPLEX deliverable), route it through `/ann`, unless you are already inside an /ann run or working as one of its specialists. The five gates still apply to anything you write directly.
- **Quality gate.** If your setup has a reviewer quality gate (the qa gate inside `/ann`, or `/check-deliverable` for a single finished file), the deliverable must survive it. Run Gate 4 yourself first; the reviewer's gate does not replace Gate 4, and Gate 4 does not replace the reviewer's gate.
