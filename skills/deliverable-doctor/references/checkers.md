# Checker briefs

Each section is one agent's brief. Build the prompt as: `checker-contract.md` in full, then the section below, then the paths (run folder, `document.md`, `document.numbered.md`, `route.json`, `run.json`). Exceptions: extract-claims and the challenger do not take the contract. Their output is not findings.

---

## extract-claims → `claims.json`

Read `document.md` end to end. List every **checkable claim**: a sentence that could be true or false and that a reader might act on. Write a JSON list to `claims.json`:

```json
{"id": "cl-001", "type": "number", "role": "figure", "block": 7, "page": null,
 "quote": "exact text from document.md, five words or more",
 "cited_source": "the source the text names for it, or null",
 "data_ref": "sheet/column the figure could be recomputed from, or null"}
```

- **type** (what evidence settles it): `number` (a figure, percentage, count, trend), `source` (the text says a named source says something), `framework` (names or applies a MEL framework, standard or method), `cause` (the programme caused, contributed to, or led to a change), `equity` (a claim about who benefited or was left out, or about disaggregation), `recommendation` (a proposed action), `fact_about_context` (a date, law, name, status or event outside the document).
- **role** (what the sentence does in this genre): `outcome`, `contribution`, `figure`, `outside_fact`, `framework_ref`, `recommendation`, `method`, `award_criterion` (proposal mode only: a claim written to score against a named criterion), `motive` (the author's own stated reason or intent), `narrative` (description or characterisation in the author's voice), `reflection` (closing lesson or self-assessment), `other`.
- Tag role honestly. The genre profile exempts `motive`, `narrative` and `reflection` in a case study. Tagging an outcome claim as narrative would hide it from the checkers, and tagging a reflection as an outcome would bring back the trial's largest noise group.
- One sentence can hold two claims ("63% of the 240 participants, a rise the programme drove"): list both.
- Quote exactly, curly apostrophes included.

---

## voice → `check_voice.json` (L1, whole document)

Audit only; never rewrite the document. Apply the `ane-voice` skill's rules in audit mode: British English, the substitution table in `writing-style-guide.md` (work folder), no em-dashes in body prose, active voice, sentence length, no hedging where none exists. Category `grammar` or `style`, always with `rule`. Severity `optional` for style. Use `should` for grammar that changes meaning or blocks a reader whose first language is not English, and `must` for grammar that makes the sentence say something false.

In `others` mode, report only what the author would recognise as an error or a real barrier to reading. Do not impose Ane's house style on a partner's document: the trial rejected four style preferences (C07, C11, C12, C22). Do not report hyphenation or spelling variants that are consistent within the document.

---

## references → `check_references.json` (L1)

The main session runs the saved `citation-verification` workflow on `document.md` (it takes markdown). The main session converts each flag it returns into a finding: `category: "citation"`, `checker: "references"`, with the workflow's evidence URL and its verified passage in `verified`. This section is a conversion guide, not an agent brief. When the workflow reports a citation as fine, write no finding for it.

---

## brand → `check_brand.json` (L1, .docx only)

The main session runs `python <office-review-pass>/scripts/review_pass.py verify <source.docx> --expect-branded` and converts each failed assertion to a finding: `category: "layout"`, `checker: "brand"`, quote = the first five words of the document's first body paragraph. Severity: `should` in `own` and `proposal` mode. In `others` mode use `optional`, unless Ane says the document will be published under IPPF branding, because a partner's own document is not bound by IPPF Visual Identity 2025.

---

## number → `check_numbers.json` (L2)

For each claim in your queue:
1. Does the figure have a source in the document (a table, an annex, a named dataset) or in the supplied data file? If none: `warning`, `should`.
2. Is it internally consistent? Percentages of a base stated elsewhere; totals that add up; the same figure stated the same way throughout. An inconsistency is `error`, `must`, with every conflicting quote in `locations`.
3. Is it described correctly (a percentage-point change called a percentage change; "doubled" when the data shows +60%)? `error`, `must`.

If a data file is listed in `run.json` → `data_files`, ALSO write `recompute.json`: one spec per figure the data can settle (shapes in `ane_package/deliverable_doctor/recompute.py`). Do not compute the figures yourself. The recompute step does that after Ane approves it.

---

## source → `check_sources.json` (L2)

For each claim: does the cited source say what the text says it says? Fetch the source in this run. Record `verified` with the passage you found (contract rule 9). Findings:
- Source says something different: `error`, `must` (misattribution), only when you have the passage.
- Source cannot be found or opened: `warning`, `should`, and say so plainly.
- `fact_about_context` claims with no source in the document: check them against a canonical source (issuing body, official gazette, publisher). If you cannot confirm the fact, write a `warning` that asks the author to verify it, and name what to check.

Canonical sources first: the publisher, issuing institution or official repository. Never cite an aggregator alone.

---

## framework → `check_framework.json` (L2)

`check_framework_prepass.json` already holds every forbidden-citation hit from the harness list. **Do not repeat those.** For each claim in your queue, check it against `mel_wiki/wiki/domain-standards.md` and the relevant `mel_wiki/wiki/frameworks/*.md` page:
- Outdated edition or superseded version: `error`, `should`, naming the current version exactly as `domain-standards.md` spells it.
- Framework named but its analytic move not applied (contribution analysis named, no rival explanations tested): `warning`, `should`.
- Framework misdescribed (OECD-DAC as five criteria; gender-sensitive called gender-transformative): `error`, `must`.

---

## cause → `check_cause.json` (L2)

For each outcome or contribution claim: does the text claim attribution ("caused", "led to", "resulted in") where the evidence supports contribution at most? Does it name rival explanations and say why they do not account for the change? Apply the contribution-versus-attribution test in `mel_wiki/wiki/lenses/` and the contribution analysis page in `mel_wiki/wiki/frameworks/`.
- Attribution claimed without a design that could support it: `warning`, `should`. The suggestion rewords to contribution and names the rival explanation to address.
- Contribution claimed with no evidence of the programme's part at all: `warning`, `should`.
- Skip claims the profile exempted. In a case study the author's stated intent is not a causal claim.

---

## equity → `check_lens.json` (L2)

Apply `mel_wiki/wiki/lenses/` (feminist, decolonial, participatory, intersectionality). For each claim:
- **Parallel disaggregation presented as interaction:** results split by sex, then by disability, then a conclusion about women with disabilities. The conclusion needs the cross-tabulation, not two separate splits. `warning`, `should`.
- Group named as reached, with no figure or source: `warning`, `should`.
- A claim about a group's views with no sign the group was asked: `warning`, `should`.
- Language that is not safeguarding-aware (identifying detail about a service seeker; deficit framing): `error`, `must`.

---

## recommendation → `check_recs.json` (L2)

For each recommendation: does it name who acts, the step, and by when or under what condition? Does one concrete example follow? A recommendation with no owner or no step is a `warning`, `should`. The suggestion rewrites it with an owner, a step and an example, using only facts in the document.

---

## prior (research mode only) → `check_prior.json`

For each claim about prior work ("no study has…", "the literature shows…"): run the `literature` skill's quick search or duplication test (OpenAlex). A claim of novelty contradicted by a found paper is a `warning`, `should`, with the paper's canonical URL and `verified` filled in. Quote the paper's own words for what it found.

---

## challenger → `challenger.json`

You receive `merged.json`. For every finding with `status: "warning"`, try to reject it. Ask: **is this wrong, or only taste?**
- `wrong`: the finding misreads the text, demands evidence the genre cannot give, or rests on a rule that does not exist.
- `taste`: a preference, not an error. Another careful reviewer would leave the text as it is.
- `keep`: it survives both questions.

A grammar or style finding that does not name a real rule is `wrong`. Do not re-check facts on the web; judge the finding as written. Write a JSON object `{"<finding id>": {"verdict": "keep|taste|wrong", "note": "one sentence"}}` covering every warning, and nothing else. Ignore `error` findings. They skip this pass.

**Do not over-tune.** Every rejection can delete a true finding. When in doubt, `keep`. The trial's value came from six substantive points that a cautious challenger would have kept.
