---
name: instrument-designer
description: Design MEL/SRHR data-collection instruments to IPPF/UNFPA publication standard. Use when Ane asks for a "questionnaire", "survey instrument", "interview guide", "KII guide", "focus group guide", "FGD guide", "observation checklist", "data collection tool", or "topic guide". Closes the gap between indicator design and analysis. Applies Groves et al. (2009) total survey error, Willis (2005) cognitive interviewing, Krueger & Casey (2015) FGD design, Brinkmann & Kvale (2015) interviewing, and ITC (2017) translation standards. Builds disaggregation in by construction and embeds consent and care-referral for sensitive content. Does not define indicators or analyse data.
---

# Instrument Designer

An indicator names what to measure. An instrument is the tool that produces the data. A rigorous indicator collected through a poorly designed questionnaire yields data that cannot answer the question. This skill prevents that.

## When to use

Trigger for any data-collection tool: structured questionnaire or survey, semi-structured key-informant or in-depth interview guide, focus-group discussion guide, observation checklist, or topic guide.

Do not trigger for indicator definition (use indicator-designer) or for analysing collected data (use the data-analysis or qualitative-coding workflows). This skill produces the tool that sits between them.

## Required inputs

Ask in one batch. First two are required.

1. **Measurement target** (required): the indicator set or research questions the instrument must capture. Ideally pulled from an existing results framework or ToC.
2. **Mode and population** (required): quantitative survey, qualitative interview/FGD, or observation; and who the respondents are (age, context, language).
3. Programme context: country or region, programme type (optional but shapes wording and sensitivity).
4. Languages the instrument will be used in (optional; decisive for translation planning).
5. Sensitive content flags: adolescent respondents, GBV, abortion, LGBTI+ (optional; triggers consent/assent and care-referral requirements).
6. Existing instrument to adapt or align with (optional).

## Method

### Step 1 — choose the instrument type

Match the tool to the purpose:
- **Questionnaire** — standardised stimulus for aggregation across respondents.
- **Semi-structured interview / FGD guide** — flexible scaffold for meaning, experience, and process.
- **Observation checklist** — practice and conditions observed directly.

Designing a qualitative guide as a group-administered questionnaire, or the reverse, is a quality failure.

### Step 2 — map every item to a construct

For each indicator or research question, write the items or questions that operationalise it. Trace every item to a named target. Cut orphans. Produce an explicit item-to-indicator map.

### Step 3 — design to standard

**Quantitative** (Groves et al. 2009; Willis 2005):
- One idea per question; no double-barrelled items; plain language; explicit recall period.
- Balanced response scales; decide explicitly on "don't know" / "prefer not to answer".
- Skip logic (routing) defined; sensitive items after rapport.

**Qualitative** (Krueger & Casey 2015; Brinkmann & Kvale 2015):
- Distinguish research questions (conceptual) from interview questions (everyday, answerable).
- FGD questioning route: opening, introductory, transition, key (2–5), ending.
- Pre-write probes; funnel from broad to specific; specify group composition logic.

### Step 4 — build disaggregation by construction

Add the disaggregation block as instrument items, never as a coding afterthought: age, gender identity (separately, not collapsed with sex assigned at birth), disability via the Washington Group Short Set, geography, and context axes (voluntary ethnicity self-identification for Roma programmes). You cannot disaggregate by an axis you did not ask about.

### Step 5 — embed ethics for sensitive content

For adolescent, GBV, abortion, or LGBTI+ content, include a consent script, an assent script plus guardian consent for minors, and a care-referral pathway in place before any data collection. This is a precondition, not an annex.

### Step 6 — plan translation and pretesting

- Multi-language: translate, independently back-translate, reconcile, and pretest per language (ITC 2017). Translation is a measurement-equivalence problem.
- Pretest in sequence: cognitive testing first (think-aloud, verbal probing) to find comprehension and sensitivity failures, then a field pilot for logistics and routing.

### Step 7 — flag data gaps

`⚠️ Data gap: [what cannot be captured] — [why it matters] — [recommended action: adapt a validated item, add collection, or descope]`

## Output structure

Produce:
1. **Instrument type and rationale** — one short paragraph.
2. **Item-to-indicator map** — table linking each item to its target.
3. **The instrument** — full questionnaire with response formats and skip logic, OR the questioning route with probes, OR the observation schedule.
4. **Disaggregation block** — the standard demographic items.
5. **Consent / assent / care-referral** — where the content requires it.
6. **Translation and pretesting note** — back-translation plan and the cognitive-testing-then-pilot sequence.
7. **Data gaps**.

Export the instrument as an IPPF-branded Word document via `ane_package.reporting.word_export`. For a structured questionnaire intended for field deployment, also emit a KOBO/ODK-deployable XLSForm: assemble the items into the survey-definition dict (schema documented in `ane_package.reporting.xlsform`) and call `xlsform.write_xlsform`. The file uploads straight to KoboToolbox (New project, then Upload an XLSForm) and bridges to the KOBO ingestion adapter (`ane_package.ingest.sources.kobo`). The XLSForm is a machine-read deployment file, so it carries no IPPF brand formatting; the Word document is the human-facing instrument. Adapt validated items from DHS-8 Model Questionnaires or UNICEF MICS6 tools rather than writing SRHR items from scratch; cite the source item and note the adaptation.

## Citation requirements

Mandatory, current editions:
- Groves et al. (2009) *Survey Methodology* 2nd ed (canonical)
- Willis (2005) *Cognitive Interviewing*
- Krueger & Casey (2015) *Focus Groups* 5th ed
- Brinkmann & Kvale (2015) *InterViews* 3rd ed
- International Test Commission (2017) *ITC Guidelines for Translating and Adapting Tests* 2nd ed
- WHO (2010) WHO/RHR/10.12 for the indicators; Washington Group (2016) WG-SS for disability
- For consent/assent/care pathways: the adolescent SRHR research ethics standard

Do not cite "WHO/UNFPA 2023" (unverified). Use WHO (2010) WHO/RHR/10.12.

## Writing rules

Follow CLAUDE.md house style. Question wording is plain and respondent-facing; instructions to the interviewer are marked distinctly from text read to respondents. Default register is Tier 1 working brief unless Ane names publication.

## Limitations

This skill designs instruments. It does not define indicators (indicator-designer), draw sampling frames, or analyse data. It does not replace cognitive testing and field piloting with real respondents; it produces a rigorous draft ready for that testing, and it specifies the testing plan.

## Edit-preservation protocol

If Ane references an existing instrument by path and asks to improve, iterate, or expand it, the protocol activates. Read the file first, edit scope-bounded via the Edit tool, preserve out-of-scope content byte-identical, and return the EDIT-PRESERVATION DELIVERY summary.

Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.
