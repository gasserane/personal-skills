---
name: literature
description: 'Search 250M+ scholarly works via OpenAlex, direct API, no third-party relay. Four modes: quick literature search, duplication test (nearest published work to a planned question, state your value-add), debate map (common-ancestor anchor papers on a topic), forensic search (source one specific claim). Use when Ane says "search the literature", "is there a review on", "has this been done already", "duplication test", "who does everyone cite", "find me a citation for", "anchor papers", "is this field emerging or settled". For a full structured evidence review use /evidence-synthesis; for a COMPLEX-tier Evidence Brief use /researcher — both of those call this capability as a step. Not for reference management (Zotero via /li) or Ane''s own library (mcp knowledge search).'
model: sonnet
---

# Literature — direct OpenAlex search, duplication test, debate map

Wires Claude Code straight to the OpenAlex catalogue (open index of the
global research system, hundreds of millions of works). Query text goes to
OpenAlex only. Every result line carries year, citations, a velocity signal,
a retraction flag, and an open-access-first link.

## When to use

- A quick "what exists on X" before deeper work.
- Before designing any study, review, proposal, or learning question: run the
  duplication test and name the nearest published work plus the value-add.
- Entering an unfamiliar field: map the debate to find the anchor papers
  everyone cites.
- A specific claim needs a source: forensic search.

## Where the code lives

- `ane_package.literature` in the work folder — `OpenAlexClient` (client.py)
  and the four moves (moves.py): `duplication_test`, `citation_velocity`,
  `map_topic_debate`, `forensic_search`.
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
