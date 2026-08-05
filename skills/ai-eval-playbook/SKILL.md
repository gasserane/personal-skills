---
name: ai-eval-playbook
description: >-
  Answer questions about evaluating GenAI / AI tools and products using the AI
  Evaluation Playbook (eval.playbook.org.ai; The Agency Fund with CGD and
  IDinsight, 2026) — the 4-level framework (Model / Product / User / Impact),
  Minimum Viable Evaluations, golden datasets, LLM-as-judge, engagement funnels,
  guardrail metrics, level linkages. Use when Ane asks how to evaluate an AI
  tool, chatbot or GenAI product, "how do I know this AI is working", "what
  should we measure for this AI tool", "where do I start with AI evals", or an
  MA/partner AI tool proposal needs an evaluation appraisal. NOT for programme
  or MEL evaluation design (/ann, /grill-mel, indicator-designer,
  evidence-synthesis own that lane) and NOT for AI used by evaluators as a
  working tool (wiki page ai-mel-framework governs that).
---

# AI Evaluation Playbook — live-fetch guide

This skill is a **stable index over a living document**, not the content itself. The canonical playbook lives at https://eval.playbook.org.ai/ and its maintainers publish quarterly releases. The cached summaries below are orientation only. **Fetch the live page before composing any substantive answer**, and say which parts of the reply come from the live page versus cached orientation.

Adapted 2026-08-05 from the maintainers' own skill file (github.com/IDinsight/ai-eval-playbook, `skills/`), with tool references fixed for Ane's harness, the corrected `/user-experience` path (the upstream typo path now redirects), and routing scoped to Ane's skill lanes.

## Step 0 — local first

1. Read `mel_wiki/wiki/frameworks/ai-evaluation-playbook.md` (work folder). It carries the verified citation block, the 4-level and MVE tables, the IPPF EN application, ECA calibration, and refresh state. For a quick orientation answer, that page plus this file is often enough — say so and name the rung.
2. If the AI tool touches SRHR, apply `mel_wiki/wiki/frameworks/ai-srhr-mel-framework.md` (WHO / UNESCO / EU AI Act compliance frame) alongside the playbook's evaluation design.

## How to fetch fresh content (priority order)

1. **WebFetch** the canonical URL. If context-mode redirects the call, use `ctx_fetch_and_index` and query the indexed page.
2. **`?ask=` endpoint** for narrow lookups: append `.md?ask=<URL-encoded-question>` to any page URL for a direct answer with citations. Example: `https://eval.playbook.org.ai/model-behaviour/level-1-module-evaluation/overview.md?ask=what+is+a+golden+dataset`.
3. **claude-in-chrome** as fallback for pages that block automated fetch.
4. Avoid old GitBook-ID URLs (`/spaces/<id>/pages/<id>`); use the semantic paths below.

URL notes (as of 2026-08-05): `/user-expereince` (upstream's documented typo path) now **redirects to `/user-experience`** — use the corrected spelling. Section roots (e.g. `/model-behaviour`) duplicate at `…/overview.md`. Two Level-3 sub-pages have slug/title mismatches (`descriptive-analysis` renders "Identify outcome metrics"; `user-privacy-and-security` renders the process-evaluation page) — quote the rendered H1, not the slug.

## The 4-level framework (cached orientation, 2026-08-05)

| Level | Question | Primary owners |
|---|---|---|
| L1 — Model | Does the AI system perform as intended? | AI engineers, ML researchers |
| L2 — Product | Does the product engage and retain users? | PMs, data scientists, UX researchers |
| L3 — User | Does it change thoughts, feelings, knowledge, behaviour? | Behavioural scientists, M&E specialists |
| L4 — Impact | Do development outcomes improve? | Impact evaluators, economists |

Levels are cyclical, not linear. L1 alone is not evaluation. L2 optimises **time to success**, never time on device. The wiki maps L1–L2 to output, L3 to outcome, L4 to impact (wiki's addition, not the playbook's).

Minimum Viable Evaluations (fetch [the MVE page](https://eval.playbook.org.ai/additional-resources/minimum-viable-evaluations) before quoting in a deliverable): L1 = 2–3 rubric dimensions with thresholds + 30–50 golden-dataset items + ≥1 safety metric + expert review; L2 = engagement/retention tracking + Helpful/Not-Helpful signal; L3 = 10 conversation logs/week expert-reviewed + 1 proximal outcome; L4 = counterfactual with adequate sample + version control + cost data.

## Link map (verified 2026-08-05 at site level)

- **Home / About**: https://eval.playbook.org.ai/
- **Process & authorship**: https://eval.playbook.org.ai/overview/the-process-behind-this-playbook
- **Getting started**: `/getting-started/building-blocks-for-genai-evaluation`, `/getting-started/building-the-team`, `/getting-started/building-the-infrastructure`
- **FAQ / Glossary / MVE / Tools**: `/additional-resources/frequently-asked-questions`, `/additional-resources/glossary`, `/additional-resources/minimum-viable-evaluations`, `/additional-resources/additional-resources`
- **L1 Model** (root `/model-behaviour`): 6-step loop under `/model-behaviour/how-to-evaluate/` — `1.-decide-on-an-evaluation-rubric`, `2.-decide-on-metrics`, `3.-develop-a-golden-dataset`, `4.-scoring-and-error-analysis`, `5.-automate-your-evaluations`, `6.-red-teaming`
- **L2 Product** (root `/product-analytics`): `/product-analytics/how-to-evaluate/how-is-level-2-evaluation-performed`, `methods-for-experimentation-a-b-testing-and-beyond`, `connection-with-other-levels`, `why-arent-users-engaging`
- **L3 User** (root `/user-experience`): `/user-experience/how-to-evaluate/how-is-level-3-evaluation-performed`, `descriptive-analysis` (renders "Identify outcome metrics"), `defining-guardrail-metrics-measuring-potential-harm`, `why-arent-thoughts-feelings-and-behavior-changing` (renders experimentation), `user-privacy-and-security` (renders process evaluation)
- **L4 Impact** (root `/social-impact`): `/social-impact/how-to-evaluate/how-is-level-4-evaluation-performed`, `a-quick-primer-on-impact-evaluation-methods`, `key-design-considerations-for-ai-specific-impact-evaluations`, `common-pitfalls-to-avoid`, `process-evaluation-why-arent-outcomes-changing`
- **Level linkages** (root `/level-linkages`): `risk-assessment-and-mitigation`, `data-protection`, `process-evaluations` (+ `do-i-need-a-process-evaluation`, `what-does-it-take-to-do-a-process-evaluation`)

If a fetched sub-page 404s, fetch its section root and follow the rendered navigation; then flag the dead path so this skill and the wiki page get updated.

## Answering rules

1. **Cite to Ane's standard.** The Agency Fund, with the Center for Global Development and IDinsight (2026) *AI Evaluation Playbook*, living document, canonical site + the specific page URL, **with access date**. Stable snapshot when one is needed: *Generative AI Evaluation Playbook: Policy Brief*, CGD, April 2026. Verify hyperlinks in session per CLAUDE.md Citation Standards; never from memory.
2. **Adapt to the reader.** Funders/management → evidence standards, cost-effectiveness, readiness for scale. M&E/behavioural readers → constructs, survey design, causal inference. Engineers/PMs → rubrics, metrics, CI, tooling. MA staff/implementors → MVEs and practical first steps, Tier 1 register, plain English.
3. **Be honest about trade-offs.** Evaluation is resource-intensive; help the reader decide what is *enough* for their stage (the MVE floor exists for this), rather than prescribing the maximum.
4. **Live page wins.** If the live page disagrees with this skill's cached content or with the wiki page, the live page wins; flag the discrepancy to `domain-standards.md`'s pending-verification log and note this skill needs an update — do not silently edit the wiki citation block.
5. **Route neighbouring asks away.** Programme/MEL evaluation design → `/ann`, `/grill-mel`, `indicator-designer`, `evidence-synthesis`. AI used by evaluators → wiki `ai-mel-framework`. Scoring a written proposal → `donor-proposal-scoring`. Content headed into a deliverable follows the deliverable's tier and rung, not this skill's answer-first mode.
