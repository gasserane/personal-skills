# Changelog — gasserane/personal-skills

All notable changes to the Ann / Vi / Li / Researcher skill set are documented here.

## [2026-10-08] — Vendor six mattpocock skills

**Skills affected:** wayfinder, grilling, grill-me, grill-with-docs, domain-modeling, setup-matt-pocock-skills (new here)

- Copied from Ane's laptop copies, which match no single upstream commit (local wayfinder rule, local disable-model-invocation flips). Each folder carries the MIT LICENSE and an UPSTREAM.md with its base commit.
- Effect: the SessionStart installer now restores them on the laptop, on a migrated device and in web sessions.

## [2026-10-06] — mel-discipline: team portable v1.0

**Skills affected:** mel-discipline

### mel-discipline
- **New portable `portables/mel-discipline-team/SKILL.md`.** Team release v1.0 for IPPF colleagues, shipped as `mel-discipline.zip` with `RELEASE-NOTES.md` (claude.ai upload via Customize > Skills). Differs from `SKILL.md` in 7 lines: the qa-gate, CLAUDE.md-tier, and MEL Wiki / library references became generic wording, the register rule is spelled out in Gate 1 and Gate 4 check 6, and the maintenance note became a version line. The five gates are unchanged.
- **Maintenance note updated** to name the third variant and to correct the parity claim: `/system-audit` has no portables check, so the 2026-07-07 entry's "version parity is a `/system-audit` check item" was not true. Parity stays manual until a check is added.
- **Personal claude.ai zip retired** (`portables/mel-discipline-claude-ai.zip` removed). claude.ai cannot reach CLAUDE.md, the MEL Wiki or the library, so the team version is the better upload for Ane too; it is now her claude.ai copy as well as the colleagues'. Maintenance note updated to two variants.

### system-audit
- **New Step 7 axis: portables parity** via `scripts/check_portables_parity.py`. Zips under `portables/` must match `SKILL.md`; a `*-team` copy may differ only on personal-setup lines. Tested red on a seeded stale zip and a seeded gate edit, green on the repo.

## [2026-07-07] — New skill: mel-discipline (five-gate working discipline, pre-Fable-sunset extraction)

**Skills affected:** mel-discipline (new)
**System-level additions:** pre-verdict checklists in `~/.claude/agents/{mel-framework-architect,data-analysis-specialist,inferential-analysis-specialist}.md`; hyperlink verification check in `qa-reviewer.md`; dimension coverage rule in `safeguarding-reviewer.md` (claude-config repo, not this repo)

### mel-discipline
- **New skill.** Encodes the five-gate working discipline (scope → evidence → adversarial reasoning → verify before done → faithful reporting) so Opus/Sonnet-class models hold the top-tier rigour bar after the Fable model sunset (2026-07-08).
- **TDD-built.** Baseline pressure test (Sonnet, deadline pressure) produced plausible-but-unverified citations, body em-dashes, and no adversarial pass. The with-skill run fixed 4 of 5 failures. The surviving loophole (checklist theater: asserted em-dash PASS over 5 actual hits) was closed in REFACTOR with the perform-not-assert rule.
- **`portables/`** carries the claude.ai surface variants: upload zip (`mel-discipline-claude-ai.zip`), personal-preferences block, Project custom-instructions text. Regenerate all from SKILL.md on every change; version parity is a `/system-audit` check item.

## [2026-06-19] — New skill: grill-mel (MEL-aware grilling)

**Skills affected:** grill-mel (new)

### grill-mel
- **New skill.** A relentless one-question-at-a-time interview that stress-tests a MEL/SRHR design (ToC, evaluation, indicator set, results framework, proposal angle, learning question) before drafting. The MEL-aware sibling of Matt Pocock's generic `grilling` skill.
- Walks ten MEL branches (purpose-and-use, audience-and-tier, outcome altitude, tested-vs-untested assumptions, attribution-vs-contribution, OECD-DAC six-criteria coverage, indicators-and-disaggregation, substantive lens application, data-gaps-and-feasibility, evidence-and-sources).
- Recommends an answer for every question; applies Tier 1 voice (plain English, translatability, no em-dashes); probes from three perspectives on contested branches; enforces the factual-reliability rule (flag-and-ask, never invent a fact about IPPF/MAs/contacts); hands off to `/toc-builder`, `/indicator-designer`, `/evidence-synthesis`, `/proposal`, or `/ann` rather than drafting itself.

**Why:** On 2026-06-19, five Matt Pocock engineering skills were reviewed and installed. Their grilling/domain skills are code-shaped; Ane's work is ~90% non-code MEL/SRHR. `grill-mel` ports the interview discipline onto the MEL branches that decide whether a design survives scrutiny. Routing between `grill-mel`, `/ann`, `brainstorming`, and the generic `grilling` is laned in the work-folder `CLAUDE.md` § Skill routing.

---

## [2026-04-29] — Verified hyperlinks + recency check on every cited source

**Skills affected:** mel-framework-citation
**System-level additions:** `~/.claude/CLAUDE.md` Citation Standards section (user-level, not in this repo); `agent-improvements/{ann,vi,researcher}-overlay.md` STANDING PREFERENCE entries (in work-folder repo, not in this repo)

### mel-framework-citation
- **New `## Hyperlink and recency protocol` section** — six-step verification protocol covering citation list assembly, recency check against current authoritative editions, URL verification via WebSearch/WebFetch, preference order for hyperlink targets (publisher canonical → direct PDF → institutional repository → PubMed/PMC; aggregators supplementary only), explicit unverified-URL flagging, and recency-exception statements
- **New `### Citation correction discipline` subsection** — requires in-line correction when WebSearch surfaces inaccurate citations drafted from memory; forbids publishing unverified citations to keep drafts tidy
- **Updated `## Output` section** — every citation in the `## Sources` section now requires a verified hyperlink to the canonical publisher page; unverified citations must be flagged explicitly

**Why:** On 2026-04-29 paragraph-transformation work, two citation errors (UNFPA 2024 misnamed; migrant-health attribution overconfident) only surfaced because per-source WebSearch verification was run. Ane's standing instruction: from now on, verified hyperlinks + recency check apply system-wide to MEL/SRHR output, not on-request.

**Architectural note:** This rule is anchored in three layers — (1) `~/.claude/CLAUDE.md` Citation Standards as the constitutional source, (2) this skill file as immediate operational guidance, (3) `ann-overlay.md`, `vi-overlay.md`, `researcher-overlay.md` as repo-controlled patches that survive any upstream skill restore. The three-layer architecture prevents skill-restore overwrites from silently dropping the rule.

---

## [2026-04-26] — Researcher model default

**Skills affected:** researcher

### Researcher
- **Model default**: added `model: opus` to frontmatter — Researcher now always runs on Opus regardless of invocation path (Ann-spawned or direct)
- **Session Start model check**: added self-check that notifies Ane if invoked on a non-Opus model

---

## [2026-04-26] — Agent system audit improvements

**Skills affected:** ann, vi, li, researcher
**System-level additions:** `mel_wiki/wiki/domain-standards.md`, `CHANGELOG.md`

### Ann
- **Vi failure path**: added explicit halt-and-present protocol when Vi fails both return cycles in PHASE 5
- **SIMPLE task insight capture**: added lightweight wiki flag step in PHASE 6 for SIMPLE tasks that do not generate an Evidence Brief
- **Cost estimate model**: replaced vague "rough range" with defined token-range bands
- **Domain standards reference**: added link to `mel_wiki/wiki/domain-standards.md` as primary source; inline block retained as quick reference

### Vi
- **Progress signal clarification**: marked as informational; execution continues immediately without waiting for response
- **Post-escalation compile logic**: escalated subtasks are explicitly excluded from the coverage check and placed in the ESCALATION annex
- **Contradiction resolution**: added protocol for when specialists contradict on material points (flag, state precedence, mark for verification)
- **Standing instructions**: added optional block allowing Ann to pass Ane's validated preferences to Vi's specialist design
- **Domain standards reference**: added link to `mel_wiki/wiki/domain-standards.md`

### Li
- **CATALOG table schema**: defined explicit column headers (`Title | Author(s) | Year | Language | Doc_type | Key_topics | Quality | Readable`)
- **First-run setup**: added artifact-log.md creation check in INGEST-FROM-RESEARCHER Step 2
- **LINT trigger**: clarified as "on request or automatically as part of CURATE (weekly)" — removes ambiguous standalone "weekly" claim

### Researcher
- **Tool unavailability fallback**: added protocol for Consensus / PubMed / knowledge MCP failure — log and continue, do not block
- **Roster advisory language**: clarified that specialist roster in Artifact A is advisory; Vi owns final design
- **Evidence Brief length cap**: Artifact A limited to 2,500 words; prioritisation order defined
- **Intra-evidence conflict resolution**: added explicit conflict flagging protocol for contradictory Tier 1 sources
- **Domain standards reference**: added link to `mel_wiki/wiki/domain-standards.md`

### System-level
- Created `mel_wiki/wiki/domain-standards.md` — single source of truth for current authoritative framework versions; replaces four identical embedded blocks
- Created `CHANGELOG.md` — documents all skill changes for future reference
