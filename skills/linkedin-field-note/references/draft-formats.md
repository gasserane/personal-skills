# Stage 3 — DRAFT: article, short post, first comment

The `.md` files are canonical; `.docx` renders follow them until Ane hand-edits a `.docx`, at which point that file becomes authoritative (edit-preservation). Study the exemplars before drafting: the #01 article and the v3 ULTRA-SHORT post in the content folder are the proven shapes.

## File naming (match the folder's convention)

- `YYYY-MM-DD LinkedIn ARTICLE - field note NN - <short slug>.md` (+ `.docx`)
- `YYYY-MM-DD LinkedIn POST - field note NN - <short slug>.md` (+ `.docx` if Ane wants one)

## Article format

1. **Title = the claim, first person.** "I built a 33-agent AI system for evaluation work. Here is what actually mattered." Not a topic label.
2. **Italic header block** (metadata, never published): audience ("MEL practitioners with beginner-to-medium AI fluency" is the series default), draft date, publishing plan (article first, post links to it in first comment), and pre-post checks (numbers current if posting later than drafting; employer social-media guidance where the piece mentions IPPF work).
3. **Opening:** story (2 sentences max) or blunt claim; the BLUF lands by sentence three.
4. **Body:** numbered sections whose headers are claims ("Written standards beat clever instructions"), not labels ("Standards"). Each section: the lesson, the reason, one concrete example, and where MEL readers recognise the pattern ("It is the same reason we write indicator reference sheets").
5. **The candour section** sits inside the numbered flow, not in a disclaimer ghetto.
6. **"What comes next"** closing section: where the experiment goes, then the closing question to readers.
7. **P.S. — the AI-use disclosure**, in Ane's framing: written with help from the system it describes; she gave structure by dictation, the AI drafted, she checked and decided. Self-irony welcome here, once. A P.P.S. is optional (social-experiment framing, audience-as-data).
8. **Hashtags, last line:** `#AIFieldNotes #MEL #Evaluation #ResponsibleAI #AIforNGOs` (confirm against the ledger's series rules; Ane may evolve them).

## Short post format (the v3 ULTRA-SHORT shape, ~250-300 words)

1. Hook line = the thesis with its twist ("...and the agents turned out to be the least important part.").
2. One-paragraph context: why going public, why field notes.
3. Quick definition "in good MEL tradition" of the piece's one technical term, with a practitioner analogy.
4. The lessons as a numbered list, 2-3 sentences each (usually the article's top three).
5. "What comes next" in one or two lines.
6. Pointer: "The longer field note ... is in the article. Link in the first comment."
7. The closing question.
8. P.S. disclosure (compressed), then hashtags.

## First comment (draft it in the same stage)

The article link placeholder plus any P.P.S. that was trimmed from the post. Posted by Ane or by the skill immediately after the post goes live.

## Rendering the .docx

Render from the `.md` with the personal-brand generators: read `generators/gen_article.py` and follow its pattern (fall back to `pb.py` primitives: `base_document`, `page_setup`, `para`, `style_run`, `rule_below`, `brand_footer`). Wine & Slate only. The `.docx` exists so Ane can review and hand-edit in Word; keep it faithful to the `.md`, no extra decoration.

## Before showing Ane

Run the ane-voice checklist over both drafts: active voice, sentences under 25 words, no em-dashes anywhere in the publishable text, no hedging, translatability pass (cut idioms and phrasal verbs), acronyms spelled on first use, warmth intact (do not sand off the story or the P.S. humour). Verify every number or carry its `⚠️` flag into the header block. Then present article and post together, ask for edits, iterate in conversation, and write files at her confirmed milestone.
