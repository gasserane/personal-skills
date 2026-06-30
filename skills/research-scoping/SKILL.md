---
name: research-scoping
description: A fast single-pass scoping map that surfaces the perspectives a MEL/SRHR question demands, where those perspectives conflict, and whether the question is worth a full orchestration — before committing tokens to one. Produces a map and a triage verdict, never citations or findings. Use when Ane says "scope this", "research scoping", "map the angles", "what perspectives does this need", "is this worth a full /ann run", "triage this before I build it", or wants a cheap first look at a question, proposal angle, learning question, or evaluation framing. Not an interview of Ane (use /grill-mel), not the deliverable or any sourced evidence (use /ann, /researcher, or /evidence-synthesis), and not a multi-agent debate (use /decision-debate).
---

# Research Scoping

A single-context triage pass that maps a question before you decide to spend real tokens on it. It runs the multi-perspective move from Stanford's STORM method compressed into one prompt: discover the perspectives the question demands, surface where they fight, sketch how a full answer would be structured, then say whether to handle it inline or escalate. It retrieves nothing and cites nothing. The output is a map and a plan, framed as questions to pursue, not answers.

The value is economic and analytical at once. A full COMPLEX /ann run costs hundreds of thousands of tokens; this pass costs a fraction of that in one context with no subagent fan-out. So it either saves you the big run, or sharpens the roster so the big run is better aimed.

## Lane — when this skill, not another

- **research-scoping** (this): map a question's perspectives and tensions in one cheap pass, then triage. No retrieval, no citations, no subagents, no deliverable.
- **/grill-mel**: interview Ane one question at a time to sharpen a design she already holds. research-scoping runs the opposite direction, handing Ane a map without interviewing her.
- **/ann**: full orchestration that produces the deliverable. research-scoping is the front door you walk through before deciding to open it.
- **/researcher, /evidence-synthesis**: retrieve and cite real sources. research-scoping never does; it hands off to these when the question needs evidence.
- **/decision-debate**: token-heavy multi-agent debate on one contested decision. research-scoping is single-context and spawns nothing.

If the question clearly warrants the deliverable, skip scoping and go straight to /ann or the right builder.

## The honest-by-construction rule

This skill must never print a citation or assert a fact about IPPF, an MA, a partner, a contact, a figure, or a date. Everything it surfaces is a hypothesis to verify, by design. A fast, un-sourced map that looks authoritative is the failure mode the whole MEL system exists to prevent, so the guardrail is structural, not stylistic:

- No `Author (year)` citations. If a framework is relevant, name the analytic move ("test rival explanations") and add it to the claims-to-verify list for the handoff. Do not cite it.
- No asserted facts. Where a fact would matter, write `⚠️ to verify: [what]` instead of a value.
- Close every output with the banner below, so the reader cannot mistake the map for findings.

## Method — one context, no fan-out

Run every step in a single pass. Light context reads (the conversation, a named project file) are fine to understand the question. Do not run a literature search or spawn specialists; that is the handoff's job, and reaching for it means you are in the wrong skill.

1. **Restate the question** in one line, so the scope is explicit and shared.
2. **Discover perspectives.** Derive the 4 to 6 angles the question genuinely demands, not a generic checklist. This is the same move Vi runs at SELECT, but standalone and up front. Name each angle plainly.
3. **Sharpest questions.** For each perspective, the one or two questions it would press hardest.
4. **Tension map.** Where these perspectives most likely disagree. This is the payload: the conflict, not a smoothed summary. One line per live tension. If you cannot find three real tensions, the question is probably SIMPLE.
5. **Shape of a full answer.** A skeleton outline of how the real deliverable would be structured if commissioned.
6. **Triage verdict.** SIMPLE (handle inline now) or COMPLEX (escalate). For COMPLEX, name a seed specialist roster and the claims that would need verifying. For SIMPLE, say what the inline answer would cover.

## Output structure

Use this template every time:

**Scoping map: [question]**

1. **Question** — one-line restatement.
2. **Perspectives** — the 4 to 6 angles, named.
3. **What each presses on** — the sharpest question per perspective.
4. **Where they conflict** — the tension map, one line per live disagreement. This is the core.
5. **Shape of a full answer** — skeleton outline.
6. **Verdict** — SIMPLE or COMPLEX, the recommended next step, and for COMPLEX a seed roster plus a `⚠️ to verify:` list.

End with:

> **Scoping map, not findings.** No claim here is sourced. Treat each line as a hypothesis to verify, not an answer. To produce the real thing, hand this map to /ann, /researcher, or /evidence-synthesis.

## Standing rules

- **Stay cheap.** One context, no subagents, no retrieval. The moment you reach for a literature search, hand off.
- **Recommend, do not survey.** The verdict carries a pick (SIMPLE or COMPLEX) and a named next step, not a menu.
- **Voice.** Plain English (Flesch-Kincaid grade 9 to 10), gloss any MEL term on first use, no em-dashes in body prose. Pass the translatability test: would a Romanian, Tunisian, Ethiopian, or Vietnamese English-speaker understand it on first read?
- **Three perspectives minimum.** The discovery move forces this. Fewer than three real angles is itself a signal the question is SIMPLE.

## Close

Deliver the map, then offer the handoff:

> "Map done. Verdict: [SIMPLE / COMPLEX]. Want me to take this to /ann, /researcher, or /evidence-synthesis, or handle it inline if SIMPLE?"

Do not start producing the deliverable from inside this skill. The map is the product; the handoff produces the answer.
