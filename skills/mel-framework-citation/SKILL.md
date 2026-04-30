---
name: mel-framework-citation
description: Enforce IPPF/UNFPA/UNAIDS evidence-and-rigour citation standard on MEL/SRHR output. Tier-aware on placement — Tier 1 working brief uses an Evidence base line at end of section; Tier 2 publication uses inline citations; Tier 1 / junior-MEL keeps framework names visible in prose AND uses an annotated Evidence base line. Use whenever Ane produces a theory of change, evaluation design, indicator set, donor report, or SRHR programme analysis. Injects current authoritative framework versions with author and year, flags outdated versions, and applies the data-gap protocol. Do not use for non-MEL work.
---

# MEL Framework Citation

Applies Ane's non-negotiable MEL/SRHR citation standard from CLAUDE.md. Generic framework references are a quality failure. This skill prevents that. Citation rigour is constant across audience tiers; placement varies by tier per CLAUDE.md "Audience tiers and register".

## When to use

Trigger whenever the output is an MEL or SRHR deliverable: theory of change, evaluation design, indicator framework, donor report, programme analysis, decolonial or feminist evaluation note, OECD-DAC review, participatory method recommendation, SRHR rights analysis.

Do not trigger for non-MEL documents, general correspondence, or requests unrelated to evaluation/SRHR.

## Required behaviour

Every MEL/SRHR claim must carry author surname, year, and specific document title. Minimum. Section or page when available. The rigour rule is tier-invariant; the placement rule is tier-specific (see below).

### Citation placement by audience tier

Read the audience tier from the prompt's Standing instructions block (passed by Ann via Vi). If the tier is not stated, default to Tier 1 / colleague.

- **Tier 1 working brief (default).** In the running text, name the analytic move, NOT the framework. Write "tested whether the programme caused the outcome by ruling out rival explanations," not "applied Mayne (2019) revisited contribution analysis." At the end of each section, append `**Evidence base:** [author (year) full title, section, hyperlink]; [next source]`. The full source list also appears in the `## Sources` section at end of document.
- **Tier 1 / junior-MEL learner subgroup.** In the running text, name the framework AND the analytic move. Write "we tested rival explanations using Mayne (2019) revisited contribution analysis, because the programme operated alongside three other interventions." Append an annotated `**Evidence base:**` line: `Mayne (2019) [framework foundation, read first]; Lemire et al. (2020) [practitioner application, worked example]`. The annotation tells the learner what each source is for.
- **Tier 2 publication.** In the running text, cite inline: `Mayne (2019) "Revisiting the Contribution Question", Evaluation 25(3)`. Use the same inline format throughout. The `## Sources` section appears at end of document.

Hyperlink rules below (canonical publisher pages, openly-accessible preferred) and recency rules apply to all tiers.

### Current authoritative versions to enforce

Use these. Flag any alternative as below current standard.

| Topic | Current standard | Supersedes | Notes |
|---|---|---|---|
| Contribution analysis | Mayne (2019) "Revisiting the Contribution Question", *Evaluation* 25(3) | Mayne (2011) | Use "contribution plausibility" vocabulary, not earlier "contribution story" alone |
| Feminist evaluation framing | Cornwall & Rivas (2015) *Third World Quarterly* 36(2) | — | Pair with Batliwala & Pittman (2010) for participatory design, Podems (2014) for positionality |
| SRHR indicators | WHO/UNFPA Sexual Health Indicators (2023 revision) | 2015 edition | Cross-reference ICPD+25 (2019), SDG 3.7, 5.6 |
| Rights-based approach | UNFPA HRBAP + UN Common Understanding HRBA (2003) | — | Pair with WHO/OHCHR sexual rights (2006/2010), UNFPA State of World Population 2021 |
| Gender-transformative | IGWG Gender Integration Continuum | — | Pair with Rao & Kelleher (2005) for institutional change |
| Theory of Change | Vogel (2012) DFID review | — | Feminist ToC: van Eerdewijk et al. (2017) KIT |
| Decolonial evaluation | Chilisa (2020) 2nd ed. | Chilisa (2012) 1st ed. | Pair with Chouinard & Cousins (2015) for practitioner application |
| Participatory methods | Davies & Dart (2005) MSC; Wilson-Grau (2018) IAP "Outcome Harvesting" — supersedes the 2012 Wilson-Grau & Britt working paper; Earl, Carden & Smutylo (2001) Outcome Mapping; Patton (2011) Developmental Evaluation | Wilson-Grau & Britt (2012) — superseded | Fals Borda (1987) for PAR epistemology |
| OECD-DAC criteria | OECD (2019) "Better Criteria for Better Evaluation" | 1991 edition (5 criteria) | Must include Coherence or flag omission |

### Mandatory disaggregation for indicators

Any indicator set must disaggregate by at minimum:
- Age cohort
- Gender identity (not sex alone)
- Disability status
- Geographic stratum

Flag any indicator missing any of these as below current standard.

## Protocol

When producing MEL/SRHR output:

1. Identify every framework, concept, or indicator invoked.
2. Match each against the table above. If current, cite with full author + year + document title + section if available.
3. If the user's draft references an outdated version, flag it in-line: `⚠️ Outdated version — current standard is [author year]`.
4. If a claim lacks a source, flag with `⚠️ Data gap: [claim] — needs source — [recommended action]`.
5. Never hedge with "according to WHO guidelines" or "feminist scholars suggest". Cite specifically.

## Lens application

Feminist, decolonial, intersectionality, and participatory lenses must change the analysis, not appear as acknowledgement sentences. When applying a lens, show what it changed.

- **Feminist**: whose voices shaped evaluation questions, power differentials named, norms questioned, bodily autonomy centred for SRHR.
- **Decolonial**: framework origin examined, Global North assumptions named, co-design vs consultation distinguished.
- **Intersectionality**: disaggregation plus interaction effects, not parallel disaggregation alone.
- **Participatory**: position on Hart (1992) ladder named, consultation vs co-design distinguished.

## Hyperlink and recency protocol

Per CLAUDE.md Citation Standards, every cited source carries a verified hyperlink to the canonical publisher page, and every source must represent the most recent authoritative evidence available at the time of writing.

### Verification protocol

Before finalising any MEL/SRHR output that includes citations:

1. **Build the citation list** during drafting (author, year, title, section, publisher).
2. **Recency check** — for every grey-literature source not in `${MEL_WIKI_ROOT}/wiki/domain-standards.md` (Atlases, EIGE Index, FRA reports, EPF/IPPF EN reports, ECHR judgments, EU strategies, UNFPA SWOP), run a WebSearch to confirm the cited edition is current. If a more recent edition exists, swap or flag.
3. **URL verification** — run WebSearch (or WebFetch) for each source to retrieve the canonical publisher URL. Batch parallel WebSearch calls for efficiency. Do not guess URLs from training data.
4. **Preference order for hyperlink target**: publisher's canonical page → direct PDF on publisher's domain → institutional repository or DOI → PubMed/PMC for biomedical articles. Aggregators (ResearchGate, academia.edu, Wikipedia) are supplementary, never sole.
5. **Flag what cannot be verified** — `⚠️ URL unverified — confirm before publication` rather than guess.
6. **State recency exceptions explicitly** — `(no superseding edition as of [date])` or `(canonical reference; subsequent literature builds on but does not supersede)`.

### Citation correction discipline

If WebSearch reveals that a citation drafted from memory is inaccurate (wrong year, wrong title, superseded edition), correct it in-line in the deliverable and note the correction transparently in the sources section or as an end-of-output verification note. Do not publish unverified citations to keep the draft tidy.

## Output

Produce the requested MEL/SRHR artefact applying the placement rule for the audience tier (see "Citation placement by audience tier" above):

- **Tier 1 working brief:** analytic moves named in prose without framework names; `**Evidence base:**` line at end of each section; full `## Sources` section at end of document.
- **Tier 1 / junior-MEL:** framework names AND analytic moves named in prose; annotated `**Evidence base:**` line at end of each section; full `## Sources` section at end of document.
- **Tier 2 publication:** inline citations throughout; full `## Sources` section at end of document.

Every `## Sources` entry lists full bibliographic form with a verified hyperlink to the canonical publisher page. Where a citation could not be verified in-session, flag it explicitly with `⚠️ URL unverified — confirm before publication`.

## Writing rules

Follow CLAUDE.md house style. For this skill specifically:
- Never write "recent research" or "best practice" without a named source.
- Never use "should" or "must" without a framework warrant.
- If a claim cannot reach publication standard with available information, flag the gap rather than fill with competency-level content.

## Limitations

This skill does not retrieve new literature. It enforces the standards list in CLAUDE.md. When a framework outside the list is invoked, ask Ane whether the reference is current, or flag for verification. Update this skill when CLAUDE.md's framework standards change.
