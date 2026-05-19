---
name: learning-product
description: Convert a Researcher Evidence Brief into one of four learning-product output types — MA-facing 2-page brief, workshop / CoP pack, regional learning brief, or donor / management talking-points memo. Use when Ane asks for "learning product", "learning brief", "MA brief from this Evidence Brief", "workshop pack", "CoP pack", "regional learning brief", "donor memo from research", "management memo from research", or names one of the four output types directly. Reads from a single Researcher Evidence Brief slug under `literature-reviews/<slug>/`. Reuses the brief's verified sources only; never fabricates citations. Applies IPPF Visual Identity 2025 brand template and Tier 1 working brief register.
model: opus
---

# Learning Product

One Researcher Evidence Brief → one of four learning-product output types. The skill carries the brief's evidence into the format the audience can use, without weakening the rigour and without adding sources the brief did not verify.

## When to use

Trigger on any of:

- "learning product", "learning brief", "MA brief from this Evidence Brief", "MA-facing brief"
- "workshop pack", "CoP pack", "facilitator pack", "build me a workshop from this brief"
- "regional learning brief", "federation brief", "regional synthesis"
- "donor memo from this brief", "management memo", "talking-points memo", "decision memo for donor"
- explicit naming of an output type (`v1`, `v2`, `v3`, `v4`, `ma-brief`, `workshop-cop-pack`, `regional-learning-brief`, `donor-management-memo`)

Do not trigger for:

- producing the underlying Evidence Brief — that is the `researcher` skill
- general decision memos not derived from a Researcher Evidence Brief — that is the `decision-memo` skill
- evaluation design or indicator design — those are separate skills
- ToC building — `toc-builder`

## Required inputs

Ask in one batch. First two are required.

1. **Evidence Brief slug** (required): the directory name under `literature-reviews/`, e.g. `2026-05-10_cse-anti-gender-opposition-eca`. The skill reads `literature-reviews/<slug>/evidence-brief.md`.
2. **Output type** (required): one of `ma-brief` (v1), `workshop-cop-pack` (v2), `regional-learning-brief` (v3), `donor-management-memo` (v4).
3. **Recipient** (required for v4 only): one of `donor-programme-officer`, `donor-senior`, `ippf-en-management`, `ippf-central-management`, `mp-or-policy`. Used to calibrate voice register and the decision-asked framing.
4. **Audience focus** (optional): MA cluster, sub-region, country list. Defaults derive from the Evidence Brief's geography metadata.
5. **Length override** (optional): word count or page count beyond default. Defaults defined per output type below.
6. **Workshop format** (optional, v2 only): `single-90min` (default), `two-session-split`, `half-day`, `full-day`. Affects slide count and segment timing.
7. **Workshop modality** (optional, v2 only): `in-person` (default), `hybrid`, `virtual`. Affects facilitator notes and microstructure adaptations.
8. **Country snapshot count** (optional, v3 only): default 4; allowed range 3–5.
9. **Country naming convention** (optional, v3 only): `sub-region-label` (default — Western Balkans MA, Caucasus MA, Baltic MA, Visegrád MA) or `country-name` (triggers redaction-candidate flagging).
10. **Decision asked** (optional, v4 only): the specific decision the recipient must make. If absent, the skill drafts a placeholder and flags it for replacement before publication.

## Session start

1. Read this SKILL.md fully.
2. Read the Evidence Brief at `literature-reviews/<slug>/evidence-brief.md`.
3. Read the matching exemplar at `agent-improvements/learning-product-exemplar-v[1|2|3|4].md` for the requested output type. The exemplar is the structural target.
4. Read `~/.claude/CLAUDE.md` audience-tier register section once per session if not already in context.

## Workflow

### Step 1 — parse inputs and route

Identify output type. If missing or ambiguous, ask Ane in one round:

> "Which output type? `ma-brief` (2-page MA brief), `workshop-cop-pack` (workshop + CoP pack), `regional-learning-brief` (5–8 page federation brief), or `donor-management-memo` (1-page memo)?"

If `donor-management-memo` is selected without a `recipient` parameter, ask for it in the same round.

### Step 2 — load source material

Read in order:

1. `literature-reviews/<slug>/evidence-brief.md` — the source content
2. `literature-reviews/<slug>/sources.md` if present — verified hyperlink list
3. `literature-reviews/<slug>/literature-review.md` if present — fuller synthesis for v3 depth
4. `agent-improvements/learning-product-exemplar-v[N].md` — structural target

The Evidence Brief frontmatter carries the `region`, `period`, and `confidence` metadata the output's title block uses.

### Step 3 — apply the output-type sub-prompt

Route to one of the four sub-prompts below. Each sub-prompt instantiates the corresponding exemplar's structure against the Evidence Brief's content.

### Step 4 — apply quality gates (all output types)

Before returning the draft:

- **BLUF discipline.** Sentence 1 = the verdict. Sentence 2 = the load-bearing reason. v1 headline ≤ 3 lines bold; v3 executive summary 5 bullets exact; v4 bottom line 1 paragraph bolding the decision-ask.
- **Voice register.** Tier 1 working brief by default. v4 unlocks directive register only at the decision-asked section. v2 facilitator notes use directive verbs for procedural steps.
- **Citation placement.** Tier 1 working brief: framework names off the running text; `**Evidence base:**` line at end of section. v2 source slide uses "For further details you can consult:" lead phrase per `feedback_source_slide_framing.md`.
- **Citation rigour.** Author surname + year + venue + section where applicable. Lifted verbatim from the Evidence Brief. Never invent.
- **Hyperlink policy.** Reuse only URLs that appear in the Evidence Brief or its `sources.md`. Never fabricate. Any URL not present in the source carries `⚠️ URL unverified — confirm before publication`.
- **Session-time URL audit step.** Before returning the draft, verify each cited URL against the IPPF/UNFPA hyperlink standard:
  - Aggregator wrappers (`consensus.app`, ResearchGate, academia.edu, Wikipedia) MUST be replaced with the canonical publisher URL or DOI before publication. Aggregators are tolerated only as supplementary alongside canonical, never as sole source.
  - DOI links that resolve to a paywall MUST be supplemented with an open-access alternative (PMC, institutional repository, publisher-hosted open PDF, author manuscript) where one exists.
  - Publisher-migrated URLs (Rowman to Bloomsbury, journal venue changes, etc.) MUST be updated to the current canonical URL.
  - URLs returning 404 MUST be replaced with the canonical permanent link (typically UNESDOC, DOI, or institutional repository).
  - When the canonical source has no open-access alternative and the audience is non-academic, the citation MUST flag "paywalled, no open-access alternative found" so MA staff and partner readers know in advance.

  The audit applies WebFetch and WebSearch at session time. Lift the audit cost across the four output types (v1/v2/v3/v4) by running once per Evidence Brief, caching the URL substitutions, and reusing them across all output types generated from the same source brief.
- **Sentence length.** Under 25 words. Active voice. No em-dashes in body prose. No nominalisations where a verb works.
- **Plain English.** Anglo-Saxon over Latinate. Acronyms spelled on first use. Translatability test for ECA / SSA / MENA readers.
- **Disaggregation default.** When the Evidence Brief carries WG-SS, age, gender identity, geography breakdown, the output preserves the disaggregation rather than collapsing.
- **Cross-MA naming.** Default sub-region labels (Western Balkans MA, Caucasus MA, Baltic MA, Visegrád MA) unless the Evidence Brief or Ane explicitly names a country. Country-level naming triggers a redaction-candidate flag.
- **IPPF Visual Identity 2025.** Word, PPTX, and PDF outputs go through `ane_package.reporting` brand template entry points. No hard-coded colours, fonts, or formats.

### Step 5 — provenance footer

Every output ends with a `## How this <product> was made` block:

- One paragraph naming the source Evidence Brief (slug + date), the voice register applied, and the brand template path.
- A `**Cross-MA references named:**` line listing every MA cluster or country named in the body.
- A `**Redaction candidates:**` list of any specific MA, country, or named individual a federation reader may want to remove before external use. If the body uses sub-region labels only, the list reads "none at sub-region level".
- A `**Companion artefacts in the four-exemplar series:**` line for v2/v3/v4 cross-referencing the other three outputs as `agent-improvements/learning-product-exemplar-v[N].md`.

### Step 6 — return

Return the draft as text in the assistant turn. If the output is workshop-pack (v2), additionally generate the artefact files via `ane_package.reporting`:

- Slide deck → `pptx_export.write_pptx_deck`
- Handout one-pager → `word_export.write_word_report` → exported to PDF via `pdf_export.write_pdf_report`
- Worksheet → simple Word file via `word_export.write_word_report`

For v1, v3, v4: return as markdown body in the assistant turn. Ane converts to Word/PDF/PPT via the existing reporting modules at her discretion. v3 is long enough to also produce a Word document via `word_export.write_word_report` if Ane asks.

---

## Sub-prompt — v1 — MA-facing 2-page brief

**Default length.** 1,200 words (≈ 2 pages). Hard cap: 1,500. Below 1,000 fails the brief's substantive density test.

**Required structure** (mirror `learning-product-exemplar-v1.md`):

1. **Title block** — title, audience, length, date, voice, evidence (Tier 1/2 mix from the brief).
2. **Headline** — 3-line BLUF, bold the verdict in line 2.
3. **Why this brief** — frames the issue. 3–5 sentences. Names the geography from the Evidence Brief.
4. **What we know** — 3–5 numbered findings. Each finding is one paragraph. Findings come from the Evidence Brief's RQ1 / Findings section verbatim or compressed.
5. **Evidence base line** — at end of "What we know". Hyperlinked. Pulls from the brief's source list.
6. **Four levers your MA can use** — 3–4 levers. Each lever has: action (1 sentence), Why it works (1 paragraph), One-MA example (1 short paragraph; sub-region labels by default), Resource estimate (1 line). Skip a sub-field only if the Evidence Brief does not provide content.
7. **What to do next quarter** — single concrete action. Force one-lever commitment.
8. **Adaptation prompts for your context** — 4 questions. Questions invite MA judgement, not Secretariat directive.
9. **Questions to bring to your next regional peer exchange** — 4 questions seeding the CoP convening.
10. **How this brief was made** — provenance + redaction candidates list per Step 5.

**Voice.** Tier 1 working brief, collaborative. "We propose," "your MA can," "evidence suggests," "MAs may adapt to context." Reserve directive voice for compliance-subject content only — none in v1.

**Quality bars specific to v1:**

- Adaptation prompts MUST be questions, not statements.
- Each lever MUST carry a Why-it-works paragraph; missing this drops the brief below USAID Learning Brief implementer-audience standard.
- The "What to do next quarter" section MUST force one-lever commitment, not multi-lever menu.
- When the source Evidence Brief carries finding-level confidence markers (HIGH / MODERATE / LOW / MIXED), preserve them inline next to each finding in the "What we know" section. Federation readers need the differential confidence to interpret the lever choices; collapsing to a single rating obscures it.

---

## Sub-prompt — v2 — workshop / CoP pack

**Default settings.** Single 90-minute session; 8–15 participants; in-person modality; full pack (slides + facilitator notes + handout + worksheet + pre-read + post-event prompts).

**Required structure** (mirror `learning-product-exemplar-v2.md`):

1. **Pack metadata block** — workshop title, scope, audience, length, modality, date, voice, source brief, CoP cultivation framing.
2. **Pre-event materials** — pre-read (the v1 brief if it exists, otherwise the Evidence Brief's executive summary); pre-event diagnostic (4 questions); facilitator briefing (1 page).
3. **Slide deck — 14 slides at default settings**, structured: cover (1) → BLUF and diagnostic-feedback (2–3) → findings (4–7) → group-work segment using 1-2-4-All or equivalent Liberating Structures microstructure (8) → levers (9–12) → pair work with worksheet (13) → plenary commitments (14) → sources (15). Plus or minus 1 slide allowed; never below 12 or above 17. Each slide carries: content, facilitator note (time + what to do + what to draw out + watch-for cue), and hybrid/virtual adaptation when relevant.
4. **Handout one-pager** — Side A: 4 findings as a 4-row table; Side B: 4 levers as a 4-row table plus closing question.
5. **Worksheet** — single page: Lever picked, Why this lever for your context, First 30 days week-by-week, What you need from the federation, What will tell you it worked.
6. **Post-event materials** — 48-hour email (commitments table + questions list + CoP-cultivation framing); week-6 peer-exchange prompt (2 questions); facilitator AAR (4 questions, facilitator only).
7. **Hybrid and virtual adaptations** — inline notes per microstructure.
8. **Materials checklist** — for in-person session.
9. **How this pack was made** — provenance + redaction candidates per Step 5.

**Voice.** Tier 1 working brief collaborative throughout slide content. Facilitator notes use directive verbs for procedural steps ("Read the BLUF aloud. Pause. Ask...") — this is procedural, not register-shifted.

**Quality bars specific to v2:**

- The 1-2-4-All microstructure (Lipmanowicz & McCandless 2013) or equivalent Liberating Structures method MUST appear at the small-group segment. No "discuss in pairs" without structure.
- Every slide MUST carry a per-slide facilitator note. Skip the "watch for" cue only when there is genuinely nothing to watch for (rare).
- Post-event materials are part of the pack, not optional. Without them the pack is a workshop, not a CoP-cultivation pack.
- The slide-15 source slide uses "For further details you can consult:" not bare "Source:"; body font ≥20pt for projection.
- CoP cultivation framing is explicit: the workshop is the first convening of a building CoP; commitments and worksheets are first practice artefacts.
- When the source Evidence Brief carries more than 4 findings, drop the LOW-confidence and LOW–MODERATE-confidence findings from the slide deck (slides 4–7); keep them in the handout's evidence base and in the source slide. The slide deck holds 4 finding slides; the handout absorbs overflow.
- If `ane_package.reporting.pptx_export` is unavailable in the current session (skill running outside the work folder, or `ane_package` not installed), fall back to a markdown deck specification — slide-by-slide content + facilitator notes — and instruct Ane to run the PPTX generation in the work folder. PPTX is preferred but not blocking.
- An optional `cop-state` parameter (`building` default / `established`) controls the CoP framing. `building` uses "first convening of a building CoP"; `established` uses "[N]th convening of the [name] CoP" with N and name passed at invocation.

**Brand application.** Slide deck via `pptx_export.write_pptx_deck`; handout via `word_export.write_word_report` → PDF; worksheet via `word_export.write_word_report`. Power BI / Tableau exports not applicable.

---

## Sub-prompt — v3 — regional learning brief

**Default length.** 3,000–5,000 words (≈ 5–8 pages); default target 6 pages (~3,200 words).

**Default country snapshot count.** 4; range 3–5.

**Default naming convention.** Sub-region labels.

**Required structure** (mirror `learning-product-exemplar-v3.md`):

1. **Title block** — title, audience (federation-wide MELers, senior leadership, donor programme officers, policy researchers), length, date, voice, source brief.
2. **How to read this brief** — default v3 section between Title block and Executive summary. Two parts:
   - A **note on language** sub-paragraph naming the acronyms used in the brief and pointing readers to the glossary near the end.
   - A **note on confidence levels** sub-paragraph defining each confidence label that appears in the brief, plus a single sentence on the basis for the rating. The basis is the source Researcher Evidence Brief, which applies standard evidence-synthesis discipline. Rating depends on study type, number of independent sources, consistency across studies, and directness to the question. The approach is similar to GRADE in health research, adapted to mixed evidence bases typical of CSE / SRHR evaluation.

   Default content for the confidence-labels list (preserve verbatim across v3 outputs; substitute domain topic where bracketed):

   - **We are confident in this finding.** Multiple peer-reviewed studies, working independently, point to the same answer. The evidence converges.
   - **We are fairly confident in this finding.** The finding fits how we already know [domain topic] works. Specific evaluation in our region (or for this exact approach) is limited. Practitioner experience indicates the effect. Published comparative data is not yet at the level a donor or external reader would expect.
   - **Less confident — emerging evidence.** Theoretical or mechanism-based reason exists to think the approach works. Operational evaluation has not yet tested it directly. Treat as promising rather than proven.
   - **Mixed confidence — varies by approach.** The findings inside this bullet sit at different levels. The body of the brief preserves the differences.
3. **Executive summary** — 5 bullets exact. Bullets carry the regional pattern, not just findings restated.
4. **Why this brief** — 2–3 paragraphs. Includes the CoP-cultivation framing (the brief is itself a CoP practice artefact).
5. **The regional landscape** — 3 sub-headers naming the structural shifts that frame the analysis (e.g., for ECA: opposition convergence; EU candidate-status pressure; improved adolescent SRHR data). Each shift cites Evidence Brief sources verbatim.
6. **Four findings with cross-MA evidence** — pulled from the Evidence Brief RQ1 findings; each finding adds a "Cross-MA evidence" sentence naming the sub-region pattern. Closes with `**Evidence base:**` line.
7. **Country snapshots — N MA contexts** — fixed sub-structure per snapshot: Context (1 paragraph) → Lever applied (1 line) → What worked (2–3 bullets) → What did not work (1–2 bullets) → Lesson (1 sentence). Skip a row only when the Evidence Brief does not cover it.
8. **Cross-cutting strategy — what the snapshots share** — the brief's analytical contribution. Names the pattern across snapshots (e.g., lever-fit follows existing relational capital). One paragraph plus a short list. This is the section where the regional brief earns its keep relative to v1.
9. **Adaptation prompts by MA pattern** — 3 patterns, each leading to a different lever recommendation. Each pattern uses a diagnostic question. Closes with a fallback path for MAs that fit none of the three patterns.
10. **What this means for the federation** — 3 actions maximum. The only place where federation infrastructure is named.
11. **Sources** — full Evidence base from the brief's source list.
12. **How this brief was made** — provenance + redaction candidates + companion artefacts per Step 5.

**Voice.** Tier 1 working brief, federation-wide collaborative. The regional brief addresses MELers and senior leadership across the federation; voice acknowledges the federation's MA-led architecture rather than asserting Secretariat authority.

**Quality bars specific to v3:**

- Executive summary is always exactly 5 bullets. Federation-wide leadership audience reads only the bullets.
- Country snapshots use the fixed sub-structure. Variance in snapshot length is a quality failure.
- The cross-cutting strategy section MUST surface a pattern across snapshots, not restate the findings.
- Adaptation prompts MUST be diagnostic questions, not directives.
- Three federation actions maximum. Four dilutes attention.
- Sub-region labels by default; any country-level naming requires explicit redaction-candidate flag.
- When the source Evidence Brief carries finding-level confidence markers, preserve them inline next to each finding in "Four findings with cross-MA evidence". Same requirement as v1.
- When the source Evidence Brief carries 3+ data gap entries, add a "What we don't know" section drawing from the brief's data gap inventory as the eleventh structural element (between "What this means for the federation" and "Sources"). Federation-wide audience should see evidence limitations alongside findings; hiding them transfers the gap-discovery work to the donor or external reader.
- Preserve the source brief's exact regional label form. If the brief uses "Visegrád / Central Europe", do not collapse to "Visegrád MA" without preserving the alternative label at first use.

---

## Sub-prompt — v4 — donor / management talking-points memo

**Default length.** 900 words (≈ 1 page). Hard cap 1,500. Beyond 1,500: split into two memos or escalate to v3 (regional learning brief) instead.

**Required structure** (mirror `learning-product-exemplar-v4.md`):

1. **Title block** — title, audience (named recipient role), length, date, voice, source, decision asked stated at top.
2. **Bottom line** — 1 paragraph. Bolds the decision-ask. Decision-grade summary; reader can stop after 30 seconds.
3. **Three talking points** — exactly three. Each talking point is 1–2 paragraphs and translatable to oral briefing. Talking points pull from the Evidence Brief's RQ1 / RQ2 / RQ3 findings.
4. **Anticipated questions** — 3–5 Q&A pairs. Pre-answers the questions the recipient is most likely to ask.
5. **Decision asked** — numbered, specific. Each item is a discrete decision the recipient is asked to make. No vague asks.
6. **Sources** — short list. Uses "For further details you can consult:" lead phrase. Pulls from Evidence Brief sources.
7. **How this memo was made** — provenance + recipient-placeholder flag if needed + companion artefacts per Step 5.

**Voice.** Tier 1 working brief through talking points. Directive register unlocks at the decision-asked section per `~/.claude/CLAUDE.md` audience-tier register: "We request," "We seek approval for," "We ask the [recipient] to authorise."

**Quality bars specific to v4:**

- Bottom line is exactly one paragraph; bolds the decision-ask. No room for two BLUFs.
- Three talking points exact. Four dilutes; two looks insubstantial.
- Anticipated questions section is mandatory unless Ane explicitly overrides.
- Decision asked is numbered and specific. Vague asks ("we'd appreciate consideration") are quality failures.
- Voice unlocks directive register only at decision-asked. Talking points stay collaborative. Mixing produces incoherent register.
- Recipient parameter is required at invocation; without it the voice cannot be calibrated.
- When the source Evidence Brief is MIXED or LOW on any finding, the Anticipated questions section MUST address evidence limitations explicitly. Donor due-diligence will surface limitations regardless; pre-answering them is a credibility move.

**Recipient calibration:**

| Recipient | Voice nuance | Decision-ask framing |
|---|---|---|
| `donor-programme-officer` | Operational; programme-mechanics fluency assumed | "Continued funding at current level"; "approval of incremental additions"; specifies budget envelope |
| `donor-senior` | Strategic; pattern-level argument | "Endorsement of the framework"; "indication of multi-year intent" |
| `ippf-en-management` | Federation-respecting; MA-priority counter-balance visible | "Secretariat capacity"; "convening role"; "infrastructure" |
| `ippf-central-management` | Federation-wide pattern; Vision 2030 / Strategic Framework alignment visible | "Cross-region applicability"; "model for adaptation"; "federation learning architecture" |
| `mp-or-policy` | Public-policy register; rights-frame visible | "Rights-respecting policy"; "evidence-informed legislative posture" |

---

## Citation requirements

Every learning product reuses the Evidence Brief's verified citations. Mandatory rules:

1. **Citations come from the Evidence Brief or its `sources.md`. Period.** The skill never adds new citations not in the source. If a stronger source exists than what the brief used, the gap goes back to Researcher, not into a learning product.
2. **Format.** Author surname + year + venue + section where applicable. Tier 1 working brief moves citations to `**Evidence base:**` line at end of section.
3. **Hyperlinks.** Reuse the Evidence Brief's verified URLs. URLs not present in the source carry `⚠️ URL unverified — confirm before publication`.
4. **Recency.** The Evidence Brief enforces recency at production time; the learning product inherits it. If the Evidence Brief is older than 12 months, the skill flags this in the provenance footer with `⚠️ Source brief is older than 12 months — confirm currency before external use`.
5. **Conflicting sources.** Where the Evidence Brief flagged `⚠️ CONFLICT:` between Tier 1 sources, carry the flag forward into the learning product. Do not paper over.
6. **Data gaps.** Where the Evidence Brief flagged `⚠️ Data gap:`, the learning product preserves the gap inline using the same format. Do not omit.

## Cross-MA naming and redaction-candidate protocol

Default federation-trust posture: name MA work at sub-region cluster level (Western Balkans MA, Caucasus MA, Baltic MA, Visegrád MA) unless the Evidence Brief or Ane explicitly names a country.

When a country or named individual appears in the body:

- Add a `**Redaction candidates:**` list at the end of the provenance footer.
- Each redaction candidate names what is at risk if it is published externally without check (specific MA exposure on sensitive content; named individual; named pilot site).
- The list is for Ane's manual review before any external use.

When the body uses sub-region labels only, the list reads `**Redaction candidates:** none at sub-region level`.

## Brand application

Every artefact carries IPPF Visual Identity 2025 via `ane_package.reporting.brand.IPPF_FORMAT_TEMPLATE`. Format-specific entry points:

| Format | Used for | Module entry point |
|---|---|---|
| Word | v3 default; v4 when recipient is management; v1 if requested | `ane_package.reporting.word_export.write_word_report` |
| PowerPoint | v2 slide deck | `ane_package.reporting.pptx_export.write_pptx_deck` |
| PDF | v2 handout; v4 when recipient is donor; v3 if requested | `ane_package.reporting.pdf_export.write_pdf_report` |
| Markdown | All output types in the assistant turn | (text body) |

No hard-coded colours, fonts, or formats. Every reporting call reads from `IPPF_FORMAT_TEMPLATE`. Tier 2 publication-standard exception (donor's own brand, peer-reviewed venue) requires explicit override; document the deviation in the file.

## Writing rules

Follow `~/.claude/CLAUDE.md` writing-style section verbatim. Active voice. Sentences under 25 words. No em-dashes in body prose. No filler ("in order to", "it should be noted"). No nominalisations where a verb works. No abstract openings. No rhetorical questions. State the main point first.

Anglo-Saxon over Latinate where meaning survives: use not utilise; start not commence; help not assist; check not ascertain; run not facilitate (except where facilitate names a workshop role).

Acronyms spelled on first use, every document. CSE = Comprehensive Sexuality Education on first use, even when the audience already knows.

Translatability test on every sentence: would a Romanian, Tunisian, Ethiopian, or Vietnamese English-speaking reader understand on first read? Cut idioms.

## Limitations

This skill does not:

- produce the underlying Evidence Brief — that is the `researcher` skill
- verify hyperlinks at session time — that is Researcher's job at brief production time. The skill reuses verified URLs only.
- generate diagrams, infographics, or video — separate workflows
- fabricate cross-MA cases, named individuals, or specific pilot sites not in the Evidence Brief
- decide whether to publish the output externally — that decision goes to Ane after redaction-candidate review
- replace MA-led adaptation. Outputs are drafted in Tier 1 working brief register inviting MA judgement; they are not federation directives.

## Vi specialist registration

This skill is also registered as a Vi specialist `learning-product-designer` at `agent-improvements/agent_registry.md`. Vi spawns the specialist when a task brief asks for a learning product alongside other deliverables. The specialist reads the same Evidence Brief slug and produces the same four output types via the same router.

## Edit-preservation protocol

If Ane references an existing output by path and asks to improve, iterate, or expand it, the protocol activates. Read the file first, edit scope-bounded via the Edit tool, preserve out-of-scope content byte-identical, and return the EDIT-PRESERVATION DELIVERY summary.

Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.
