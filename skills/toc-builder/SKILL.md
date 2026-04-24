---
name: toc-builder
description: Build a rigorous Theory of Change for MEL/SRHR programmes following Vogel (2012) DFID criteria and van Eerdewijk et al. (2017) KIT feminist ToC model. Use when Ane asks for a "theory of change", "ToC", "programme logic", "change pathway", "pathway analysis", or similar. Produces articulated outcomes, preconditions, assumptions (tested vs untested), contribution questions, and an evidence plan. Flags missing feminist political economy analysis.
---

# Theory of Change Builder

A ToC is not a logic model with arrows. It is an argument about how change happens, with the assumptions made visible and testable. This skill enforces that standard.

## When to use

Trigger for theory-of-change work: new programme design, ToC revision, pathway analysis, programme logic review, funder-required ToC submissions, or ToC critique.

Do not trigger for routine results frameworks, logframes, or indicator lists — those are downstream of the ToC.

## Required inputs

Ask in one batch. Do not start drafting without the first four.

1. **Long-term outcome or vision**: the change Ane wants the programme to contribute to, stated in language the target population would recognise (required)
2. **Target population and context**: who, where, what constraints shape their lives (required)
3. **Programme scope**: what interventions the programme can actually deliver (required)
4. **Timeframe**: short (12 mo), medium (3 yr), long (5-10 yr) markers (required)
5. Existing analysis: prior ToC, needs assessment, or evaluation findings (optional)
6. Feminist political economy analysis: who holds power in this system, how gender and other axes shape access (optional but required for SRHR; will prompt if missing)

## Method

Work backward from the long-term outcome. Never forward from activities.

### Step 1 — articulate the vision

Write the long-term outcome as one sentence. Must be specific enough to be falsifiable. "Improved SRHR outcomes" fails. "Adolescent girls in [region] access quality contraception within 30 minutes' travel, without third-party consent" passes.

### Step 2 — identify preconditions

What must be true for the long-term outcome to hold? List preconditions at medium-term and short-term horizons. Each precondition is itself a change state, not an activity.

### Step 3 — surface the causal links

For every link between preconditions, name:
- **Causal claim**: why does A lead to B in this context?
- **Assumption**: what must be true, outside the programme's control, for A to actually lead to B?
- **Evidence status**: *tested* (cite the source), *plausible* (cite the framework), or *untested* (flag for evidence gap)

### Step 4 — apply the feminist political economy lens

Do not skip this, even if the programme is not labelled SRHR. For each node:
- Whose interests does this change serve? Whose interests does it threaten?
- What power relations must shift for this change to stick?
- Which voices defined this outcome? Who was consulted? Who co-designed?

If these questions cannot be answered, mark the precondition with `⚠️ Feminist political economy analysis missing`.

### Step 5 — identify threats to the ToC

From Mayne (2019): what alternative explanations would account for the expected change if the programme were not running? What other contributions are likely? Name them.

### Step 6 — define the contribution question

State the evaluative question the ToC must eventually answer. Follow Mayne (2019) phrasing: "To what extent and in what ways did the programme contribute to [outcome], given other contributions and context?"

### Step 7 — plan the evidence

For each assumption, name:
- What would confirm it?
- What would disconfirm it?
- What data source could provide that evidence?
- When will the ToC be revisited in light of the evidence?

## Output structure

Produce a ToC document with these sections under these H2s:

1. **Vision** — one sentence, as described in Step 1
2. **Context and population** — two paragraphs max
3. **Pathway diagram** — text representation: each precondition as a node, each link described in one sentence. If the user needs a visual, produce Mermaid source.
4. **Preconditions by horizon** — three columns (short / medium / long), each precondition one line
5. **Causal claims and assumptions** — table: *From → To*, *Causal claim*, *Assumption*, *Evidence status*
6. **Feminist political economy analysis** — per-node power and participation notes
7. **Threats to the ToC** — rival explanations and other contributions
8. **Contribution question** — one sentence
9. **Evidence plan** — table: *Assumption*, *Confirming evidence*, *Disconfirming evidence*, *Data source*, *Revisit date*
10. **Data gaps** — `⚠️ Data gap:` entries for anything missing

## Citation requirements

Every framework claim cites author and year. Mandatory versions:
- Vogel (2012) "Review of the Use of 'Theory of Change' in International Development" (DFID)
- van Eerdewijk et al. (2017) "White Paper: A Conceptual Model of Women and Girls' Empowerment" (KIT)
- Mayne (2019) "Revisiting the Contribution Question" *Evaluation* 25(3)
- Cornwall & Rivas (2015) for feminist framing when relevant

## Writing rules

Follow CLAUDE.md house style. No hedging in causal claims — if the claim is uncertain, state that the evidence is untested. No logical leaps — if Step 3 cannot name the causal mechanism, mark the link as `⚠️ Untested mechanism`.

## Limitations

This skill does not generate indicators. Route to `indicator-designer` after the ToC is stable. It does not replace stakeholder consultation — it structures the analysis Ane brings from that consultation.
