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
- **role** (what the sentence does in this genre): `outcome`, `contribution`, `figure`, `outside_fact`, `framework_ref`, `recommendation`, `method`, `award_criterion` (proposal mode only: a claim written to score against a named criterion), `general_claim` (a statement about how the world works, true or false whoever says it: "prevention costs less than response"; "adolescents trust peers more than teachers"), `own_record` (the author organisation's own observation, monitoring record, internal consultation, seat or role, or its own assessment of a situation, with no outside body and no outside count named: "our outreach team noticed more questions about consent this spring"; "we sit on the district health committee"), `motive` (the author's own stated reason or intent), `narrative` (description or characterisation in the author's voice), `reflection` (closing lesson or self-assessment), `other`.
- Tag role honestly. The genre profile exempts `motive`, `narrative`, `reflection` and `own_record` in a case study. Tagging an outcome claim as narrative would hide it from the checkers, and tagging a reflection as an outcome would bring back the trial's largest noise group.
- **`own_record` has hard limits.** A case study exempts it, so a wrong tag hides a claim. A claim that names an outside count or event (prosecutions, incidents, police officers, court cases, deaths) or an outside body (a ministry, a court, a statistics office, a named NGO) is never `own_record`, even when the author's own monitoring relayed it: "our monitoring counted 30 court cases last year" is a `figure`. A `general_claim` is never `own_record`. When in doubt, use the other role.
- One sentence can hold two claims ("63% of the 240 participants, a rise the programme drove"): list both.
- **A motive that rests on a general claim is two claims.** "We chose peer educators because young people trust peers more than teachers" holds a motive (we chose peer educators) and a general claim (young people trust peers more than teachers). List the motive with role `motive` and the general claim, quoted on its own, with role `general_claim` and type `cause` or `source`. The same holds for narrative and reflection. Do not split a sentence that only states intent ("we wanted every session to feel safe").
- **`cited_source`**: fill it whenever the text names who said or published the fact ("according to the health ministry", "the national survey shows"), whatever the claim's type. The router sends such claims to the source checker too.
- Quote exactly, curly apostrophes included.

---

## voice → `check_voice.json` (L1, whole document)

Audit only; never rewrite the document. Apply the `ane-voice` skill's rules in audit mode: British English, the substitution table in `writing-style-guide.md` (work folder), no em-dashes in body prose, active voice, sentence length, no hedging where none exists. Category `grammar` or `style`, always with `rule`. Severity `optional` for style. Use `should` for grammar that changes meaning or blocks a reader whose first language is not English, and `must` for grammar that makes the sentence say something false.

In `others` mode, report only what the author would recognise as an error or a real barrier to reading. Do not impose Ane's house style on a partner's document: the trial rejected four style preferences (C07, C11, C12, C22). Do not report hyphenation or spelling variants that are consistent within the document.

---

## references → `check_references.json` (L1)

Runs on Sonnet (Run A fixes, Fix 6). The brief follows the saved `citation-verification` workflow's checks, but this agent runs them itself: the workflow takes no model argument.

1. Read `document.md` in full. List every citation and hyperlink: inline citations, evidence-base lines, footnotes, bare linked sources. One entry per source per distinct claim.
2. If there are more than 12, check the 12 that matter most: those a reader would act on first, then sources you do not recognise, then order of appearance. Name every citation you did not check in one `optional` finding, so none is silently dropped.
3. For each citation, assume it is wrong and try to show it. Test four things:
   - **Exists and attributed.** Do the author, year and title match a real source? Search the web.
   - **Current.** Does a newer edition or a superseding document exist? Read `mel_wiki/wiki/domain-standards.md` (work folder) first, then search.
   - **Link.** Does the URL open, this run, on the canonical source (the publisher, the issuing institution or an official repository)? A link only to an aggregator (ResearchGate, academia.edu, Wikipedia) fails this test.
   - **Forbidden.** Is it on the citation-errors list in `domain-standards.md`?
4. Write a finding only when a test fails: `category: "citation"`, `checker: "references"`, with the page you fetched in `verified` (contract rule 9). A citation you cannot confirm exists is a `warning` that says so plainly. Never guess a citation into existence. When all four tests pass, write nothing.

---

## brand → `check_brand.json` (L1, .docx only)

The main session runs `python <office-review-pass>/scripts/review_pass.py verify <source.docx> --expect-branded` and converts each failed assertion to a finding: `category: "layout"`, `checker: "brand"`, quote = the first five words of the document's first body paragraph. Severity: `should` in `own` and `proposal` mode. In `others` mode use `optional`, unless Ane says the document will be published under IPPF branding, because a partner's own document is not bound by IPPF Visual Identity 2025.

---

## coherence → `check_coherence.json` (L1, whole document)

Read `document.md` end to end, Background and closing sections included: the other half of a tension often sits in a passage no claim checker sees. Report only two kinds of finding.

1. **Tension** (`kind: "tension"`). Two passages a reader cannot hold together without a link the document does not give. Numeric or not. Quote the first passage in `quote` and the second in `locations`. The suggestion names the missing link. Synthetic example: "The clinic ran at full capacity all year" in one section and "many booked appointments went unused" in another. The suggestion asks the author to say which period or service each sentence describes.

   **Trajectory check (always run it).** One kind of tension hides in plain sight, because each passage reads well on its own.
   1. List every forward statement of scope: "new", "first", "introduced in", "expanded to", "will reach", "launched".
   2. For each, search the whole document for earlier statements about the same service, place or group, including passages about past years.
   3. Ask whether the two passages tell one story the reader can name: an expansion, a restart after a closure, or a replacement. If the document never says which, report a tension and quote both passages.

   Synthetic example: "the counselling service has operated across the district for a decade" and, later, "counselling will be introduced in three new health centres". The suggestion asks whether the new centres extend the existing service or restart it after a closure. When the document states the link ("after the two-district pilot, the service opens in four new centres"), write nothing.
2. **Unquantified result** (`kind: "unquantified"`). An evaluative word for a result the programme could count ("remarkably strong attendance", "a sharp rise in referrals", "surprisingly high demand") with no figure for it anywhere in the document. Search the whole document before you report: a figure in an annex or a table counts. The suggestion asks for the figure, or for the comparison the word implies.

Every finding is `status: "warning"`, `severity: "should"`, `category: "substance"`, with `kind` set. The schema refuses anything else, and the challenger tests every one.

**Out of scope, never report:**
- Any demand for outside evidence. That belongs to the source checker.
- Motives, narrative or reflection, unless the sentence states a countable result.
- Style, wording or structure. That belongs to voice.
- A restatement of the same point in several places. Report it once, with the other quotes in `locations`.

When two passages can be read together without strain, write nothing. An empty list is a good result on a coherent document.

---

## number → `check_numbers.json` (L2)

For each claim in your queue:
1. Does the figure have a source in the document (a table, an annex, a named dataset) or in the supplied data file? If none: `warning`, `should`.
2. Is it internally consistent? Percentages of a base stated elsewhere; totals that add up; the same figure stated the same way throughout. An inconsistency is `error`, `must`, with every conflicting quote in `locations`.
3. Is it described correctly (a percentage-point change called a percentage change; "doubled" when the data shows +60%)? `error`, `must`.

If a data file is listed in `run.json` → `data_files`, ALSO write `recompute.json`: one spec per figure the data can settle (shapes in `ane_package/deliverable_doctor/recompute.py`). Do not compute the figures yourself. The recompute step does that after Ane approves it.

---

## source → `check_sources.json` (L2)

Your queue holds `source` and `fact_about_context` claims, and also claims of other types whose text names a source (`cited_source` is filled). For each claim, fetch the source in this run and record `verified` with the passage you found (contract rule 9). Check three things separately: **the fact, the date, and the body that issued it.**

Every claim in your queue must end in exactly one of two places. A claim that ends in neither is listed as unaccounted in the report and sent back to you.
1. **A finding** in `check_sources.json`.
2. **A cleared record** in `cleared_source.json`, when the source confirms the claim. One record per claim:
   ```json
   {"claim_id": "cl-004", "quote": "exact claim quote", "checked": "fact, date and issuing body",
    "source_kind": "law | report | dataset | web | other",
    "verified": {"url": "...", "fetched_in_run": true, "passage_found": true,
                 "passage": "the sentence you found", "source_version_date": "YYYY-MM-DD or null"}}
   ```
   A cleared record without a found passage does not count. Cleared records never reach the author. Ane reads them in the report and can overturn a wrong clearance.

**Outcomes.**
- **Confirmed**: the passage supports the claim as written. A paraphrase that keeps the same status (same fact, date and body) is confirmed. Write a cleared record, not a finding.
- **Misattributed**: the passage contradicts the attribution or the fact. `error`, `must`, `kind: "attribution"` when the problem is who said it. Only when you have the passage.
- **Imprecise** (`kind: "imprecise"`): the source supports a reading that changes the status the text implies: whether something exists or not, a date, the issuing body, or a number. `warning`, `should`. Quote the text and the passage, and suggest precise wording. Synthetic example: the text says a scheme "started in 2021"; the passage says it was announced in 2021 and began in 2022. Another: the text says "there is no national guideline"; the passage shows guidance exists as one section of a wider national plan. Both are imprecise, not confirmed.
- **Named body not found** (`kind: "attribution"`): the passage names a different originating body, and you cannot find the body the text names. `warning`, `should`. Warning is the default because a relaying body and an originating body can both be right: a statistics office's bulletin republished in a regional health board's yearbook is on record with both bodies. Synthetic wording: "We found this figure in the national statistics office's yearly bulletin. If the health ministry also published it, name that document."
- **Source cannot be found or opened** (`kind: "not_found"`): `warning`, `should`, and say so plainly. Allowed only after **both** searches below have failed.

**Search the fact, not only the body.** Before you report "cannot be found", run a second search on the fact alone: the figure plus its subject, with no body named, in the document's language and in English. If a passage turns up under another body, the outcome is **named body not found** (`kind: "attribution"`): quote that body's passage and ask whether the named body also published it. Report `not_found` only when the fact-only search also finds nothing. Record every search in `verified.searches` as `{"query": "...", "names_body": true | false}`. A `not_found` finding with no search where `names_body` is `false` fails the schema and comes back to you. A `not_found` finding has no page to cite, so its evidence is the list of searches.

Synthetic example: the text credits a count of clinic closures to "the minister's answer in parliament". A search for the minister's answer finds nothing. A search for the count and "clinic closures" alone finds the same count in the statistics office's annual bulletin. The finding names the bulletin and asks whether parliament also disclosed the figure.

**Sensitive run or offline source pack.** When your prompt tells you to check only against sources in scope (a sensitive run, or a fixture that supplies a local source pack), run both searches inside those sources, never on the web. Record the local file as the passage's `url`. The two-search rule is the same.
- `fact_about_context` claims with no source in the document: check them against a canonical source (issuing body, official gazette, publisher). If you cannot confirm the fact, write a `warning` that asks the author to verify it, and name what to check.

**Laws, codes and regulations.** Record the version date of the text you read in `source_version_date` and set `source_kind: "law"`. Before you clear the claim, search for amendments after that date. A cleared law record without a version date counts as unaccounted. Check the legal category too: an act can be covered as a named offence, as a qualified form of another offence, or as an aggravating circumstance, and these are different claims.

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
- **`general_claim` in the case-study profile** (a statement about how the world works, such as "prevention costs less than response"): `warning`, `should`. The suggestion asks the author to state the basis, or to present it as the organisation's own view ("in our experience…"). Never ask for a study or an evaluation design. The same rule applies when the source checker receives a `general_claim`.

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
