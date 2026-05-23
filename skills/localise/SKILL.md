---
name: localise
description: Produce an MA-facing deliverable in a target language (Romanian, French, Spanish, or Russian) to IPPF rigour, with English as the canonical source. Use when Ane asks to "localise", "translate this brief", "in Romanian/French/Spanish/Russian", "Romanian version", "produce a French companion", or "review my Spanish draft". Applies a curated SRHR glossary (controlled terminology), preserves the Tier 1 working-brief register, makes safeguarding-aware term choices, runs back-translation QA, and flags for native review. Never authors from scratch in the target language. Does not design instruments or audit English voice (use ane-voice for English).
---

# Localise

English is the canonical source. The target-language deliverable is derived and review-flagged. This skill produces a target-language version of a finished English deliverable, a target-language companion, or a review of your own target-language draft. It does not author from scratch in the target language.

Supported languages: Romanian (`ro`, fully curated), French (`fr`), Spanish (`es`), Russian (`ru`). French, Spanish, and Russian are working-draft glossaries refined at use. Adding a further language is a new glossary file.

## When to use
Trigger for: localising a finished English brief; producing a target-language companion to an English deliverable; reviewing a target-language draft you wrote. Do not trigger for English voice work (use ane-voice) or instrument design (use instrument-designer).

## Modes (detected from input)
1. **Localise a finished doc** then you provide an English deliverable (paste or path) and get a target-language version plus a QA note.
2. **English plus companion** then Vi or you provide the finished English deliverable and get a target-language companion alongside it.
3. **Review my draft** then you provide your target-language draft (plus the English source if available) and corrections are walked one by one, never a silent rewrite.

## Required inputs
1. The English source (or, for mode 3, the target-language draft plus the English source). Required.
2. Target language: Romanian, French, Spanish, or Russian (Romanian is the most curated; the others are working drafts).
3. Audience and member-association context (shapes register and cultural adaptation).
4. Restrictive-context flag (triggers the safeguarding pass on sensitive terms). Mandatory for Russian-language output (see the legal-review banner in the Russian glossary).

## Method
1. Read the target-language glossary `mel_wiki/wiki/glossaries/srhr-terminology-<lang>.md`, substituting the target-language code (`ro`, `fr`, `es`, `ru`). For Russian, read the legal-review banner at the top first.
2. Translate and adapt. Apply controlled terms; preserve BLUF, plain language, collaborative voice, numbered steps; adapt examples to the member-association context.
3. Terminology-compliance check. Confirm every glossary English term in the source uses the controlled target-language rendering.
4. Back-translation QA. Back-translate key passages to English; diff against the source; flag meaning drift.
5. Safeguarding pass. List every `sensitive`-flagged rendering used; in a restrictive context, surface the term choice for confirmation and route it to safeguarding-reviewer (mandatory for the legally-exposed Russian terms: LGBTI+, gender identity, sexual orientation, CSE, reproductive rights).
6. Output. IPPF-branded Word via `ane_package.reporting.word_export` with the document language set via the `lang` parameter (`ro`/`fr`/`es`/`ru`); plus the QA note.

## Output structure
1. The target-language deliverable.
2. Terminology-compliance note.
3. Back-translation QA note (meaning-drift flags).
4. Sensitive-term list and the choices made.
5. Native-review stamp ("native review recommended" / "validated by author").
6. Data gaps.

## Citation requirements
ITC (2017) *ITC Guidelines for Translating and Adapting Tests* 2nd ed; Brislin (1970) back-translation (canonical); WHO process of translation and adaptation. Controlled terms cite their glossary source.

## Writing rules
Follow CLAUDE.md house style for the English QA notes. The target-language prose follows the equivalent Tier 1 register in that language. Default register is Tier 1 working brief unless Ane names publication.

## Limitations
Produces a draft for native review where the author cannot validate the output. Does not replace native-speaker sign-off for languages the author does not read. Romanian is the most curated glossary; French, Spanish, and Russian are working drafts whose unsourced and competing-rendering terms are refined at first use. Russian carries restrictive-context legal-exposure flags — never distribute Russian-language SRHR material inside Russia without legal review and safeguarding-reviewer sign-off.

## Edit-preservation protocol
In mode 3, and any time Ane references an existing file by path, read the file first, edit scope-bounded via the Edit tool, preserve out-of-scope content byte-identical, and return the EDIT-PRESERVATION DELIVERY summary.

Apply mel_wiki/wiki/concepts/edit-preservation-protocol.md when target file exists.
