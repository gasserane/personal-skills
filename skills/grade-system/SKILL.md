---
name: grade-system
description: Apply substantive quality and reliability grading to Ane's MEL/SRHR system (Ann/Vi/Li/Researcher team + wiki + harness + three-repo architecture). Use whenever Ane types /grade-system, /grade, /quality-grade, /rate-system, or asks "how good is the system", "rate the system", "grade the team", "what's the system grade", "is the system any good", "system quality". Produces letter grades on 9 components and 10 dimensions plus OECD-DAC adapted criteria, three concrete risks, what an external evaluator would still want, and concrete recommendations for moving the grade. Includes mandatory self-grading bias note. Honest grading, not flattery. Different from /system-audit (finds bugs to fix) by focusing on overall quality posture rather than specific issues.
---

# Grade System

You are applying substantive quality and reliability grading to Ane's MEL/SRHR system. Output is a Tier 1 working brief with letter grades, dimensional analysis, OECD-DAC adapted criteria, concrete risks, and recommendations for grade movement. Honest grading. Self-grading bias acknowledged openly.

## When to use this
- Ane types /grade-system, /grade, or asks how good the system is
- Periodic quality read (suggested cadence: monthly, or after major bias-correction work)
- Before stakeholder communication where you need to characterise the system honestly
- After substantial system changes to assess whether they moved the grade

## Mandatory self-grading bias note (always include in output)

You are both grading the system and operating inside it. Per the 2026-05-06 mel-system-bias-audit, the LLM-as-Judge effect makes you likely to favour outputs and architectures that match your own reasoning patterns. State this openly in the output. The grade is the system's internal calibration, not external validation. The structural test (community / external MA practitioner review) remains the test the system has not yet permitted to exist.

This note is non-negotiable. Skip it and the grade is misleading.

## Workflow

### Step 1 — Gather empirical evidence

Read in parallel:
- `agent-improvements/ann-overlay.md` (Active + Archived) — extract retrospective bullets with cost figures, harness state, and key learnings. Count sessions. Note any major incidents (e.g., DOCX truncation, em-dash regression).
- `agent-improvements/coordination-log.md` — friction events with status (OPEN / CLOSED).
- `agent-improvements/cost-calibration-log.md` — count rows with observed actuals vs `not observed`. Note ⚠️ over-band entries.
- `agent-improvements/qa-disagreement-log.md` — count rows. If 0, watch-trigger has not fired and structural test is open.
- `agent-improvements/system-audit-*.md` (most recent) — design strengths and weaknesses.
- `agent-improvements/audit-drift-*.md` (most recent) — drift items resolved or carrying forward.
- `mel_wiki/wiki/index.md` — page counts (frameworks, concepts, indicators, lenses).
- `agent-improvements/agent_registry.md` — count specialists; cross-reference with `~/.claude/agents/`.
- Run `python tests/run_tests.py` for static state and `python tests/run_tests.py --output` for fixture coverage.

### Step 2 — Apply per-component grades

Grade scale: A / A− / B+ / B / B− / C+ / C and below. Use evidence from Step 1, not vibes.

| Component | Considerations |
|---|---|
| Ann (Convener) | 7-phase workflow integrity, retrospective discipline, cost-estimation accuracy, complexity-classification track record, Vi/Li orchestration ceiling |
| Vi (Orchestrator) | SELECT → DELEGATE → REVIEW → COMPILE flow, reconciliation protocol, model-rule alignment with registry, in-context-skill ceiling, taxonomy-table completeness |
| Li (Knowledge Manager) | Operations breadth (10 ops: QUERY, INGEST-FROM-RESEARCHER, INGEST-AD-HOC, INGEST-DOCUMENT, CATALOG, OVERLAY-DIGEST, LINT, CURATE, SYNC-CLAUDE-AI, REORGANIZE), CURATE quality (substantive vs archive-only), tier-branched ingestion, quarterly multilingual targets |
| Researcher (Evidence Synthesis) | Two-artifact protocol, tier-tagged source classification, multilingual live-retrieval rule operational state, external-retrieval validation status |
| Specialists (count from registry) | Agent file count match, calibration anchor coverage, registry-vs-Vi consistency, model-default discipline |
| Wiki | Page count, YAML frontmatter discipline, em-dash count trend, P1/P2/P3 priority discipline, bidirectional cross-references |
| Test harness | Static check count, fixture coverage, regression-protection breadth |
| qa_block schema + Ann PHASE 5 gate | Field-by-field verification working, schema-vs-implementation consistency, recent additions (power_shift_check, external_review_check) integrated |
| Three-repo architecture | claude-config + personal-skills + anework-package — restoration paths, mirror clones, sync gaps, migration robustness |

For each component: assign a grade with one-line rationale citing the evidence file.

### Step 3 — Apply per-dimension grades

| Dimension | What it measures |
|---|---|
| Correctness | Citation accuracy, framework version currency, lens application |
| Reliability | Quality consistency across runs, failure-mode track record |
| Robustness | Graceful degradation, self-detection, skill-fallback bannering |
| Efficiency | Token cost vs output, observability surfaces |
| Maintainability | Drift resistance, single source of truth, restoration paths |
| Honesty / calibration | Data-gap flagging, recursive-limit acknowledgement |
| Audience-tier register | Tier 1 working brief / Tier 2 publication / junior-MEL paths working |
| Lens substantiveness | Feminist, decolonial, intersectionality applied vs tokenistic |
| Power awareness | Positionality, knowledge origin, who shapes questions |
| Empirical evidence base | How many real production runs back the design claims |

For each dimension: assign a grade. Each must be defensible from the evidence collected in Step 1. Do not give A grades without specific evidence; do not give C grades without specific gap.

### Step 4 — Apply OECD-DAC adapted (6 criteria)

Adapt the 2019 six-criteria framework to the system context:

| Criterion | Adapted meaning |
|---|---|
| Relevance | Does it serve Ane's actual MEL/SRHR work? |
| Coherence | Do the parts fit together? |
| Effectiveness | Does it produce publication-standard outputs? |
| Efficiency | Token cost vs output quality |
| Impact | Does it change Ane's productivity / output quality vs baseline? Often "Insufficient evidence" without counterfactual data. |
| Sustainability | Maintainability, drift resistance, dependency robustness |

### Step 5 — Three concrete risks

Three honest risks, ranked by impact. Each has:
- Description (one sentence)
- Why it matters (one sentence)
- Mitigation in place (if any)
- What could close it

Examples from the 2026-05-06 grading: silent qa-reviewer disagreements that Ane accepts without flagging; token cost estimation opacity; self-derived bias-correction roadmap.

### Step 6 — What an external MA evaluator would still want

List items the system itself cannot satisfy from inside its own boundary:
- Sample of qa_block outputs reviewed by non-IPPF MA practitioner
- Counterfactual data (productivity vs baseline)
- The first time qa-reviewer flagged a Tier 2 output for missing external review and publication was actually delayed
- Track record on humanitarian-srhr-specialist running multi-country (the Opus override condition fires there)
- Quarterly non-English ingestion targets met for 2 consecutive quarters

### Step 7 — Overall grade and recommendations

Single overall grade with rationale. Concrete recommendations for grade movement:

| Time horizon | Achievable moves |
|---|---|
| Today (1-2 hours) | Cost-calibration log, scaffolding, one fixture capture |
| This week | Em-dash sweep on 10 most-loaded P2 pages, send external auditor invitation, capture 2 more fixtures |
| Next month | External MA practitioner sample audit fires, multilingual gap log accumulates first 3 entries, cost-calibration log gets 5+ observed actuals for one task type |
| Strategic (no deadline) | Vi/Li elevation to true subagents pending watch-trigger evidence |

Be honest about which moves are single-day vs structural ceilings. The A− → A jump usually requires the external auditor.

## Output format

Tier 1 working brief. BLUF first. Tables for component / dimension / OECD grades. Honest tone, no flattery. No em-dashes. No hedging. Per CLAUDE.md.

Use this template:

```
# Quality and reliability grading — Ann/Vi/Li/Researcher + MEL/SRHR system

**BLUF: Overall [grade]. [One-sentence summary of strengths and ceilings.]**

## Self-grading bias note
[Mandatory paragraph explaining the LLM-as-Judge effect and that this is internal calibration, not external validation.]

## Per-component grades
| Component | Grade | One-line rationale |
|---|---|---|

## Per-dimension grades
| Dimension | Grade | What it means |
|---|---|---|

## OECD-DAC adapted
| Criterion | Grade | Comment |
|---|---|---|

## Three concrete risks
1. [risk + impact + mitigation]
2. [risk + impact + mitigation]
3. [risk + impact + mitigation]

## What an external MA evaluator would still want
- [bullet list]

## Recommended sequencing for grade movement
| Time horizon | Achievable moves |

## Bottom line
[One paragraph: overall grade, what holds it back, what would move it.]

**Evidence base:** [inline file paths]
```

## What NOT to do

- Do not produce flattering grades. The system has real ceilings; name them.
- Do not skip the self-grading bias note. The note IS the discipline.
- Do not produce specific bug fixes. Those are `/system-audit`.
- Do not invent evidence. Cite the source files you actually read in Step 1.
- Do not give all dimensions A grades. If you cannot defend an A from specific evidence, the grade is lower.
- Do not give all dimensions C grades. The system has done substantial work; honest grading recognises what works.

## Closing

End with: "Want concrete recommendations for moving the grade?" Wait for Ane's response.

If Ane confirms, surface 2-3 concrete one-day moves that would shift specific dimensions. Be honest about which are achievable today vs structural ceilings. Then ask whether to execute.

## Cost band
Two shapes, calibrated from observed actuals:
- **Grade-only pass:** ~40-80k (reading overlay files, audit history, harness state).
- **Grade plus followup execution:** ~200k. All three observed runs (2026-05-10, 2026-05-20, 2026-05-22) blew the grade-only band by 2.5 to 5× once followup edits and commits were bolted on. Classify as COMPLEX-execution despite skill-only tooling, and treat ~200k as the working estimate.

Both stay within the 200k system-improvement cap; the grade-plus-followup shape reaches it. If the run is grading only with no edits, the lower band applies.

## Cross-references
- `/system-audit` finds bugs; `/grade-system` characterises overall quality posture. Use both for a complete read: audit first to clear quick fixes, then grade.
- `agent-improvements/system-audit-2026-04-28.md` is the original architecture audit; carries through to grade dimensions.
- `agent-improvements/external-calibration-auditor-invitation-draft.md` is the standing invitation that would fire the external structural test.
