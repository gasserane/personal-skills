---
name: media-to-roadmap
description: 'Turn an external tech/AI source (YouTube video, podcast, blog article, tweet or thread) into a de-duplicated improvement roadmap for the MEL system and Claude Code setup: fetch the content, extract concrete techniques, inventory what the system already does, classify each idea reuse/improve/rebuild on an Adopt/Trial/Assess/Hold ring, and write the roadmap file with a mandatory What-NOT-to-build section. Use for "analyse this video/article/talk/thread for my system", "turn this into a system-improvement plan", or a pasted URL with improvement intent. Not for MEL research video files needing the transcription+consent pipeline (video-content-analysis), mining internal QA logs (/improve-system), inspecting the system itself (/system-audit, /grade-system), academic evidence review (evidence-synthesis), or writing the LinkedIn piece (linkedin-field-note).'
model: opus
---

# /media-to-roadmap — external source in, de-duplicated roadmap out

One job: somebody published a video, podcast, article or thread about AI coding, agents or developer workflow, and Ane wants to know what in it is worth adopting. The output is one roadmap file in `agent-improvements/`, already checked against what the system does today.

## Why this exists

The pattern has run by hand at least six times: the Karpathy/Forte video became a 14-item register, the Nate Herk/Cole Medin podcast a 9-item roadmap, the loops video (2026-06-21) the monitoring-loops build plan, the STORM video (2026-06-30) the research-scoping skill, and the Thariq context-engineering article plus the Isenberg graph-engineering video (2026-08-04) a sequenced adoption plan. The pipeline is always the same; the part worth standardising is the judgement call about what NOT to implement, because the source always oversells (STORM's "90 seconds = 48 PhD hours" claim is the reference case).

## Method, in order

### 1. Fetch the source — never work from memory

Every claim in the roadmap traces to fetched content. Retrieval recipes per source type (YouTube transcript with the POT-token fallback, articles, login-gated x.com threads) are in `references/fetch-patterns.md`. Fetch through context-mode (`ctx_fetch_and_index` / `ctx_execute`) so the raw transcript stays out of the conversation. If the source cannot be fetched, stop and say so; do not reconstruct it from training data.

### 2. Extract concrete techniques

List what the source actually proposes, as specific, implementable claims — not themes. For each claim, record the source's own evidence for it and the strongest objection to it. A claim that survives its objection can be classified; one that does not goes straight to the do-NOT-adopt list with the objection as the reason.

### 3. Inventory what already exists

Before classifying anything, check what the system already does. The surfaces, in the order they answer fastest:

1. Installed skills — `~/.claude/skills/` names and descriptions.
2. Hooks — `~/.claude/settings.json`.
3. The harness — `tests/run_tests.py` check names.
4. `scripts/` and `ane_package/` in the work folder.
5. Standing rules — `~/.claude/CLAUDE.md` and the project `CLAUDE.md`.
6. Specialist agents — `agent-improvements/agent_registry.md`.

An idea the system already implements is recorded under **Already doing** as validation, never re-proposed as new work. This de-dup pass is the whole reason the skill exists; skipping it produces the duplicate-entry drift the backlog harness check was built to catch.

### 4. Classify every surviving idea

Two axes per idea, both mandatory:

- **Build route: reuse > improve > rebuild.** Prefer extending an existing hook, check, module or skill over building parallel machinery. Name the thing being reused or improved; "new" requires stating why nothing existing serves.
- **Ring: Adopt / Trial / Assess / Hold** (ThoughtWorks radar frame):
  - **Adopt** — proven fit, low risk, do it in the named block.
  - **Trial** — promising; pilot on one bounded workflow with a named success check before system-wide use.
  - **Assess** — worth understanding; a spike or a watch item, no build commitment.
  - **Hold** — do not pursue now; the reason is stated, because Hold entries are how the next scan avoids re-litigating.

### 5. Write the roadmap

Target: `agent-improvements/<slug>-YYYY-MM-DD.md`, slug from the source. Apply `mel_wiki/wiki/concepts/edit-preservation-protocol.md` when the target file exists. Required sections, in this order:

1. **Source** — what/who/where/date, fetch method used, scan date.
2. **What the source says** — the extracted claims, each with its evidence and strongest objection.
3. **Already doing** — validation list, each item naming the existing surface.
4. **Adopt / Trial / Assess / Hold** — the classified ideas, each with build route and effort guess.
5. **What NOT to build** — mandatory, with reasons. An empty section means the scan failed, not that everything is worth building.
6. **Warning signals** — what in the source, if it shows up in the system later, indicates the advice aged badly.
7. **Sequenced blocks** — Adopt/Trial items grouped into buildable sessions, spec-then-clear style.

On request, also write a continuation handoff to `agent-improvements/handoffs/` so a fresh session can build block 1 without this session's context.

## Hard rules

- **Scope advice to the model generation it targets.** A technique demonstrated on frontier-generation models does not automatically transfer to the Sonnet-tier specialist prompts; say which generation the source used and whether the transfer holds.
- **No third-party orchestration platforms without the two checks.** IPPF devices deny admin rights, and SRHR data never enters non-enterprise tools. Any idea requiring an install or an external service passes the no-admin check and the sensitive-data check before it can leave Assess.
- **Strip the hype before endorsing.** The strongest objection is named per endorsement (challenge-by-default). Repeating the source's own benchmark claims without that objection is a quality failure.
- **Numbers about the system are computed, not recalled.** A count of checks, skills or hooks stated in the roadmap is computed in the same turn or replaced by the command that produces it.

## Sits beside, does not duplicate

| Neighbour | Difference |
|---|---|
| `video-content-analysis` | MEL research video FILES (FGDs, webinars) through a transcription + consent pipeline; this skill reads published external content |
| `/system-audit`, `/grade-system` | inspect the system from inside; this ingests external input and routes findings into it |
| `/improve-system` | mines internal QA logs and session history; this is the external-signal counterpart |
| `evidence-synthesis` | formal academic REA; this is grey tech-watch content |
| `linkedin-field-note` | a scan's verdict can seed a field note, but writing the piece is that skill's job |
