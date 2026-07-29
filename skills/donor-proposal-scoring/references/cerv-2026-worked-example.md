# The worked example this method is built on

CERV 2026, scored blind on 29 July 2026, then compared against the donor Evaluation Summary Report. Every instruction in SKILL.md that looks arbitrary comes from something that went wrong here.

Read this when a scoring judgement feels uncertain, or before a live advisory run, to recognise the failure shapes.

## The files

Outputs, and the fullest available statement of both output shapes:

`C:\Users\AGasser\OneDrive\1. Ane's PROJECTS\AI in IPPF EN 2026\MY MEL AI SYSTEM DEMO\DEMO ARTEFACTS\test\`

- `CERV-2026-proposal-scoring.md` — the SCORE output shape
- `CERV-2026-scoring-vs-donor-comparison.md` — the CALIBRATE output shape
- `gen_cerv_scoring_docx.py`, `gen_cerv_comparison_docx.py` — the two Word builders

Source documents, usable as a test fixture:

`C:\Users\AGasser\OneDrive\1. Ane's PROJECTS\AI in IPPF EN 2026\MY MEL AI SYSTEM DEMO\CERV 2026 - Proposal evaluation demo\`

- `call-fiche_cerv-2025-og-sga_en.pdf` — the call document
- `CERV OG Final Proposal 2026.pdf` — the submitted proposal
- `101234533_CERV FPA - OG 2026_ESR.pdf` — the donor Evaluation Summary Report

A fresh run against these three files is the way to test any change to this skill.

## The numbers

| Criterion | Max | Blind score | Donor score | Direction |
|---|---|---|---|---|
| Relevance | 40 | 33 | 31 | too generous, +2 |
| Quality | 40 | 28 | 31 | too harsh, −3 |
| Impact | 20 | 13 | 16 | too harsh, −3 |
| **Total** | **100** | **74** | **78** | **4 low** |

- Published range was 70 to 78. It **contained** the true value, at its ceiling. The range was honest; the point estimate was pessimistic.
- Pass-fail conclusion: **correct**. Both scorings passed both thresholds.
- Criterion ranking: **wrong**, and this is the important failure. The blind run called Relevance strongest and Impact weakest. The donor scored Relevance and Quality equal and rated Impact proportionally strongest, 80 per cent against 65. A fix list is built on the ranking, so a wrong ranking sends effort to the wrong section.
- Counts: **7** findings contradicted, **9** substantive areas missed, **8** findings independently confirmed.

## The pattern, in one line

**The run scored the document; the donor scored the programme.**

The run findings clustered on internal consistency, arithmetic, section placement and literal compliance with the call checklists. The donor findings clustered on programmatic substance: whose rights are covered, which populations are reached, whether stated approaches are worked through, and whether the people who will run the work are named.

Both readings are defensible. Only one decides funding. This is why SKILL.md Step 2 runs the programmatic pass first and ends with a balance check on where the findings landed.

## The seven contradicted findings

Each was a real feature of the document. None was fabricated. All were mis-weighted, because they assumed an evaluator who audits compliance line by line rather than one forming a holistic judgement about a competent applicant.

| The finding | Rank given | Donor verdict |
|---|---|---|
| Sub-granting misses about seven mandatory control requirements | fix #2 | procedures "fit within all requirements of the Call" |
| Cost-effectiveness asserted not shown, the clearest points loss | fix #1 | budget "follows cost-effectiveness principles", resource-to-result relationship "good" |
| Needs evidence sits in the wrong section, will not be credited | fix #3 | credited it, "seven well-defined needs" |
| Two indicators lack baselines; indicators do not reach outcomes | fix #4 and #7 | monitoring strategy "robust", baseline "aligned with the objectives" |
| Dissemination reads as weak, 13 of 14 deliverables restricted | fix #6 | dissemination "strong, targeted and well-integrated" |
| Undocumented budget line is a financial feasibility gap | fix #8 | management and coordination costs "reasonable" |
| The timetable may be unfilled | flagged unverifiable | implicitly rejected, schedule "aligns with planned activities" |

Three lessons are encoded from this table:

1. **Search the whole document before calling anything absent.** Elements judged missing from the sub-granting section were plausibly credited from the institutional systems described elsewhere in the submission.
2. **Section-placement findings are low confidence by default.** The evaluator read across sections twice: crediting needs evidence filed under Impact, and scoring the communications narrative rather than the deliverable table.
3. **Checklist compliance and score loss are different registers.** The seven sub-granting items may still be worth fixing before signature. They were worth zero points. Hence the two-register rule in SKILL.md Step 8.

## The nine misses

| Donor finding | Criterion | Why it was missed |
|---|---|---|
| Child rights: no UN Convention citation, no age bands, absent from the monitoring framework, no child-specific outreach | all three | the instruction was read as ethics, never converted into a scoring lens |
| Intersectionality named but not worked through in access terms | Relevance | the framing was credited at face value, never tested for whether it changed the analysis |
| SRHR treated as the whole of gender equality; economic empowerment, political participation and leadership missing | Relevance | the chain was read as a strength; the donor read its narrowness as a limit |
| Needs assessment lacks disaggregated data and evidence of consultation with marginalised communities | Relevance | needs evidence judged on source quality, not on whose voices produced it |
| Interventions not tailored to specific marginalised groups, naming refugees and rural populations | Quality | not considered |
| AI risk mitigation and digital safety absent | Impact | not considered, despite the proposal making AI a work-stream |
| No contingency for key staff; no staffing plan for sub-grant management | Quality | the sub-granting controls were audited and nobody asked who runs them |
| Safeguarding enforcement across partners, as distinct from adoption | Quality | the annexed policy was credited without asking how compliance is monitored |
| Barriers to collaboration in restrictive environments; no examples of past collaboration | Relevance | filed under Impact as a past-performance point |

Four of the nine sit in the rights-holder category, which is why that pass is its own step with its own reference page. Two more are the lens-substantiveness failure. Two are the who-runs-this gap.

## The eight confirmed findings

Reached independently from the same source documents, which is what makes them worth trusting:

financial sustainability after funding ends is not answered (both filed it under Impact, and it was the sharpest thing either found) · the evaluation component lacks scope and implementation detail · stakeholder involvement in the evaluation is not set out · the theory of change and results architecture are a genuine strength · transnational collaboration and cross-border transfer are well handled · risk identification and mitigation are sound · ethics, values and safeguarding are well covered · the proposal passes both thresholds.

Convergence on the sustainability finding is the proof that the method locates real weaknesses. It is the argument for running it at all.

## What this means for how the method is sold

**Use it for:** finding fixable defects fast, building a structured criterion-by-criterion review, catching internal inconsistencies a human reader skims past, and producing a candid range rather than a false-precision number.

**Do not use it for:** predicting a score. Four points low, seven contradicted findings and a wrong criterion ranking is not a forecasting tool.

The value is the fix list, not the number. Any output that reads as a prediction has overstated itself.
