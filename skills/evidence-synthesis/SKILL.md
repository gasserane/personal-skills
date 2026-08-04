---
name: evidence-synthesis
description: Conduct a rigorous rapid evidence assessment or systematic-lite literature review for MEL/SRHR questions. Use when Ane asks for "evidence review", "literature review", "evidence synthesis", "REA", "what does the evidence say", "what do we know about", or similar. Produces a structured brief with question framing, method, findings by theme, confidence grading, and implications for programme or evaluation design. Does not invent citations.
---

# Evidence Synthesis

Rapid evidence assessment without shortcuts that collapse confidence. Every finding carries a source and a confidence grade. Gaps are named, not hidden.

## When to use

Trigger for evidence review work: programme design questions, evaluation framing, policy briefs, funder questions about what works, contribution analysis needing prior-evidence assembly.

Do not trigger for news scans, stakeholder mapping, or quick factual lookups. Those are different tasks.

## Required inputs

Ask in one batch. The first two are required.

1. **Question**: what Ane needs the evidence to answer, as a specific question (required)
2. **Purpose**: programme design, evaluation framing, policy advocacy, donor response, academic input (required; shapes depth and format)
3. **Scope constraints**: geography, population, intervention type, time range (optional; will default if missing)
4. **Sources Ane trusts or distrusts**: organisations, journals, or author groups to prioritise or treat cautiously (optional)
5. **Timeline**: how much time Ane has — determines whether rapid (2 hours), standard (1-2 days), or rigorous (1-2 weeks) synthesis (default: rapid)

## Method

### Step 1 — frame the question

Use the framework that fits:
- **PICO** for intervention-effectiveness questions: Population, Intervention, Comparison, Outcome
- **SPIDER** for qualitative or mixed-method questions: Sample, Phenomenon of Interest, Design, Evaluation, Research type
- **SPICE** for service evaluation questions: Setting, Perspective, Intervention, Comparison, Evaluation

Show the frame explicitly before searching.

### Step 2 — define inclusion and exclusion criteria

For rapid synthesis: minimum criteria are population, intervention or phenomenon, outcome, timeframe (default last 10 years), language, study type.

State each criterion. Explain any exclusion decision that would surprise a peer reviewer.

### Step 3 — select synthesis approach

Choose one, name the choice:
- **Thematic synthesis**: when findings group into recurring themes (Thomas & Harden 2008)
- **Narrative synthesis**: when studies are too heterogeneous to pool but a structured summary is needed (Popay et al. 2006)
- **Realist synthesis**: when the question is "what works, for whom, in what circumstances, and why" (Pawson et al. 2005)
- **Meta-analysis**: only when effect sizes from comparable quantitative studies can be pooled. Usually out of scope for rapid work.

### Step 4 — search and screen

**Duplication test first.** Before searching for evidence, search OpenAlex for published reviews on the question itself (`ane_package.literature`, commands in the `literature` skill: `dup-test`). If a review already covers the ground, state the value-add of this synthesis over it (new population, period, context, method, or lens) or narrow the question with Ane. A clean result can be a terminology miss — re-run with the field's own vocabulary before concluding the field is empty.

**When the duplication test comes back clean, run the era split** (`literature` skill: `era-split`). It searches the same topic either side of a split year and reports which terms entered the literature and which faded. Two uses. It names the older vocabulary to re-search, which is the most common reason a field looks empty when it is not. And the direction of the shift is itself a finding for the Method section: terms like `trial`, `cohort` or `implementation` entering mark an evidence base that has matured, which changes what confidence grade the body of evidence can carry.

**When study design decides usability, escalate to Consensus.** OpenAlex cannot filter by sample size, study type, human-only, or journal tier. For effectiveness questions where an underpowered or non-human study is not usable evidence, use the Consensus escalation documented in the `literature` skill, apply only the filters the question requires, and record the result cap it reports.

If Ane provides sources, use them. If not, ask where to search:
- Grey literature: WHO, UNFPA, UNAIDS, IPPF, Cochrane, 3ie, relevant IGOs
- Academic: PubMed, Scopus, Global Health Database, Cochrane; OpenAlex via the `literature` skill (open-access links, citation-velocity signals)
- Ane's resource library: `3. Ane's RESURSE/` subfolders matching the topic

Never invent citations. Check each candidate source's retraction flag when it comes through OpenAlex — a retracted work is excluded and noted. If a search cannot be conducted in this session, ask Ane to paste the top sources or point to the library subfolder.

### Step 5 — extract findings

For each source, extract:
- Full citation (author, year, title, journal or publisher, DOI if available)
- Setting and population
- Intervention or phenomenon studied
- Key finding, in the source's own framing
- Study design and sample size
- Confidence flags: low sample, non-random, self-report, author conflicts, funder bias

### Step 6 — grade confidence

For each finding or theme, grade using a GRADE-adjacent scheme:
- **High**: consistent findings across multiple rigorous studies; mechanism understood
- **Moderate**: consistent findings but with methodological limitations or narrow context
- **Low**: few studies, or conflicting findings, or serious bias risk
- **Very low**: single source or methodologically weak studies only

Explain the grade in one clause. No inflation.

### Step 7 — map where the evidence conflicts

Consensus is rarely the whole story, and smoothing it hides the most useful signal. After grading, map the disagreements:
- Where two or more sources reach opposite conclusions on the same question, name both with citations.
- Where a finding holds in one setting or population but reverses in another, treat that contrast as a finding, not noise.
- Where the strongest-evidence source disagrees with the most-cited or most-recent one, say so.

Do not resolve a live disagreement by picking the convenient side or averaging the two. State the conflict, say which reading the evidence currently favours and why, and flag any conflict the evidence cannot yet settle with `⚠️ Unresolved:`.

### Step 8 — apply the relevant lenses

For SRHR or gender-related questions, apply:
- **Feminist lens**: whose voices shaped the research questions? Are women and girls subjects of the research or objects? Cornwall & Rivas (2015) framing.
- **Decolonial lens**: where was the research conducted, who funded it, whose knowledge is centred? Chilisa (2020).
- **Intersectionality**: does the evidence disaggregate to current standard (age, gender identity, disability, geography)? Flag when it does not.

### Step 9 — identify gaps

Name what the evidence does not answer. Use `⚠️ Evidence gap:` format. Distinguish:
- Gaps in research (the study has not been done)
- Gaps in context (research exists but not from relevant settings)
- Gaps in population (research exists but excludes the target group)
- Gaps in method (research exists but with weak designs only)

### Step 10 — order the reading

A brief that lists twenty sources and ranks none of them hands the reader the sorting problem back. Before writing, pick 5 to 7 sources and put them in the order a newcomer should read them. The ordering logic, in sequence:

1. **The best recent review or meta-analysis first.** Broadest orientation for the least reading time. When a good systematic review exists it is almost always first.
2. **Then the foundational work** the rest of the field builds on. Usually older and heavily cited; the `anchor` signal from the `literature` skill identifies these.
3. **Then two or three at the current frontier**, especially any that extend or challenge the earlier consensus. The `rising` signal identifies these.
4. **Last, one source that exposes a gap or a live disagreement**, so the reader sees where the unsettled questions sit.

For each, write two sentences and no more: what it contributes in this sequence (not what it is about), and what to look for while reading it ("the effect sizes are compared in Table 3", "the discussion sets out the unresolved debate"). Hyperlink every title, open-access target first, because MA staff and partners cannot pass paywalls.

Order by what the reader needs, never by confidence grade or alphabetically. A low-confidence source can still be the right first read when it is the only one that frames the whole question.

## Output structure

Produce an evidence brief with these sections:

1. **Question** — as framed in Step 1, with the framework named
2. **Method** — inclusion criteria, search approach, synthesis approach, limitations of the rapid format
3. **Key findings** — organised by theme. Each finding:
   - One-sentence statement
   - Confidence grade
   - Supporting sources (author year)
4. **Where the evidence conflicts** — disagreements surfaced in Step 7, not smoothed. For each: the opposing findings with citations, which reading the evidence currently favours and why, or `⚠️ Unresolved:` where it cannot yet be settled
5. **Lens observations** — feminist, decolonial, intersectional notes
6. **Implications** — what this means for the stated purpose (programme design, evaluation, etc.). Be concrete.
7. **Start here** — the 5 to 7 sources from Step 10, in reading order, each with its one-line contribution and one-line what-to-look-for. Move this section up to sit directly after the executive summary when the brief's purpose is orientation rather than a decision, because a reader entering an unfamiliar field needs the reading order before the findings.
8. **Evidence gaps** — `⚠️ Evidence gap:` entries
9. **Sources** — full citations, alphabetical by first author
10. **Search audit** — the three numbers, never conflated: queries sent, unique results received, results cited. Name the tool used (OpenAlex, Consensus, hand-supplied), any result cap observed, every failed search, and any thin result set. Compute these from the run; never estimate them. A thin result is reported, never topped up from training knowledge.

## Citation requirements

Every finding cites at least one source. Method references:
- Thomas & Harden (2008) for thematic synthesis
- Popay et al. (2006) for narrative synthesis
- Pawson et al. (2005) for realist synthesis
- GRADE Working Group for confidence grading

For SRHR-specific framings:
- Cornwall & Rivas (2015), Chilisa (2020) for lenses
- WHO (2010) WHO/RHR/10.12 + UNFPA HRBAP + UNFPA SoWP 2021/2024/2025 for rights-based framing

## Writing rules

Follow CLAUDE.md house style. In this skill specifically:
- Never summarise a finding in language stronger than the source supports.
- Never present contested findings as settled.
- Never use "evidence shows" without a specific citation.
- Flag when a finding is contested, and by whom.

## Limitations

Rapid syntheses are not systematic reviews. State this limitation in the Method section. Do not invent effect sizes or pool findings across incompatible studies. If Ane needs a systematic review, route to a proper review protocol (PRISMA) rather than inflating rapid-review scope.

## Edit-preservation protocol

If Ane references an existing output by path and asks to improve, iterate, or expand it, the protocol activates. Read the file first, edit scope-bounded via the Edit tool, preserve out-of-scope content byte-identical, and return the EDIT-PRESERVATION DELIVERY summary.

Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.
