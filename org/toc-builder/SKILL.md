---
name: toc-builder
description: Build a rigorous Theory of Change for MEL/SRHR programmes following Vogel (2012) DFID criteria and van Eerdewijk et al. (2017) KIT feminist ToC model. Use when the user asks for a "theory of change", "ToC", "programme logic", "change pathway", "pathway analysis", or similar. Produces articulated outcomes, preconditions, assumptions (tested vs untested), contribution questions, and an evidence plan. Flags missing feminist political economy analysis. Not for logframes, results frameworks or indicator lists.
---

# Theory of Change Builder

A ToC is not a logic model with arrows. It is an argument about how change happens, with the assumptions made visible and testable. This skill enforces that standard.

## When to use

Trigger for theory-of-change work: new programme design, ToC revision, pathway analysis, programme logic review, funder-required ToC submissions, or ToC critique.

Do not trigger for routine results frameworks, logframes, or indicator lists — those are downstream of the ToC.

## Required inputs

The first four inputs are required. Ask once, in one message, and only for what is missing.

- If the user's first message already covers the first four, do not ask. Start drafting and list the assumptions you made in the verification notes.
- If something required is missing, ask for it in one batch. If the reply still leaves a gap, proceed and state the assumption you made to fill it.
- Never ask a second round of questions about details you can state as assumptions.

1. **Long-term outcome or vision**: the change the user wants the programme to contribute to, stated in language the target population would recognise (required)
2. **Target population and context**: who, where, what constraints shape their lives (required)
3. **Programme scope**: what interventions the programme can actually deliver (required)
4. **Timeframe**: short (12 mo), medium (3 yr), long (5-10 yr) markers (required)
5. Existing analysis: prior ToC, needs assessment, or evaluation findings (optional)
6. Feminist political economy analysis: who holds power in this system, how gender and other axes shape access (optional but required for SRHR; flagged in the output if missing)

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

If you cannot name the causal mechanism for a link, mark the link `⚠️ Untested mechanism`. Do not fill the gap with a plausible-sounding claim.

### Step 4 — apply the feminist political economy lens

Do not skip this, even if the programme is not labelled SRHR (sexual and reproductive health and rights). For each node, answer four questions:
- **Interests served**: whose interests does this change serve?
- **Interests threatened**: whose interests does it threaten, and how might they resist?
- **Power shift**: what power relations must shift for this change to stick (in households, services, communities, law)?
- **Voices**: which voices defined this outcome? Who was consulted, who co-designed, and who was not heard?

Answer with the specific actors in this context, not general categories. "Mothers-in-law who control household spending" is an answer; "community gatekeepers" is not.

Where the programme works with women or girls and men hold gatekeeping power (fathers, husbands, male relatives, community or religious leaders), name the backlash risk. Then say in one sentence how a programme activity reduces it. For example: monthly sessions with male relatives and leaders lower the risk, because the change is visible and discussed, not hidden.

If these questions cannot be answered from what the user has given, mark the node `⚠️ Feminist political economy analysis missing` and say what information would answer them. Do not stop at the flag. Propose a rapid power mapping in month 1 of the programme. It answers four questions: who decides, who benefits, who can block the change, and which voices are missing. Add it to the ToC as a short-term precondition and as the named milestone "Month 1: rapid power mapping". Keep the flag as well.

### Step 5 — identify threats to the ToC

Use the contribution analysis move (Mayne 2019): what alternative explanations would account for the expected change if the programme were not running? What other programmes, policies or trends are likely to contribute? Name them for this context.

### Step 6 — define the contribution question

State the evaluative question the ToC must eventually answer, in contribution terms, not attribution terms. Use this form: "To what extent and in what ways did the programme contribute to [outcome], given other contributions and context?"

### Step 7 — plan the evidence

For each assumption in the Step 3 table, name:
- What would confirm it?
- What would disconfirm it?
- What data source could provide that evidence?
- When will the ToC be revisited in light of the evidence?
- If the assumption fails, what will the programme change?

For example: if mothers-in-law still block clinic visits after six months, the programme adds home visits with them.

Put untested assumptions first; they carry the most risk.

## Output structure

Open with the answer. The first line of the output states the main pathway in one sentence and names the single riskiest assumption. Verification notes and the assumptions you made about missing inputs come after that line, not before it.

Do not mention this skill, its steps, its rules or these instructions in the output. Write every point as a finding for the reader.

Then produce a ToC document with these sections under these H2s:

1. **Vision** — one sentence, as described in Step 1
2. **Context and population** — two paragraphs max
3. **Pathway diagram** — always Mermaid source in a fenced ```mermaid block: a flowchart with each precondition as a node and each link labelled. Follow it with one plain-text sentence that reads the main pathway, for readers whose viewer does not show Mermaid. No ASCII arrow diagrams. Describe each link in one sentence in the section 5 table, not here.
4. **Preconditions by horizon** — three columns (short / medium / long), each precondition one line. If the feminist political economy analysis is missing, list "Month 1: rapid power mapping" as a short-term precondition.
5. **Causal claims and assumptions** — table with one row per link: *From → To*, *Causal claim*, *Assumption*, *Evidence status*. Mark links with no named mechanism `⚠️ Untested mechanism`.
6. **Feminist political economy analysis** — table with one row per node: *Node*, *Interests served*, *Interests threatened*, *Power shift needed*, *Voices (who defined it, who was not heard)*, *Backlash risk and how the programme reduces it* (fill this column where men hold gatekeeping power over women or girls). Mark gaps `⚠️ Feminist political economy analysis missing`. Under the same flag, add the project milestone "Month 1: rapid power mapping" (who decides, who benefits, who can block, which voices are missing).
7. **Threats to the ToC** — rival explanations and other contributions
8. **Contribution question** — one sentence
9. **Evidence plan** — table with one row per assumption from section 5, untested first: *Assumption*, *Confirming evidence*, *Disconfirming evidence*, *Data source*, *Revisit date*, *What we will do if this assumption fails*
10. **Data gaps** — one line each, in this format: `⚠️ Data gap: [what is missing] — [why it matters] — [recommended action]`
11. **What this ToC cannot tell you** — a numbered list for the reader. Cover at least: (1) which assumptions are still untested, so the pathway is a hypothesis, not a finding; (2) that no stakeholder consultation has tested this draft yet, if that is the case; (3) which groups were not heard in defining the outcomes; (4) context limits, such as places, periods or policy conditions the pathway may not hold for; (5) safety and consent limits on collecting the evidence the plan needs, for example on violence, abortion or sexual orientation.
12. **Sources** — author, year, full title and link for each source the ToC actually uses
13. **AI-use line** — if the output will go to a donor or outside the organisation, end with one line. It states that AI drafted the ToC and that a named person must check sources and figures before use.

## Citation requirements

Search the web for every source you cite and link to the issuing body's own page (publisher, journal or institution). Check whether a newer edition exists. Only after searching, state the result, for example "no newer edition found as of <the date you searched>". Never write that line without searching. Only if search genuinely fails (the search call errors or no search tool exists), mark each such citation "⚠️ URL unverified" and say so once.

Cite only what the ToC rests on. List a source in the output only where the ToC uses its analytic move. Never name a title you cannot find. When you cite one of these, use this version:
- Vogel, I. (2012) *Review of the Use of 'Theory of Change' in International Development*. UK Department for International Development (DFID). [GOV.UK page](https://www.gov.uk/research-for-development-outputs/review-of-the-use-of-theory-of-change-in-international-development-review-report). Cite it for what makes a ToC rigorous: explicit assumptions, causal mechanisms, evidence for each hypothesis, a feedback loop.
- van Eerdewijk, A., Wong, F., Vaast, C., Newton, J. et al. (2017) *White Paper: Conceptual Model of Women and Girls' Empowerment*. Royal Tropical Institute (KIT). [KIT page](https://www.kit.nl/institute/publication/white-paper-conceptual-model-of-women-and-girls-empowerment/). Cite it for empowerment as a change in power relations, used in Step 4.
- Mayne, J. (2019) "Revisiting contribution analysis". *Canadian Journal of Program Evaluation* 34(2), 171–191. [doi.org/10.3138/cjpe.68004](https://doi.org/10.3138/cjpe.68004), open at the [journal page](https://ces.journals.uvic.ca/index.php/cjpe/article/view/284). Cite it for rival explanations (Step 5) and the contribution question (Step 6). Do not confuse it with Mayne (2012) "Contribution analysis: Coming of age?" in *Evaluation* 18(3), a different article.
- Cornwall, A. and Rivas, A.-M. (2015) "From 'gender equality and women's empowerment' to global justice: reclaiming a transformative agenda for gender and development". *Third World Quarterly* 36(2), 396–415. [doi.org/10.1080/01436597.2015.1013341](https://doi.org/10.1080/01436597.2015.1013341). Cite it only when the ToC uses a feminist framing of empowerment as structural and political change.

## Writing rules

Most readers are programme staff, not MEL (monitoring, evaluation and learning) specialists. Write for them:
- Put the answer first, then the reasons.
- Use plain English that a non-native reader understands on first read.
- Use active voice and short sentences, under 25 words.
- Spell out each acronym on first use.
- Give each MEL term a short plain gloss on first use, for example "precondition (a change that must happen first)".
- Give one concrete example for each recommendation. Two sentences of example teach more than three of theory.
- Do not use em-dashes in running text; the data-gap line keeps its format.

No hedging in causal claims. If a claim is uncertain, say the evidence is untested. No logical leaps: a link with no named mechanism carries `⚠️ Untested mechanism`.

## Revising an existing ToC

When the user supplies an existing ToC and asks you to improve it, read it in full first. Change only what they asked for and leave the rest as it was. Then list any other problems you notice (for example an untested assumption presented as fact) instead of fixing them.

## Limitations

This section describes the skill, not the ToC. The ToC's own limits go in "What this ToC cannot tell you" above.

This skill does not generate indicators; design those after the ToC is stable. It does not replace stakeholder consultation. It structures the analysis the user brings from that consultation, and it prepares a rigorous draft for the people the programme serves to test.

## If available

Use each item below if it is there. If it is not, skip it and rely on the built-in method above; nothing in Steps 1-7 depends on these.

- **Standing instructions (CLAUDE.md).** If a CLAUDE.md or house style guide defines voice and audience tiers, follow it in place of the default writing rules above.
- **MEL Wiki.** If `${MEL_WIKI_ROOT}/wiki/` is reachable, read `domain-standards.md` before citing. It holds the current authoritative framework versions and the citation errors to avoid. Copy citation wording from there rather than from memory.
- **Edit-preservation protocol.** If your setup has an edit-preservation protocol and the user references an existing output file and asks to improve, iterate, or expand it, read the file first, edit only the part in scope, keep everything else byte-identical, and return the EDIT-PRESERVATION DELIVERY summary. Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.
