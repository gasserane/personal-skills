---
name: indicator-designer
description: Design MEL/SRHR indicators to IPPF/UNFPA/UNAIDS publication standard. Use when Ane asks for "indicators", "KPIs", "results framework", "M&E indicators", "measurement framework", or equivalent. Enforces WHO/UNFPA (2023) disaggregation, applies Tier 1/2/3 integrity markers, defines measurement mechanisms, and flags data gaps. Distinguishes output, outcome, and impact indicators precisely.
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
4. Existing indicators Ane wants to retain or adapt (optional)
5. Data source constraints: what data Ane can and cannot collect (optional but often decisive)
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
- **Disaggregation**: at minimum age cohort, gender identity, disability status, geographic stratum (WHO/UNFPA 2023). Flag any missing.
- **Tier**:
  - **Tier 1** — globally validated indicator from an authoritative source (WHO, UNFPA, SDG indicator framework). Cite source and year.
  - **Tier 2** — validated indicator adapted for this context. Note the original and the adaptation.
  - **Tier 3** — novel or bespoke indicator. Flag confidence level. Explain why a Tier 1 or 2 indicator was not sufficient.

### Step 3 — cross-reference global frameworks

For every indicator, check and cite where applicable:
- WHO/UNFPA Sexual Health Indicators (2023)
- SDG indicator framework (targets 3.7, 5.6 for SRHR)
- ICPD+25 commitments (2019)
- Donor framework, if specified

If a candidate indicator predates the 2023 WHO/UNFPA revision, flag it. Propose the current equivalent.

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

Produce an indicator table with these columns:

| # | Indicator name | Type (output/outcome/impact) | Definition | Numerator | Denominator | Data source | Frequency | Disaggregation | Tier | Framework reference | Data gap flag |

Follow the table with:
- **Intersectionality note**: which interaction effects the set tracks and which it does not
- **Measurement mechanism summary**: one paragraph on who does what
- **Tier distribution**: count of Tier 1/2/3 indicators. Flag if Tier 3 exceeds 20% of the set — Ane may be reinventing standards unnecessarily.
- **Sources**: full citations for every framework referenced

## Citation requirements

Mandatory versions:
- WHO/UNFPA Sexual Health Indicators (2023 revision)
- SDG indicator framework (UN Statistics Division, latest)
- ICPD+25 Nairobi Summit commitments (2019)
- For rights-based framing: UNFPA HRBAP + WHO/OHCHR sexual rights working definition (2006/2010)
- For gender-transformative indicators: IGWG Gender Integration Continuum

## Writing rules

Follow CLAUDE.md house style. Indicator names lead with verbs where possible ("Proportion of adolescent girls who access..."). Definitions never use "should" or "must" — they describe what the indicator measures, not what the programme intends.

## Limitations

This skill does not design data collection instruments, sampling frames, or analysis plans. It does not assess whether indicators are feasible at scale — that requires field knowledge Ane brings. It does not replace participatory indicator co-design with target populations; it prepares a rigorous draft for that consultation.
