# A synthetic worked example of the method

A fictional EU-style rights and values call ("Call X") and a fictional applicant ("Applicant X"), scored blind, then compared against the donor Evaluation Summary Report (ESR). Every name, figure and quoted donor phrase below is invented. The record has the same shape as the private calibration record and teaches the same lessons, so every instruction in SKILL.md that looks arbitrary maps to a failure shown here.

Read this when a scoring judgement feels uncertain, or before a live advisory run, to recognise the failure shapes. If the private calibration record is present (see the SKILL.md Evidence base), read that one instead: it is the real run this method is built on.

## The files

Outputs, and the fullest available statement of both output shapes. The names follow the SKILL.md Outputs pattern; for this synthetic record none of these files exists:

`<run folder>\outputs\`

- `call-x-proposal-scoring.md`: the SCORE output shape
- `call-x-scoring-vs-donor-comparison.md`: the CALIBRATE output shape
- `gen_call_x_scoring_docx.py`, `gen_call_x_comparison_docx.py`: the two Word builders

Source documents, in the shape of a test fixture:

`<run folder>\sources\`

- `call-x-call-document.pdf`: the call document
- `applicant-x-proposal.pdf`: the submitted proposal
- `call-x-ESR.pdf`: the donor Evaluation Summary Report

To test a change to this skill, run it against the three source files the private record names, when it is present, or against any call document, proposal and ESR set you hold. Then compare the result with the failure shapes below.

## The numbers

| Criterion | Max | Blind score | Donor score | Direction |
|---|---|---|---|---|
| Relevance | 30 | 25 | 22 | too generous, +3 |
| Quality | 50 | 33 | 39 | too harsh, −6 |
| Impact | 20 | 12 | 15 | too harsh, −3 |
| **Total** | **100** | **70** | **76** | **6 low** |

- Published range was 66 to 76. It **contained** the true value, at its ceiling. The range was honest; the point estimate was pessimistic.
- Pass-fail conclusion: **correct**. The call set minimums of 18, 30 and 10 points per criterion and 60 overall. Both scorings passed all four.
- Criterion ranking: **wrong**, and this is the important failure. The blind run called Relevance strongest and Impact weakest. The donor rated Quality proportionally strongest, 78 per cent against the blind run's 66, and Relevance weakest, at 73 per cent. A fix list is built on the ranking, so a wrong ranking sends effort to the wrong section.
- Counts: **6** findings contradicted, **8** substantive areas missed, **5** findings independently confirmed.

## The pattern, in one line

**The run audited the document; the donor judged the programme.**

The run findings clustered on checklist items, cost detail, section placement and what the extracted text could not show. The donor findings clustered on programmatic substance: which groups the work reaches, whether the declared approaches change what the programme does, and who delivers each mechanism.

Both readings are defensible. Only one decides funding. This is why SKILL.md Step 2 runs the programmatic pass first and ends with a balance check on where the findings landed.

## The six contradicted findings

Each was a real feature of the proposal. None was fabricated. All were mis-weighted, because they assumed an evaluator who audits compliance line by line rather than one forming a holistic judgement about a competent applicant.

| The finding | Rank given | Donor verdict |
|---|---|---|
| Partner-selection section misses five items from the call's due-diligence checklist | fix #1 | partner selection "transparent and consistent with the call conditions" |
| Staff costs look high for the activity load, the biggest expected points loss | fix #2 | staff effort "justified by the workplan", budget "proportionate to the planned activities" |
| Stakeholder map sits under Quality, not Relevance, so will not be credited | fix #3 | credited it under Relevance, "a thorough map of the actors involved" |
| Three outcome indicators lack targets; output counts stand in for outcomes | fix #4 and #8 | indicators "specific and measurable", targets "realistic for the period" |
| Outreach reads as thin, 9 of 12 events closed to the public | fix #6 | outreach "well planned and suited to each audience" |
| Budget table columns did not survive extraction, so totals went unchecked | flagged unverifiable | implicitly rejected, budget "consistent across work packages" |

Three lessons are encoded from this table:

1. **Search the whole document before calling anything absent.** The due-diligence items judged missing from the partner section were described in the applicant's governance annex, and the evaluator plausibly credited them from there.
2. **Section-placement findings are low confidence by default.** The evaluator read across sections twice: crediting the stakeholder map filed under Quality, and judging the outreach plan as a whole rather than the access setting of each event.
3. **Checklist compliance and score loss are different registers.** The five due-diligence items may still be worth fixing before signature. They were worth zero points. Hence the two-register rule in SKILL.md Step 8.

## The eight misses

| Donor finding | Criterion | Why it was missed |
|---|---|---|
| Disability: named as a target group, but no accessible formats, no accessibility budget and no disability data in the monitoring plan | all three | the target-group list was read as coverage, never tested level by level |
| Participation claimed, but the target groups decide nothing in design, monitoring or evaluation | Quality | the word "participatory" was credited at face value, never tested for what people actually decide |
| Gender-transformative claim with no activity that addresses the norms behind the problem | Relevance | the claim was read as framing, never checked against the activity list |
| Young people treated as one group; no age bands, so a 15-year-old and a 29-year-old get the same offer | Relevance | "young people" was accepted as a population without asking which ages |
| Migrants with insecure legal status: fear of data sharing, a barrier to taking part, not addressed | Quality | not considered |
| Environmental footprint of travel and events, a cross-cutting call priority, not addressed | Impact | not considered: the call's cross-cutting priorities were never turned into scoring prompts |
| European added value, a stated call priority: the cross-country exchange is one study visit with no shared output | Relevance | the call's priority list was read once at intake and never revisited |
| No named coordinator for the partner network; no plan if the lead person leaves | Quality | the coordination structure was drawn as a diagram, and nobody asked who staffs it |

Three of the eight are rights-holder gaps, which is why that pass has its own step and its own reference page. Two are lens claims that changed nothing in the design. Two are call priorities the run never looked for. One is the who-runs-this gap.

## The five confirmed findings

Reached independently from the same source documents, which is what makes them worth trusting:

the evaluation has no budget line of its own and no independent evaluator (both filed it under Quality, and it was the sharpest thing either found) · funding after the grant ends rests on a hope, not a plan · the needs analysis draws on recent national data and partner case records · safeguarding and data-protection policies are in place and annexed · the proposal passes every threshold.

Convergence on the evaluation finding is the proof that the method locates real weaknesses. It is the argument for running it at all.

## What this means for how the method is sold

**Use it for:** finding fixable defects fast, building a structured criterion-by-criterion review, catching internal inconsistencies a human reader skims past, and producing a candid range rather than a false-precision number.

**Do not use it for:** predicting a score. Six points low, six contradicted findings and a wrong criterion ranking is not a forecasting tool.

The value is the fix list, not the number. Any output that reads as a prediction has overstated itself.
