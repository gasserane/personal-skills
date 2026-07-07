---
name: mel-discipline
description: Use when producing any MEL/SRHR analytical deliverable (brief, evaluation design, indicator set, ToC, evidence review, data analysis) — especially under deadline pressure, on Opus/Sonnet/Haiku-class models, or when tempted to cite a source without opening it, skip a verification pass, or deliver in one draft. Also use when a specialist subagent prompt asks for "working discipline" or "five gates".
---

# MEL Working Discipline (Five Gates)

## Overview

Rigour is a procedure, not a talent. This skill encodes the working discipline that top-tier models apply by default, so any model produces deliverables that survive Ane's qa gate. Every analytical deliverable passes five gates, in order. Skipping a gate under deadline pressure is the failure mode this skill exists to prevent: a wrong citation in front of a Director costs more than the two minutes verification takes.

**Violating the letter of a gate is violating its spirit.**

## Gate 1 — SCOPE before working

State in your first lines of work (not in the deliverable):
1. The task in one sentence, and the decision it drives.
2. Audience tier and register (default Tier 1 working brief per CLAUDE.md).
3. **Verification plan** — one line: which facts, citations, or numbers you will check, and how.
4. **Pre-mortem** — the single most likely way this deliverable misleads its named reader.

## Gate 2 — EVIDENCE before reasoning

- Provided materials, MEL Wiki, and Ane's library BEFORE web search.
- Search-effort ladder: 1 search for a single fact; 3–5 for a medium task; 5–10 for deep research or comparison. State when you stop and why.
- **Citation rule: no source enters the deliverable unless you opened it this session.** A citation you recall but did not open is either deleted or flagged `⚠️ URL unverified — confirm before publication`. Partial recognition from training is not current knowledge.
- Every kept citation: author + year + title + venue, plus a canonical link (publisher, institution, repository — never an aggregator as sole link).
- Recency: check for a superseding edition; if citing an older source deliberately, say why in the standard form.

## Gate 3 — REASON adversarially

- Name the strongest objection to your own recommendation IN the deliverable, and answer it or concede it.
- For causal or contribution claims: list the rival explanations and what the evidence says about each.
- Agreement is a finding, not a reflex: if the obvious answer survives the objection, say why.

## Gate 4 — VERIFY before declaring done

Run this checklist on the finished draft. **Perform each check physically; never report a result you did not produce.** In this skill's own wording test, a model reported "em-dash sweep: zero ✅" over a body containing five em-dashes. A claimed PASS without the performed check is itself a Gate 4 violation.

| # | Check | How |
|---|---|---|
| 1 | Every citation opened this session or flagged unverified — walked source by source through the Evidence base line, including frameworks, tools, and commissions named as design anchors; "well-known" grants no exemption | Trace each named source to the fetch/read that opened it, or attach the ⚠️ flag to that specific source. Observed failure (2026-07-07): a draft verified 1 of 4 Evidence-base sources and batch-passed the rest as canonical |
| 2 | Em-dash sweep: zero U+2014 in body prose (data-gap separator `⚠️ Data gap: [what] — [why] — [action]` exempt) | Literal character search on the draft text (Grep/search tool when available; else re-read paragraph by paragraph hunting `—`). Rewrite each hit as a comma, colon, or two sentences |
| 3 | BLUF: sentence 1 is the verdict or answer | Read sentence 1 |
| 4 | Data gaps flagged in the standard format, never papered over | Scan for asserted-but-unsourced claims |
| 5 | Numbers recomputed once from source, not carried forward on trust | Recompute and state both values |
| 6 | Tier register: length 500–2500 (Tier 1), citations off the running prose, acronyms spelled on first use, plain-English verbs | Scan |

## Gate 5 — REPORT faithfully

- State what you verified and what you could not. An unverified item reported plainly beats a confident guess.
- No hedging in the verdict; no overclaiming in the findings. "Will" for commitments, "should" for recommendations.
- If the deliverable cannot reach standard with available information, say so with a data-gap flag instead of filling the gap with generic content.

## Rationalizations — all mean STOP

| Excuse | Reality |
|---|---|
| "No time to verify, she needs it in 20 minutes" | Gate 4 takes 2 minutes. A fabricated citation in a management meeting costs the deliverable's credibility entirely. |
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

## Maintenance note

Two condensed variants of this skill exist for claude.ai surfaces (uploaded skill zip; personal-preferences block). When this file changes, regenerate both from this file — see `portables/` in this skill directory. Version parity is a `/system-audit` check item.
