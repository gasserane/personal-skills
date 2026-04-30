---
name: ane-voice
description: Audit and rewrite AI-generated or AI-edited prose to match Ane's IPPF MEL/SRHR voice. Tier-aware — defaults to Tier 1 working brief register (IPPF colleagues, MA staff, NGO and collaborative partners, management); Tier 2 publication only when the prompt names it. Use when the user pastes text and asks to "humanize", "de-AI", "fix the voice", "remove AI slop", "sharpen this", "tighten", "edit for tone", or "review this draft". Strips hedging, filler, nominalisations, em-dashes, passive voice, abstract openings, framework name-dropping in working briefs, and inline citations in the running text where an evidence-base line belongs. Preserves MEL/SRHR rigour. Does not push prose toward casual or blog tone.
---

# Ane Voice

A post-processing editor for prose. Audits AI-slop patterns and rewrites to the CLAUDE.md house style — tier-aware, with Tier 1 working brief as default. Inverts the default humanizer pattern where it would collapse writing toward casual voice.

## When to use

Trigger when the user:
- Pastes text and asks to "humanize", "de-AI", "fix voice", "sharpen", "tighten", "edit this"
- Asks to review a draft for AI-slop patterns
- Asks for a stylistic pass on existing prose

Do NOT trigger for:
- New-document generation → route to `decision-memo`, `internal-comms`, or `doc-coauthoring`
- Citation enforcement alone → route to `mel-framework-citation`
- Summarisation or translation

## Counter-behaviour (critical)

This skill does NOT do what most public humanizers do. Specifically, do NOT:
- Add hedging ("perhaps", "might"), burstiness, or casual rhythm
- Add em-dashes or rhetorical flourishes
- Add rhetorical questions
- Soften confident claims that are evidence-backed
- Pad for length or add transitions

If a public humanizer pattern would add any of the above, do the opposite.

## Required inputs

1. The text to edit (required)
2. Target audience tier (optional; default: Tier 1 working brief):
   - **Tier 1 working brief** (default) — IPPF colleagues, MA staff, NGO and collaborative partners, management team. ~90% of outputs.
   - **Tier 2 publication** — peer-reviewed article, externally released donor report, published guide, external policy paper. Opt-in only.
3. If Tier 1, the audience subgroup (optional, sharpens voice positioning): *colleague* / *MA-staff* / *partner-NGO* / *management* / *junior-MEL*. Default = *colleague* with collaborative voice (we propose, MAs may adapt). *management* unlocks directive voice (IPPF requires) where appropriate. *junior-MEL* (capacity-building, training, mentoring, methodology walkthroughs) flips signposting visibility — see Pass 9.
4. Permission to cut content that exists only as filler (default: yes).

## Eight-pass protocol

Run passes in order. Show the audit first, then the rewrite.

### Pass 1 — Kill nominalisations

Scan for nominalised verbs. Promote the verb, name the actor, drop the noun phrase.

| AI pattern | Rewrite |
|---|---|
| make a decision | decide |
| provide support | support |
| conduct a review | review |
| ensure the implementation of | implement |
| reach an agreement | agree |
| take into consideration | consider |
| carry out an assessment | assess |

### Pass 2 — Cut filler

Remove and verify the sentence still parses. It will usually be shorter and clearer.

| AI pattern | Rewrite |
|---|---|
| in order to | to |
| it should be noted that | delete; state directly |
| it is important to | delete |
| please be advised | delete |
| as per | under / according to |
| at this point in time | now |
| in the event that | if |
| due to the fact that | because |
| a number of | several (or the count) |
| plays a key role in | delete; state what it actually does |

### Pass 3 — Flatten passive voice

Scan for `was/were/has been/have been/will be + past participle`. If an actor exists or can be named, promote to subject.

- "It was decided by the team..." → "The team decided..."
- "Funding has been approved" → "The donor approved funding"
- "Disaggregation by age was applied" → "We disaggregated by age"

Keep passive only when agent-neutrality is genuinely correct. In MEL work there is almost always a *who*.

### Pass 4 — Split long sentences

Scan for sentences over 25 words, sentences with a semicolon, or sentences with more than one conjunction. Split. One idea per sentence.

### Pass 5 — Strip em-dashes

Replace every em-dash (—) and en-dash (–) with period, comma, or parentheses, depending on the logical relationship. Never preserve.

### Pass 6 — Audit hedging

Scan for: *perhaps, might, could be, tends to, generally, often, arguably, one could argue, it seems, it appears, somewhat, relatively*.

Decision rule:
- Claim is evidence-backed → remove the hedge, state confidently.
- Claim is genuinely uncertain → keep the hedge AND add `⚠️ Data gap: [claim] — [why confidence is limited] — [recommended source or test]`.
- Default: most hedges are AI reflex. Test them.

### Pass 7 — Replace abstract openings

Scan for paragraph openers like:
- "In today's complex landscape"
- "It is important to acknowledge"
- "In recent years"
- "As we navigate"
- "There is growing recognition"
- "Stakeholders must"

Replace with a direct claim or a concrete actor + action. The opening states the point; context follows.

### Pass 8 — Verify citations (rigour and placement)

Scan for claims invoking a framework, statistic, guideline, or evidence without author + year + specific source.

**Rigour (both tiers):**
- Claim uses Ane's standard framework list (from `mel-framework-citation`) → inject the full citation (author + year + title + section).
- Claim uses another source → flag `⚠️ Citation missing: [claim] — needs source — [suggest library or web search]`.
- Never leave "research shows", "experts agree", "studies suggest" unsourced.

**Placement (tier-specific):**
- **Tier 1 working brief (default).** Move inline framework citations to an `**Evidence base:** [hyperlinked sources]` line at end of section. In the running text, name the analytic move, not the framework. Rewrite "applied Mayne (2019) revisited contribution analysis" to "tested whether the programme caused the outcome by ruling out rival explanations." Hyperlinks must lead to openly-accessible canonical sources where possible (publisher pages, institutional repositories, PMC, open PDFs); flag paywalled-only links as `⚠️ Paywalled — find open alternative`.
- **Tier 2 publication.** Keep inline `Author (year) Title, Section`. Name the framework AND its analytic move in the prose. Aggregator links (ResearchGate, academia.edu) only as supplementary alongside a canonical link.

### Pass 9 — Tier register check

Confirm the prose matches the target audience tier.

**For Tier 1 working brief, flag and fix:**
- **BLUF violation.** Recommendation buried after method or context. Rewrite so sentence 1 = the verdict; sentence 2 = the load-bearing reason.
- **Framework name-dropping.** "Applying Mayne (2019)…" / "Using Crenshaw's intersectionality framework…" in the running prose. Strip the name; keep the substantive move. *Exception: subgroup = junior-MEL — keep the framework name AND the analytic move; the signposting is the pedagogy.*
- **Visible lens signposting.** "A feminist lens reveals…" / "From a decolonial perspective…" Strip from prose; the analysis still does the work. *Exception: subgroup = junior-MEL — keep visible signposting.*
- **MEL jargon without first-use gloss.** *Outcome harvesting, contribution claim, theory of change pathway, attribution gap, MEAL.* Add 6-word gloss in parentheses on first use, or replace with plain verb.
- **Latinate over Anglo-Saxon verbs where meaning survives.** *Utilise → use; commence → start; ascertain → check; facilitate → run / lead; assist → help; endeavour → try; subsequently → then; in order to → to.*
- **Idioms and culturally-specific metaphors.** *Low-hanging fruit, moving the needle, hit the ground running, on the same page, drill down, deep dive, unpack, baked in, surface (as verb when it means show), align stakeholders.* Replace with plain verb.
- **Phrasal verbs where a single verb works.** *Set up → establish; bring up → raise; come up with → propose; find out → learn / check; figure out → work out / decide.*
- **Directive voice in MA/partner-facing content.** "IPPF requires," "must," "shall," "is required to" when the audience is an MA or partner organisation, not a compliance officer. Rewrite to collaborative: "we propose," "we recommend," "MAs may adapt X to their context," "evidence suggests X works in [context]." Reserve directive voice for management briefings, donor deadlines, and reporting compliance content where compliance is the actual subject.
- **Buried procedural content.** Steps an MA or partner has to *implement* (adapt an indicator, run a workshop, complete a template) buried in a paragraph. Promote to numbered steps with imperative verbs.
- **Recommendation without a worked example.** Flag for example addition: "Add a 2-sentence concrete example showing how this applies in [setting]."
- **Length above 2500 words without an executive summary** OR length above 1500 words without a 5-bullet executive summary on page 1. Flag for restructure.
- **Acronyms unspelled on first use.** Even *M&E*, *SRHR*, *CSE*, *AYFS*, *MISP*, *ToC*, *AYP* — spell out on first use, every document.

**For Tier 1 subgroup = junior-MEL, additionally flag and fix:**
- **Conclusion stated without the analytic move.** "We ruled out rival explanations" — restore the *why*: "We chose contribution analysis because the programme operated alongside three other interventions; single-cause attribution would not survive scrutiny."
- **Framework name absent from running text.** Restore both the framework name and the analytic move (Tier 2-style inline). The end-of-section `**Evidence base:**` line is still required.
- **Evidence base unannotated.** Add navigation annotations: `Mayne (2019) [framework foundation, read first]; Lemire et al. (2020) [practitioner application]`.
- **Missing pedagogical scaffolding where the topic invites it.** Flag for one optional callout per major section: *Common pitfall*, *Why this matters*, *Worked example*, *Read more*. Do not auto-insert; surface as a suggestion in the audit so Ane can opt in.
- **4+ MEL terms with no glossary footer.** Suggest a "Terms used in this document" footer with 1-line definitions.

**For Tier 2 publication, flag and fix:**
- Plain-English over-simplification of technical claims. The publication audience expects technical register.
- Citations not inline. Move from `**Evidence base:**` line back into the running text.
- Lens application without visible signposting. Restore the audit trail.
- Framework moves named without the framework name. Restore both.

If the input does not specify a tier and the content is unmistakably Tier 2 (academic register, peer-review framing, journal-article structure), default to Tier 2 and note the assumption at the top of the audit. If the input is unmistakably training or capacity-building content (workshop module, "how we did this" walkthrough, MEL onboarding note), default to Tier 1 / junior-MEL and note the assumption. Otherwise default to Tier 1 / colleague.

## Pattern catalog — AI-slop to flag

Distilled from public humanizer research (matsuikentaro1, Aboudjem, jpeggdev, blader, conorbronsdon, apoapostolov), filtered against CLAUDE.md rules. Keep only patterns that agree with Ane's style; drop those that would push toward casual voice.

### Lexical tells
- **Empty superlatives**: *crucial, critical, vital, essential* — replace with the specific consequence
- **Corporate abstractions**: *synergy, leverage, landscape, ecosystem, journey* — replace with a specific noun
- **Hype words**: *game-changing, transformative, paradigm-shifting* — delete or ground in cited evidence
- **Filler adjectives**: *robust, comprehensive, holistic, innovative* — keep only when a concrete property is named
- **Weasel phrases**: *it is increasingly recognised that, there is growing consensus* — needs citation or delete

### Structural tells
- Tricolons (three-item lists) pasted in for rhythm rather than content
- Parallel structures padded beyond what the meaning needs
- Headers phrased as questions
- Bullet lists of complete sentences that could be prose
- Nested bullets beyond one level

### Tonal tells
- "I hope this helps" and other performative softeners
- "Feel free to" and similar permission grants
- "Let me" statements explaining what is about to happen
- Meta-commentary ("This document will explore...") instead of doing

### MEL-specific AI tells
- Generic framework mentions without author and year ("using contribution analysis" without Mayne 2019)
- Indicator lists without disaggregation specified
- Gender references that do not say what the lens actually changed in the analysis
- Donor-report language that conflates output, outcome, and impact
- "Evidence-based" or "rights-based" used as labels without the specific evidence or rights framework named

## Output format

Open with a one-line **Tier declaration**:
`Tier: [1 working brief / 2 publication] — Audience: [colleague / MA-staff / partner-NGO / management / peer-review]`

Then return in two parts:

### Audit
A numbered list of issues found, grouped by pass. Each entry:
- **Location**: the sentence or phrase in quotes
- **Pattern**: name of the AI-slop or tier-mismatch pattern
- **Fix**: what the rewrite will do

### Rewrite
The full rewritten text. Use **bold** inline for phrases substantially changed, so Ane can scan the diff. Do not add commentary inside the rewrite itself.

Follow the two sections with a one-line **Length delta**:
`Original N words → Rewrite M words (−X%)`

Shorter is usually better. If the rewrite is longer than the original, explain why in one clause.

If any pass surfaced genuine uncertainty or missing citations, add a final **Data and citation gaps** section with `⚠️` entries.

## Writing rules applied during rewrite

Every sentence you produce must:
- Lead with the actor or the action
- Use a specific verb, not a nominalisation
- Fit under 25 words
- Name who does what by when, if the content is actionable
- Carry a source if the claim is evidential

## Limitations

- Does not fetch new sources. Flags gaps; Ane or `evidence-synthesis` closes them.
- Does not translate between languages.
- If the input is under 50 words, ask whether a full 8-pass audit is worth the overhead; a targeted pass often suffices.
- If text already matches house style, say so and return it unchanged. Do not fabricate issues to justify running all eight passes.
- Does not alter technical terminology that is correct in context even when it sounds AI-adjacent (e.g., "contribution analysis" is correct; replace only when the usage is wrong).
