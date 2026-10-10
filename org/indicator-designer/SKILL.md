---
name: indicator-designer
description: Design MEL/SRHR indicators to IPPF/UNFPA/UNAIDS publication standard. Use when the user asks for "indicators", "KPIs", "results framework", "M&E indicators", "measurement framework", or equivalent. Enforces WHO (2010) WHO/RHR/10.12 standards plus Washington Group disaggregation, applies Tier 1/2/3 integrity markers, defines measurement mechanisms, and flags data gaps. Distinguishes output, outcome, and impact indicators precisely.
---

# Indicator Designer

Indicators that do not disaggregate to current standard are below publication quality. This skill prevents that from shipping.

## When to use

Trigger for any indicator-related request: new results framework, donor indicator set, MEL plan indicators, outcome indicators for a ToC, SDG alignment, indicator audit or adaptation.

Do not trigger for general monitoring plan design or data collection planning beyond indicator definition — those are separate workflows.

## Required inputs

Ask in one batch. First three are required.

1. **What is being measured**: the outcome, output, or impact statement the indicator must capture (required; ideally pulled from an existing ToC)
2. **Programme context**: country or region, population, programme scale (required)
3. **Measurement purpose**: accountability to donor, adaptive management, advocacy, contribution analysis (required; shapes indicator choice)
4. Existing indicators you want to retain or adapt (optional)
5. Data source constraints: what data you can and cannot collect (optional but often decisive)
6. Reporting frequency required (optional; default annual)

## Method

### Step 1 — classify the measurement level

State whether the indicator measures:
- **Output**: something the programme directly produces (services delivered, people trained)
- **Outcome**: a change in behaviour, knowledge, or condition in the target population
- **Impact**: population-level change the programme contributes to

Misclassification is a quality failure. Donor reports often conflate these. Do not.

### Step 2 — propose candidate indicators

For each outcome or output, propose 2-4 candidate indicators. Mix quantitative and qualitative where both add signal. For each:

- **Name**: noun phrase, specific
- **Definition**: one sentence, unambiguous
- **Numerator / denominator**: if rate or proportion; if count, say so
- **Data source**: survey, routine service data, secondary source, qualitative interview, observation
- **Frequency**: how often measured
- **Disaggregation**: at minimum age cohort, gender identity, disability status (Washington Group Short Set WG-SS or WG-SS-Enhanced), geographic stratum, and ethnicity where relevant. Follow WHO (2010) WHO/RHR/10.12, cross-mapped with current UN authoritative guidance. Flag any missing.
- **Tier**:
  - **Tier 1** — globally validated indicator from an authoritative source (WHO, UNFPA, SDG indicator framework). Cite source and year.
  - **Tier 2** — validated indicator adapted for this context. Note the original and the adaptation.
  - **Tier 3** — novel or bespoke indicator. Flag confidence level. Explain why a Tier 1 or 2 indicator was not sufficient.

### Step 3 — cross-reference global frameworks

For every indicator, check and cite where applicable:
- WHO (2010) *Measuring sexual health: conceptual and practical considerations and related indicators* (WHO/RHR/10.12), with the WHO (2008) reproductive health indicators as its companion
- SDG indicator framework (targets 3.7, 5.6 for SRHR)
- ICPD+25 Nairobi commitments (2019) and the ICPD+30 (2024) accountability framework
- Donor framework, if specified

WHO (2010) WHO/RHR/10.12 is the current canonical reference. If a source or the user cites a "WHO/UNFPA 2023 sexual health indicators update", use WHO (2010). Tell the user that no publication record of the update they cited was found, without repeating its title. Never name a title you cannot find. If a title does not exist, leave it out of the output, even to flag it.

Search the web for every source you cite. Link to the issuing body's own page. Check whether a newer edition exists, and state what you found: "no newer edition found as of <the date you searched>". Write that line only after you have searched. Never skip the search because it seems optional. Only if a search tool is genuinely unavailable (the search call fails or no tool exists), mark each such citation "⚠️ URL unverified" and say so once.

Cite only what an indicator rests on. List a source in the output only if an indicator is taken or adapted from it. Give author, year, full title and link. Do not list sources as background or padding.

### Step 4 — apply intersectionality substantively

Disaggregation alone is parallel, not intersectional. For each indicator, note at least one interaction effect that must be tracked (e.g., adolescent girls with disabilities, rural young women, LGBTQI+ adolescents).

If interaction-effect analysis is not feasible given data volumes, say so explicitly. Do not pretend.

### Step 5 — define the measurement mechanism

For each indicator, specify:
- Who collects the data
- What tool or instrument (cite if standard; describe if bespoke)
- Quality assurance step
- Cost or burden flag if collection is resource-intensive

### Step 6 — flag data gaps

For any indicator that cannot be measured with available data, use the format:
`⚠️ Data gap: [indicator] — [what is missing] — [recommended action: proxy, new collection, or descope]`

## Output structure

Open with the answer. The first line of the output is the recommended set and why. Any verification note comes after it.

Do not mention this skill, its rules, its tier thresholds or these instructions in the output. Write every point as a finding for the reader.

Produce an indicator table with these columns:

| # | Indicator name | Type (output/outcome/impact) | Definition | Numerator | Denominator | Data source | Frequency | Disaggregation | Tier | Framework reference | Data gap flag |

Follow the table with:
- **Intersectionality note**: which interaction effects the set tracks and which it does not
- **How each indicator is measured**: per indicator, one line on who collects it, with what tool, the quality check (who does it and how often) and how the team uses the result. Then a short table with three columns: role, task, how often.
- **Tier distribution**: count of Tier 1/2/3 indicators. If more than one in five indicators is new (Tier 3), say so as a plain finding: the set may be building measures that already exist.
- **What this set cannot tell you**: a numbered list for the reader. Cover gaps in timing, cause (no comparison group, so the set cannot show the programme caused a change), groups not tracked, subgroups too small to report, and consent or safety limits.
- **Sources**: author, year, full title and link for each source an indicator is taken or adapted from
- **AI-use line**: if the output will go to a donor or outside the organisation, end with one line. It states that AI drafted the set and that a named person must check sources and figures before use.

## Citation requirements

When you cite one of these, use this version. List it in the output only if an indicator rests on it.
- WHO (2010) *Measuring sexual health: conceptual and practical considerations and related indicators* (WHO/RHR/10.12), canonical; search for a newer edition and state the result with the date you searched
- WHO (2008) reproductive health indicators, as the companion to WHO (2010)
- SDG indicator framework (UN Statistics Division, latest)
- ICPD+25 Nairobi commitments (2019) and the ICPD+30 (2024) accountability framework
- For rights-based framing: UNFPA HRBAP + WHO/OHCHR sexual rights working definition (2006/2010)
- For gender-transformative indicators: IGWG Gender Integration Continuum

## Writing rules

Most readers are programme staff, not MEL specialists. Write for them:
- Put the answer first, then the reasons.
- Use plain English that a non-native reader understands on first read.
- Use active voice and short sentences.
- Spell out each acronym on first use.
- Give each MEL term a short plain gloss on first use, for example "outcome (a change in the people the programme serves)".
- Do not use em-dashes in running text; the data-gap line keeps its format.

Indicator names lead with the measure ("Proportion of adolescent girls who access...", "Number of ..."). Definitions never use "should" or "must"; they describe what the indicator measures, not what the programme intends.

## Revising an existing indicator set

When the user supplies an existing indicator set and asks you to improve it, change only what they asked for and leave the rest as it was. Then list any other problems you notice (for example a missing disaggregation) instead of fixing them.

## Limitations

This section describes the skill, not the indicator set. The set's own limits go in "What this set cannot tell you" above.

This skill does not design data collection instruments, sampling frames, or analysis plans. It does not assess whether indicators are feasible at scale; that needs field knowledge the user brings. It does not replace participatory indicator co-design with target populations; it prepares a rigorous draft for that consultation.

## If available

Use each item below if it's there. If it is not, skip it and rely on the built-in method above; nothing in Steps 1-6 depends on these.

- **Standing instructions (CLAUDE.md).** If a CLAUDE.md or house style guide defines voice and audience tiers, follow it in place of the default writing rules above.
- **MEL Wiki.** If `${MEL_WIKI_ROOT}/wiki/` is reachable, read `domain-standards.md` before Step 3. It holds the current authoritative framework versions and the citation errors to avoid. Copy citation wording from there rather than from memory.
- **Edit-preservation protocol.** If your setup has an edit-preservation protocol and the user references an existing output file and asks to improve, iterate, or expand it, read the file first, edit only the part in scope, keep everything else byte-identical, and return the EDIT-PRESERVATION DELIVERY summary. Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.
