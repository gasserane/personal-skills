---
name: learning-agenda
description: Produce one of three learning-agenda output types — canonical federation agenda (v1), 1-page quarterly RAG dashboard (v2), or MA adaptation template (v3). Use when Ane asks for "learning agenda", "federation learning agenda", "annual learning questions", "RAG dashboard for the agenda", "MA learning agenda template", "MA adaptation template", or names one of the three output types directly. Operationalises the IPPF EN A+C hybrid (USAID structure + Patton use-anchoring + Britton AAR posture) locked 2026-05-10. Reuses verified citations from the wiki only; never fabricates sources. Applies IPPF Visual Identity 2025 brand template.
model: opus
---

# Learning Agenda

Three output types. v1 = canonical federation agenda (the annual standing document). v2 = quarterly 1-page RAG dashboard. v3 = MA adaptation template each Member Association uses to anchor its own agenda to the federation. The skill enforces the A+C hybrid discipline locked 2026-05-10: USAID document structure plus Patton use-anchoring per question, with Britton-style after-action review posture in the annual refresh.

## When to use

Trigger on any of:

- "learning agenda", "federation learning agenda", "annual learning questions"
- "RAG dashboard" in the context of the agenda; "quarterly status of learning agenda"
- "MA learning agenda", "MA adaptation template", "MA-level learning agenda"
- "refresh the agenda", "draft the 2027 cycle agenda", "federation MEL annual refresh"
- explicit naming of an output type (`v1`, `v2`, `v3`, `canonical`, `rag-dashboard`, `ma-template`)

Do not trigger for:

- learning products derived from a Researcher Evidence Brief — that is the `learning-product` skill
- general decision memos — that is the `decision-memo` skill
- general organisational learning frameworks — that is the `evidence-synthesis` skill running against the `organisational-learning-senge-argyris` wiki page
- programme M&E plans, results frameworks, indicator sets — those are separate skills
- the Researcher Evidence Brief that answers a learning-agenda question — that is the `researcher` skill

## Required inputs

Ask in one batch. Inputs marked required must be present at invocation; inputs marked optional carry defaults.

1. **Output type** (required): one of `canonical` (v1, full federation agenda), `fragment` (single-question entry — a sub-mode of v1 producing one Tier 1 or Tier 2 question entry without full-document scaffolding; used for validation, peer-review of a candidate question, or iterative agenda construction), `rag-dashboard` (v2), `ma-template` (v3).
2. **Cycle name** (required): e.g. `2027`, `FY2027-28`, `2026-2028 biennium`. Used in the title block and refresh cadence.
3. **Federation strategic context** (required for v1; optional for v2/v3): one paragraph or pointer to a strategic-plan-refresh document naming the strategic pressures that shape the cycle.
4. **Question list** (optional for v1): if Ane provides a list of learning questions with proposed Tier 1/Tier 2 classification, the skill structures them into the agenda format. If absent, the skill drafts illustrative questions from the strategic context and flags every question with `⚠️ Reasoned default — confirm with federation MEL function`.
5. **Anchored v1 path** (required for v2 + v3): file path to the canonical agenda the v2 or v3 references. Default: `agent-improvements/learning-agenda-exemplar-v1.md` (the exemplar) for skill validation; in real use, the path to the current cycle's canonical agenda.
6. **Period** (required for v2 only): e.g. `Q2 2027`. Used in the dashboard title block.
7. **Status updates** (optional for v2): per-question RAG status + one-line note. If absent, the skill produces an illustrative status flagged as such.
8. **MA name** (required for v3): the IPPF EN Member Association name (e.g. `IPPF Romania (SECS)`, `IPPF Albania`).
9. **MA strategic context** (required for v3): one paragraph naming the MA's operating context that shapes its agenda.
10. **MA question list** (optional for v3): MA-specific questions; if absent, skill drafts from the strategic context and flags as reasoned default.
11. **Cross-MA naming convention** (optional, all output types): `name` (default per locked decision 11) or `sub-region` (the redaction-fallback). Country-level naming triggers a redaction-candidate flag in the provenance footer.

## Session start

1. Read this SKILL.md fully.
2. Read the matching exemplar at `agent-improvements/learning-agenda-exemplar-v[1|2|3].md` for the requested output type. The exemplar is the structural target.
3. Read the framework foundation at `mel_wiki/wiki/frameworks/learning-agenda-usaid-cla-2022.md` and `mel_wiki/wiki/frameworks/utilisation-focused-knowledge-management.md` once per session if not already in context.
4. Read `~/.claude/CLAUDE.md` audience-tier register section once per session if not already in context.

## Workflow

### Step 1 — parse inputs and route

Identify output type. If missing or ambiguous, ask Ane in one round:

> "Which output type? `canonical` (v1, the annual federation agenda), `rag-dashboard` (v2, the 1-page quarterly status), or `ma-template` (v3, the MA adaptation template)?"

If `ma-template` is selected without an `ma-name` parameter, ask for it in the same round.

If `fragment` is selected, additionally ask: which Tier (`1` or `2`) and what question text. If a Tier 1 fragment is requested without enough context to populate the three Patton anchors (decision-maker + commitment to use + use champion), the skill drafts reasoned defaults from the federation strategic context and flags each anchor `⚠️ Reasoned default — confirm before publication`.

### Step 2 — load source material

Read in order:

1. `agent-improvements/learning-agenda-exemplar-v[N].md` — structural target for the requested output.
2. `mel_wiki/wiki/frameworks/learning-agenda-usaid-cla-2022.md` — framework foundation; the four-element USAID template + three-anchor Patton extension definitions.
3. `mel_wiki/wiki/frameworks/utilisation-focused-knowledge-management.md` — use-anchoring operational principles.
4. For v2 and v3: the v1 path provided.
5. `agent-improvements/learning-agenda-design-brief.md` "Decisions locked" section — the 12 spec-session decisions that shape the output.

### Step 3 — apply the output-type sub-prompt

Route to one of the three sub-prompts below. Each sub-prompt instantiates the corresponding exemplar's structure against the inputs.

### Step 4 — apply quality gates (all output types)

Before returning the draft:

- **A+C hybrid discipline.** USAID document structure + Patton use-anchoring per Tier 1 question + Britton-style AAR posture in the annual-refresh section (v1 only). Mixing partial discipline produces partial output.
- **Tier 1 discipline.** Every Tier 1 question carries: question + method + decision + use plan (USAID four elements) PLUS decision-maker + commitment to use + use champion (Patton three anchors). Missing any anchor flags `⚠️ Tier 1 anchor incomplete — confirm or downgrade to Tier 2`.
- **Tier 2 discipline.** Tier 2 questions carry method + indicative use case. They do NOT require a named decision-maker, by design (decision 7).
- **Tier 1 / Tier 2 split.** ~60/40 ratio with Tier 1 dominant. v1 with all Tier 2 fails the A+C hybrid; v1 with no Tier 2 collapses to pure Patton (rejected at the spec session).
- **Voice register.** v1 uses junior-MEL register: framework names visible, callout boxes (common pitfall, why this matters, worked example), glossary footer, annotated evidence base. v2 and v3 use Tier 1 working brief default: no callouts, no glossary, compact.
- **Cross-MA naming.** Default `name` per locked decision 11 (different from `learning-product` which defaults to sub-region). Country-level naming triggers redaction-candidate flag in provenance footer.
- **Citation placement.** Inline citations only when the framework name is itself the teaching point in v1 junior-MEL register; otherwise `**Evidence base:**` at end of section. URLs reused from the wiki; not fabricated.
- **Citation rigour.** Author surname + year + venue + section where applicable. Verified URLs from the framework wiki pages only. No new sources introduced by the skill.
- **Sentence length.** Under 25 words. Active voice. No em-dashes in body prose. No nominalisations where a verb works.
- **Plain English.** Anglo-Saxon over Latinate. Acronyms spelled on first use, every document. Translatability test for ECA / SSA / MENA readers.
- **IPPF Visual Identity 2025.** When Word, PPTX, or PDF artefact is requested, route through `ane_package.reporting` brand template entry points. No hard-coded colours, fonts, or formats.

### Step 5 — provenance footer

Every output ends with a `## How this <agenda | dashboard | template> was made` block:

- One paragraph naming the source design brief (`agent-improvements/learning-agenda-design-brief.md`), the cycle name, the voice register applied, and the brand template path.
- A `**Cross-MA references named:**` line listing every MA named in the body. v1 defaults to naming MAs; v2 carries forward whatever v1 named; v3 names the MA the template is for plus federation-question-anchored MAs.
- A `**Redaction note:**` paragraph stating the names-by-default policy and the sub-region fallback. If any country-level naming surfaces an externally-sensitive case, a `**Redaction candidates:**` list flags it for Ane's manual review.
- A `**Companion artefacts in the three-exemplar series:**` line for v2/v3 cross-referencing the other two outputs as `agent-improvements/learning-agenda-exemplar-v[N].md` or the current-cycle equivalents.

### Step 6 — return

Return the draft as text in the assistant turn. v1 (long-form) may also generate a Word document via `ane_package.reporting.word_export.write_word_report` if Ane asks. v2 (1-page dashboard) may generate a PDF via `ane_package.reporting.pdf_export.write_pdf_report` if Ane asks. v3 (MA template) may generate a Word document for hand-off to MA MEL Coordinators.

---

## Sub-prompt — v1 — canonical federation learning agenda

**Default length.** 5,000–7,000 words (≈ 6–10 pages). Hard cap: 8,000 words. Below 4,000 fails the substantive density test for an annual standing document.

**Default question count.** 12 questions (Tier 1×7 + Tier 2×5). Allowed range 8–15 (USAID guidance band per decision 5). Below 8 is too sparse for federation-level scope; above 15 dilutes inquiry capacity.

**Required structure** (mirror `learning-agenda-exemplar-v1.md`):

1. **Title block** — title, audience (federation MEL function + senior management + MEL CoP + MEL leads at all active MAs + new MEL hires), cycle, length, voice (Tier 1 working brief, junior-MEL register), refresh date, quarterly RAG schedule.
2. **Executive summary** — 2-minute read. Counts of Tier 1 / Tier 2; top three changes from prior cycle; named use champion for cross-question coherence.
3. **How to read this agenda** — junior-MEL pedagogical insert. Names the six sections; explains the junior-MEL register choice; uses one `**Why this matters**` callout.
4. **Cycle context and design choices** — strategic frame; A+C hybrid rationale; one `**Common pitfall**` callout; `**Evidence base for the design**` line annotated in junior-MEL register style.
5. **The twelve learning questions** — Tier 1 first (7 questions), Tier 2 second (5 questions). Each Tier 1 question carries: Question; Method; Decision the answer informs; Use plan; Decision-maker; Commitment to use; Use champion; Tier (= 1); plus inline `**Evidence base for the question**` line. At least one Tier 1 question carries a `**Worked example — how to read a Tier 1 question**` callout (junior-MEL pedagogy). Each Tier 2 question carries: Question; Method; Indicative use case; Why Tier 2; Tier (= 2); plus inline `**Evidence base for the question**` line.
6. **Inquiry investment summary** — table: question / Tier / method / staff-days / direct cost. Total row. Tier 1 / Tier 2 split row showing the discipline (Tier 1 holds 60–80% of staff-days). One `**Common pitfall**` callout on the discipline.
7. **Review checkpoints** — Quarterly RAG (light-touch, 1-page format pointing at v2 exemplar) + Annual refresh (Britton AAR posture). At least one `**Worked example — what the AAR opening looks like**` callout (junior-MEL pedagogy).
8. **How this agenda was made** — provenance per Step 5 + redaction note.
9. **Glossary** — junior-MEL register requirement. 12–18 MEL terms used in the agenda, defined in 1–2 plain-English lines each.
10. **Annotated evidence base** — junior-MEL register requirement. Each cited source carries a one-line annotation `[framework foundation, read first]`, `[practitioner application, worked example]`, or `[advanced reading]`.

**Voice.** Tier 1 working brief, **junior-MEL register**. Framework names visible (USAID 2022, Patton & Campbell-Patton 2022, Britton 2005, Lavis et al. 2009, Weiss 1979 named in prose). Callout boxes (common pitfall, why this matters, worked example). Glossary footer. Annotated evidence base. The register supports staff who are encountering MEL framework concepts for the first time alongside experienced MEL leads using the agenda as a working reference.

**Quality bars specific to v1:**

- Every Tier 1 question carries all three Patton anchors (decision-maker + commitment to use + use champion). A Tier 1 question missing an anchor MUST be flagged `⚠️ Tier 1 anchor incomplete — confirm or downgrade to Tier 2`, not silently produced as Tier 1.
- The Tier 1 / Tier 2 ratio sits at ~60/40 (target 7/5 of 12). Drift to 9/3 or 11/1 collapses the agenda toward pure Patton; drift to 4/8 or 3/9 collapses it toward research agenda.
- Junior-MEL pedagogical inserts appear at minimum: 1 `**Why this matters**` callout, 1 `**Common pitfall**` callout, 1 `**Worked example**` callout. More allowed; fewer fails the register.
- Cross-MA naming uses MA names by default per locked decision 11. Sub-region labels are the redaction fallback only.
- The annual-refresh section explicitly names the Britton (2005) AAR posture and gives a worked example of the AAR opening.
- The glossary covers terms a new MEL hire would not know on first read; not every term but the load-bearing ones (12–18 typical).
- The annotated evidence base lists each framework source with its purpose (read first / advanced / worked example). Plain `**Evidence base:**` line without annotation fails the junior-MEL register.
- `Tier 1 / Tier 2` in the agenda refers to use-commitment tiers, not the audience-tier register from `~/.claude/CLAUDE.md`. The skill prose distinguishes the two; the glossary entry on `Tier 1 / Tier 2` makes the distinction explicit.
- **Cross-question coherence.** When two or more questions in the agenda are bidirectionally connected (one informs the other; one deepens the other), the connection is named in both question entries — typically in a `**Cross-question coherence**` line within the entry. This stops questions reading as isolated inquiries when they form an analytical sequence.

---

## Sub-prompt — fragment — single Tier 1 or Tier 2 question entry

**When to use.** Validation runs (per `agent-improvements/learning-agenda-validation-input.md`); peer-review of a candidate question before adding it to the agenda; iterative agenda construction where the user is testing one question at a time before committing to the cycle.

**Default length.** 250–500 words for a Tier 1 entry; 150–300 words for a Tier 2 entry.

**Required structure** (Tier 1 fragment):

1. **Tier and question label** — e.g. "TIER 1 — Q1 (fragment)" or "TIER 1 — single-question entry".
2. **Question** — focused, practical, feasible, generative, inclusive (USAID 2022 criteria).
3. **Method** — concretely specified.
4. **Decision the answer informs** — explicit; the federation decision the answer routes into.
5. **Use plan** — timing and packaging; how findings reach the decision-maker.
6. **Decision-maker** — named at role level (or named individual where appropriate).
7. **Commitment to use** — written commitment with threshold.
8. **Use champion** — named.
9. **Tier** — explicit (`1` or `2`).
10. **Cross-question coherence** — if the question is bidirectionally connected to another question in the agenda being built, name the connection.
11. **Evidence base for the question** — line citing the wiki sources the question draws on.
12. **Provenance footer** — minimal: one paragraph naming the design brief, the source framework wiki pages, and any reasoned-default flags. NO glossary, NO annotated evidence base, NO executive summary, NO how-to-read section.

**Required structure** (Tier 2 fragment): items 1–5 + 9 + 11 + 12, with item 5 reframed as "Indicative use case" and item 9 prefaced with "Why Tier 2" reasoning.

**Voice.** Tier 1 working brief, default register. NO junior-MEL pedagogical inserts in fragment mode (the fragment is the question entry only; pedagogy belongs in the full v1 document).

**Quality bars specific to fragment mode:**

- Every Tier 1 fragment carries ALL THREE Patton anchors. A fragment missing an anchor MUST be flagged inline as `⚠️ Tier 1 anchor incomplete — confirm or downgrade to Tier 2`. Producing a Tier 1 fragment without all three anchors is a quality failure.
- Fragment mode does NOT generate a glossary, executive summary, or annotated evidence base. These are full-document elements; fragment mode is the entry alone.
- IPPF EN context realism: pilot MAs, decision-maker roles, and budget framing match the federation context provided. The fragment is rejected if it names policy-permissive MAs as pilot sites for restrictive-policy questions, or proposes budget envelopes that mismatch federation MEL capacity.
- When the source request asks for the question to anchor to a specific Researcher Evidence Brief or other artefact, the cross-question coherence line cites the artefact explicitly.

---

## Sub-prompt — v2 — quarterly RAG dashboard

**Default length.** 1 page (≈ 600 words). Hard cap: 2 pages when branded layout requires. Below 400 words fails the substantive-density test; above 2 pages defeats the senior-management-discipline purpose.

**Required structure** (mirror `learning-agenda-exemplar-v2.md`):

1. **Title block** — agenda cycle reference, period (e.g. Q2 2027), date, audience (senior management, MEL CoP, question commitment-holders), author (PLI Senior Advisor or named role), length, voice.
2. **Headline** — 30-second BLUF: counts of green / amber / red across Tier 1 and Tier 2; the most-consequential ambers and reds; the immediate actions.
3. **RAG status — Tier 1** — single-row-per-question table: # / question (short form) / method / Q[N] status (🟢 / 🟠 / 🔴) / one-line note.
4. **RAG status — Tier 2** — same structure as Tier 1.
5. **What changed this quarter** — narrative for the colour shifts; explains every red and amber. Bullet list, not paragraphs.
6. **Tier 2 watch list — emerging questions** — promotion candidates for the next refresh.
7. **Tier 2 questions to consider dropping at refresh** — pruning candidates. May be empty (the dashboard documents that emptiness as legitimate state).
8. **Action items before next dashboard** — dated, named accountability, time-bounded follow-ups.
9. **Evidence base** — single line: USAID CLA Toolkit + agenda v1 path.

**Voice.** Tier 1 working brief, default register. NO junior-MEL pedagogical inserts. NO callouts. NO glossary. The dashboard is a working artefact for senior management; the agenda v1 carries the pedagogy.

**Quality bars specific to v2:**

- One page strict in default layout. Two pages allowed only when branded line-spacing forces it.
- Single-row-per-question table format. RAG colour visible at a glance. One-line status note enforces brevity.
- Headline before tables. BLUF discipline: counts + most consequential + actions in 3–4 sentences.
- Watch list and drop list are mandatory columns. Without them the dashboard is status reporting only, not a live decision tool for the agenda's evolution between refreshes.
- Action items carry dates and named accountability. Without these the dashboard is informational, not operational.
- 3-colour RAG (🟢 🟠 🔴) by default. Some IPPF EN convention work uses 4-colour with blue for "complete"; if Ane provides the convention, switch.
- The dashboard does NOT modify the v1 agenda. It reports against it. A question that needs to change wording or downgrade tier is flagged in the watch list / drop list, then handled at the next annual refresh.
- When status updates are not provided at invocation, the skill produces an illustrative dashboard and flags every status as `⚠️ Illustrative — confirm with question commitment-holders before circulation`.

---

## Sub-prompt — v3 — MA adaptation template

**Default length.** 1,500–2,500 words (the MA agenda is lighter weight than federation; the federation v1 carries 5,000–7,000).

**Default question count.** 4–8 MA-specific questions plus 2–4 federation-anchoring entries. Below 4 is too sparse for an MA cycle; above 8 exceeds MA-level capacity.

**Required structure** (mirror `learning-agenda-exemplar-v3.md`):

1. **Title block** — title (`MA Learning Agenda <cycle>`), MA name, MA cycle (annual), length, voice, owner (MA MEL Coordinator), anchored-to v1 path, refresh date, mid-cycle review date.
2. **MA cycle context** — paragraph naming what is happening in the MA's operating environment that shapes what the MA needs to learn this cycle. 200–400 words.
3. **Anchoring questions** — federation Tier 1 questions the MA contributes to or uses the answers from. Each entry: federation question reference + MA contribution + MA use + MA use champion. Typically 2–4 entries.
4. **MA-specific learning questions** — Tier 1 (with anchors) + Tier 2 (without). Same structure as v1 question entries. Typically 3–5 MA-specific questions.
5. **Method library and inquiry investment** — table: question / Tier / method / staff-days / direct cost. Includes federation-anchoring rows (no incremental cost beyond participation) and MA-specific rows. Total row. Federation guidance row showing 8–12% MEL function staff-time inquiry-allocation target (the MA agenda fits within this).
6. **Review cadence** — 6-monthly RAG (lighter than federation quarterly) + annual refresh + federation alignment (MA MEL Coordinator joins federation refresh as MA representative).
7. **Use commitments — quick reference** — single-table summary of MA-level decision-makers + commitments + champions across all questions. The single most-used artefact for the MA MEL Coordinator across the cycle.
8. **Evidence base** — line citing USAID + Britton + Patton + the v1 agenda path.
9. **How this template was made** — provenance per Step 5; MA-template-specific note that the MA owns its agenda; federation does not approve.

**Voice.** Tier 1 working brief, default register. NO junior-MEL pedagogical inserts. The MA already has the federation v1 as onboarding material; the MA template stays compact. MA-level register: "SECS commits", "the MA's", not "the federation requires".

**Quality bars specific to v3:**

- Anchoring section appears BEFORE MA-specific section. The order is the principle: MAs anchor first, then diverge.
- Method library is narrowed to MA capacity. The skill should propose internal qualitative tracking, focus groups, light desk reviews, HR records, peer assists. The skill should NOT propose commissioned multi-country evaluations at MA level.
- Use commitments name MA-level decision-makers (MA Programmes Director, MA CSE technical lead, MA Roma coordinator). NOT federation roles.
- 6-monthly cadence (May + November typical) not quarterly. Lighter weight; respects MA capacity.
- Use-commitment quick reference table is mandatory.
- The provenance footer carries an explicit MA-autonomy note: federation does not approve MA agendas; subsidiarity principle.
- If the MA name is not in the active IPPF EN federation list, the skill flags `⚠️ MA not recognised — confirm spelling and federation status`.

---

## Citation requirements

Every learning agenda output reuses citations verified in the wiki framework pages. Mandatory rules:

1. **Citations come from the wiki framework pages.** The skill draws from `mel_wiki/wiki/frameworks/learning-agenda-usaid-cla-2022.md` and `utilisation-focused-knowledge-management.md`. New sources are NOT introduced by the skill. A new framework that should be cited goes back to Li and the wiki, then forward to the skill.
2. **Format.** Author surname + year + venue + section where applicable. Junior-MEL register (v1) keeps framework names visible in prose. Tier 1 default register (v2 + v3) moves citations to `**Evidence base:**` line.
3. **Hyperlinks.** Reuse the wiki framework pages' verified URLs. URLs not present in the wiki carry `⚠️ URL unverified — confirm before publication`.
4. **Recency.** The wiki framework pages enforce recency. The skill flags if either framework page is older than 12 months by carrying a `⚠️ Source framework page older than 12 months — verify still current` note in the provenance footer.

## Cross-MA naming and redaction-candidate protocol

**Default for learning-agenda outputs: name MAs by default per locked decision 11.** This is different from the `learning-product` skill default (sub-region labels). The reason: the agenda is internal-strategic. Naming MAs builds federation trust because MAs see their work named, and the agenda is most legitimate when MAs see themselves in it.

When a country or named MA appears in the body:

- The provenance footer carries a `**Cross-MA references named:**` line listing every MA named.
- The provenance footer carries a `**Redaction note:**` paragraph stating the names-by-default policy for internal use, and the sub-region-label fallback for external use.
- If a specific MA is named on a sensitive risk topic (anti-gender exposure, restrictive-context staff retention, donor-relationship judgement), a `**Redaction candidates:**` list flags it for manual review before any external use.

When the user invokes with `cross-MA naming convention = sub-region`, the skill substitutes sub-region labels (Western Balkans MA, Caucasus MA, Baltic MA, Visegrád MA) and notes the substitution in the provenance footer.

## Brand application

Every artefact carries IPPF Visual Identity 2025 via `ane_package.reporting.brand.IPPF_FORMAT_TEMPLATE`. Format-specific entry points:

| Format | Used for | Module entry point |
|---|---|---|
| Word | v1 default; v3 default; v2 if requested | `ane_package.reporting.word_export.write_word_report` |
| PDF | v2 default; v1 if requested; v3 for MA hand-off | `ane_package.reporting.pdf_export.write_pdf_report` |
| Markdown | All output types in the assistant turn | (text body) |

No hard-coded colours, fonts, or formats. Every reporting call reads from `IPPF_FORMAT_TEMPLATE`. Tier 2 publication-standard exception (donor's own brand, peer-reviewed venue) requires explicit override; document the deviation in the file.

## Writing rules

Follow `~/.claude/CLAUDE.md` writing-style section verbatim. Active voice. Sentences under 25 words. No em-dashes in body prose. No filler ("in order to", "it should be noted"). No nominalisations where a verb works. No abstract openings. No rhetorical questions. State the main point first.

Anglo-Saxon over Latinate where meaning survives: use not utilise; start not commence; help not assist; check not ascertain; run not facilitate.

Acronyms spelled on first use, every document. CSE = Comprehensive Sexuality Education on first use, even when the audience already knows.

Translatability test on every sentence: would a Romanian, Tunisian, Ethiopian, or Vietnamese English-speaking reader understand on first read?

## Limitations

This skill does not:

- generate the underlying Researcher Evidence Briefs that answer the agenda's Tier 1 questions — that is the `researcher` skill, commissioned per question
- package the answers into MA-facing or donor-facing briefs — that is the `learning-product` skill, run after Researcher
- run the annual refresh workshop — that is convening work; the skill produces the artefacts the convening uses, not the convening itself
- track utilisation across cycles — utilisation-tracking is a Tier B roadmap item (`Li INGEST utilisation-tracking extension`)
- replace MA judgement on MA-specific questions — outputs are drafted in Tier 1 working brief register inviting MA editorial pass; they are not federation directives
- decide whether to publish externally — that decision goes to Ane after redaction-candidate review

## Vi specialist registration

This skill is also registered as a Vi specialist `learning-agenda-designer` at `agent-improvements/agent_registry.md`. Vi spawns the specialist when a task brief asks for a learning agenda alongside other deliverables. The specialist reads the same exemplars and frameworks and produces the same three output types via the same router.

## Edit-preservation protocol

If Ane references an existing output by path and asks to improve, iterate, or expand it, the protocol activates. Read the file first, edit scope-bounded via the Edit tool, preserve out-of-scope content byte-identical, and return the EDIT-PRESERVATION DELIVERY summary.

Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.
