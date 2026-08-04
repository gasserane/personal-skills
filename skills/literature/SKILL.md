---
name: literature
description: 'Search 250M+ scholarly works via the OpenAlex API directly: quick search, duplication test, debate map (anchor papers), forensic sourcing of one specific claim, era split across a year, plus a Consensus escalation for design-filtered searches (study type, sample size, journal tier). Use when Ane wants published literature found, a claim sourced, anchor papers, or to know whether a question has been done already. For a full structured evidence review use /evidence-synthesis; for a COMPLEX-tier Evidence Brief use /researcher. Not for reference management (Zotero via /li) or Ane''s own library (mcp knowledge search).'
model: sonnet
---

# Literature — direct OpenAlex search, duplication test, debate map, era split

Wires Claude Code straight to the OpenAlex catalogue (open index of the
global research system, hundreds of millions of works). In the default modes
query text goes to OpenAlex only, with no third-party relay; the Consensus
escalation below is the one exception and is opt-in per search. Every result
line carries year, citations, a velocity signal, a retraction flag, and an
open-access-first link.

## When to use

- A quick "what exists on X" before deeper work.
- Before designing any study, review, proposal, or learning question: run the
  duplication test and name the nearest published work plus the value-add.
- Entering an unfamiliar field: map the debate to find the anchor papers
  everyone cites.
- A specific claim needs a source: forensic search.
- A duplication test came back clean, or the field looks older than expected:
  run the era split before concluding anything.
- Study design or sample size decides whether a finding is usable: escalate
  to Consensus (see "Consensus escalation").

## Where the code lives

- `ane_package.literature` in the work folder — `OpenAlexClient` (client.py)
  and the moves (moves.py): `duplication_test`, `citation_velocity`,
  `map_topic_debate`, `forensic_search`, `era_split`, `terminology_shift`.
- `scripts/literature_cli.py` in this skill — thin driver, no logic.
- Tests: `tests/literature/` in the work folder (mocked, offline).

## Running it

All commands run from anywhere; the driver bootstraps the work folder path.

1. Quick search (add `--type review` to only see reviews):

```
python scripts/literature_cli.py search "adolescent contraception uptake Eastern Europe" --from-year 2020 --per-page 10
```

2. Duplication test on a planned question:

```
python scripts/literature_cli.py dup-test "determinants of youth-friendly SRH service uptake in rural Romania" --from-year 2015
```

3. Debate map — anchor papers on a topic:

```
python scripts/literature_cli.py debate-map "comprehensive sexuality education outcomes" --top-works 5 --ancestors 5
```

4. Forensic search — source one claim:

```
python scripts/literature_cli.py forensic "school-based CSE does not increase sexual activity"
```

5. Era split — has the vocabulary moved? Two searches, one either side of the
   split year (default 2015):

```
python scripts/literature_cli.py era-split "comprehensive sexuality education" --split-year 2015 --per-page 25
```

A single search can also be windowed to one era with `--to-year`:

```
python scripts/literature_cli.py search "adolescent contraception" --from-year 2005 --to-year 2014
```

## Grey literature — use the report and dissertation types

OpenAlex indexes more than journal articles. Two work types reach grey
literature and both are worth running on any SRHR or programme question:

```
python scripts/literature_cli.py search "adolescent SRH programme evaluation" --type report --per-page 15
python scripts/literature_cli.py search "youth friendly SRH services barriers" --type dissertation --per-page 15
```

Verified live 2026-08-04: `--type report` returned 3ie evidence gap maps,
Population Council technical reports and an evaluation of the Family Planning
Association of Kenya youth centre programme, which is an IPPF Member
Association. `--type dissertation` returned theses from Kenyatta University,
the University of KwaZulu-Natal and the Open University of Tanzania. All
open-access links.

Run these whenever the question concerns programme delivery, an MA context,
or any Global South setting. An evidence base built from journal articles
alone over-represents Western academic research and under-represents exactly
the programme evidence the decolonial lens asks to be centred, and the
omission is invisible to a lens check because the missing sources never
entered the pool. Low citation counts on these results mean little: a
country-level thesis or an NGO evaluation is rarely cited even when it is the
only fieldwork from that setting.

Two limits, both real. OpenAlex indexes only grey literature someone has
deposited with metadata, so an unpublished MA evaluation or a donor report
behind a portal will not appear; pair with WebSearch against the named
institutions and with the knowledge MCP over Ane's own library. And grey
literature carries no peer review, so it needs an appraisal step (authority,
accuracy, coverage, objectivity, date, significance) before it earns the same
weight as a reviewed source. Adding grey sources without that screen lowers
rigour rather than raising it.

## Reading the output

- One work per line: `year | citations | signal | title | link`.
- Signals: `rising` (recent citation surge AND field-weighted impact above
  1.5) marks a live debate; `anchor` (heavily cited, citations slowed) marks
  a settled reference point; `steady` and `quiet` sit between.
- A mostly-`rising` result list = emerging field; mostly `anchor`/`quiet` =
  saturated one. Say which in the deliverable when it matters.
- Lines starting `!!` are RETRACTED works. Never cite one; if a retracted
  work appears in an existing deliverable's evidence base, flag it.
- Links prefer the open-access URL, then the landing page, then the DOI
  (Tier 1 hyperlink rule: MA staff cannot pass paywalls).
- Duplication verdicts (`high`/`moderate`/`low` risk) ask for a stated
  value-add; they never decide. Put the nearest-neighbour paper and the
  value-add sentence into the deliverable, not just the verdict.
- Era split prints both cohorts, then the terms that entered and the terms
  that faded, as the change in the share of works using each term. Read it
  two ways. **Vocabulary:** re-run the search with the faded terms before
  concluding a field is empty, because current terms alone drop the
  foundational older work. **Maturity:** terms like `trial`, `cohort` or
  `implementation` entering signal an evidence base that has matured; a
  cohort that is all commentary and no design signals one that has not.
  When either cohort is too thin to compare, the driver says so rather than
  reporting a shift it cannot support.
- The stopword list behind the era split is heuristic. A few filler words
  survive it. Read the top of each list, not the tail, and judge the terms
  rather than counting them.

## Consensus escalation — when design filters decide usability

OpenAlex is the default and stays the default: direct API, no relay, no
per-query cap. It cannot filter by study design. When the question turns on
whether a finding is usable rather than whether it exists (only randomised
trials, only human studies, a minimum sample size, top-tier journals only),
escalate to the Consensus connector, `mcp__claude_ai_Consensus__search`.

Filters Consensus exposes that OpenAlex does not: `study_types`, `human`,
`sample_size_min`, `sjr_max` (journal tier), plus `year_min` / `year_max`.

Rules for the escalation, all mandatory:

1. **Say why you escalated**, in one line, naming the filter that OpenAlex
   could not apply. Escalation without a design filter in play is just a
   second search engine and does not belong here.
2. **Never apply a filter Ane did not ask for or the question did not
   require.** A silent `sample_size_min` reshapes the evidence base and looks
   identical to a genuine gap in the literature.
3. **Sequential only.** Consensus rate-limits at one query per second.
   Confirm each result arrived before sending the next; never batch or
   parallelise.
4. **Cite only what Consensus returned in this session.** Anything recalled
   from training knowledge is labelled `[not from Consensus — model
   knowledge]` and excluded from every count.
5. **Record the result cap.** Consensus returns a limited number per query and
   the cap depends on the account tier. Read the actual count off the first
   response and log it. ⚠️ The tier cap on Ane's account is unverified;
   report the number observed, never a remembered one.
6. **Follow the connector's own citation format** (numbered inline references
   plus a linked reference list, and its sign-up or usage message reproduced
   verbatim) whenever Consensus results reach Ane directly.

Consensus is a relay: query text leaves for a third party. That is the trade
for the design filters, so it is a deliberate escalation, never the default.

## Audit log — report the three numbers, always

Any run that feeds a deliverable ends with an audit block. Three numbers,
tracked separately and never conflated:

- **Queries sent** — how many searches actually executed, including retries.
- **Results received** — how many works came back, deduplicated by title.
- **Results cited** — how many reached the deliverable.

Report alongside them: the tool used (OpenAlex or Consensus), any result cap
observed, every failed search with its query, and any cohort or facet that
came back thin. Format:

```
Searched OpenAlex: 6 queries, 43 unique works received, 11 cited.
Cap: none (OpenAlex returns the full page). Budget left: $0.086.
Thin: the pre-2015 cohort returned 4 works — coverage there is incomplete.
Failures: none.
```

Three rules this enforces. A search is not done until its result is back, so
never count a query you have not seen return. A thin or empty result is
surfaced, never quietly topped up from training knowledge. And the counts are
computed from the run, never estimated, per the computed-counts rule: a
number describing an artefact goes stale silently.

## Things that will bite

- **Daily budget.** Anonymous access (with the polite-pool mailto baked into
  `ane_package.literature.config`) allows about $0.10/day — roughly 100
  searches. A free key from https://openalex.org/settings/api raises it to
  $1/day: set it as the `OPENALEX_API_KEY` environment variable. The driver
  prints the remaining budget after each run; a 429 error means the budget is
  spent for today.
- **A clean duplication test can be a terminology miss.** OpenAlex matches
  title and abstract text. Re-run with the field's own vocabulary (e.g.
  "family planning" vs "contraception", "young people" vs "adolescents")
  before declaring the field empty.
- **OpenAlex is not a quality filter.** Predatory-journal works are indexed
  too. Citation counts and venue names help, but the citation-verification
  gate in the consuming skill still applies before anything is cited.
- **Abstract-only matching.** OpenAlex does not search full text here; a
  concept discussed only in a paper's body will not surface.

## Limitations

- Read-and-report only: this skill writes no files. When results feed a
  deliverable, the consuming skill's rules (citation standard, evidence-base
  lines, edit-preservation) apply there.
- Coverage skews to indexed scholarly work; grey literature (NGO reports,
  donor evaluations) is thin. Pair with WebSearch and the knowledge MCP for
  grey sources.
