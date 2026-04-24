---
name: mel-framework-citation
description: Enforce IPPF/UNFPA/UNAIDS publication-standard citations on MEL/SRHR output. Use whenever Ane produces a theory of change, evaluation design, indicator set, donor report, or SRHR programme analysis. Injects current authoritative framework versions with author and year, flags outdated versions, and applies the data-gap protocol. Do not use for non-MEL work.
---

# MEL Framework Citation

Applies Ane's non-negotiable MEL/SRHR citation standard from CLAUDE.md. Generic framework references are a quality failure. This skill prevents that.

## When to use

Trigger whenever the output is an MEL or SRHR deliverable: theory of change, evaluation design, indicator framework, donor report, programme analysis, decolonial or feminist evaluation note, OECD-DAC review, participatory method recommendation, SRHR rights analysis.

Do not trigger for non-MEL documents, general correspondence, or requests unrelated to evaluation/SRHR.

## Required behaviour

Every MEL/SRHR claim must carry author surname, year, and specific document title. Minimum. Section or page when available.

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
| Participatory methods | Davies & Dart (2005) MSC; Wilson-Grau & Britt (2012) Outcome Harvesting; Patton (2011) Developmental Evaluation | — | Fals Borda (1987) for PAR epistemology |
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

## Output

Produce the requested MEL/SRHR artefact. Inline citations throughout. At the end, append a short `## Sources` section listing every citation used, full bibliographic form.

## Writing rules

Follow CLAUDE.md house style. For this skill specifically:
- Never write "recent research" or "best practice" without a named source.
- Never use "should" or "must" without a framework warrant.
- If a claim cannot reach publication standard with available information, flag the gap rather than fill with competency-level content.

## Limitations

This skill does not retrieve new literature. It enforces the standards list in CLAUDE.md. When a framework outside the list is invoked, ask Ane whether the reference is current, or flag for verification. Update this skill when CLAUDE.md's framework standards change.
