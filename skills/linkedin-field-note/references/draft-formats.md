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

## Sequencing check (run before showing Ane; caught a publish-blocker on #02)

The article and the short post get drafted together, but they **publish in order**: article first, post second, first comment third. The post may point back to the article. The article must never point at the post.

Check every cross-reference in the article and delete or rewrite any that assumes the reader has already read the post: "in the short version I gave one answer", "the short post tells this story in full", "as I said in the post". A reader meets the article cold, so each of those sentences points at something they have not seen.

Two consequences follow, both proven on #02:

- **The article carries the full story.** If a concrete example lives only in the post, and the post is being cut to the ultra-short shape, move that example into the article before cutting. The long article is where the whole story belongs.
- **A toolkit reference is a look-back, not a promise**, whenever the calendar puts the kit's Tuesday document post ahead of the article. Write "the kit I posted on Tuesday", not "a kit I will publish".

Grep the article draft for `short version|short post|as I (said|wrote)` and confirm zero hits before presenting.

## Rendering the .docx

**A stale `.docx` is the series' known failure mode.** After any revision round on the `.md`, the previously rendered `.docx` is out of date and must not be reviewed or published from. Do not re-render mid-revision either: rendering text Ane may still change recreates exactly the divergence her standing rule guards against (final text is copied only from the source file, never from an earlier draft). Render once, after she approves the text; from that point the `.docx` she hand-edits is authoritative.


Render from the `.md` with the personal-brand generators: read `generators/gen_article.py` and follow its pattern (fall back to `pb.py` primitives: `base_document`, `page_setup`, `para`, `style_run`, `rule_below`, `brand_footer`). Wine & Slate only. The `.docx` exists so Ane can review and hand-edit in Word; keep it faithful to the `.md`, no extra decoration.

## Before showing Ane

Run the ane-voice checklist over both drafts: active voice, sentences under 25 words, no em-dashes anywhere in the publishable text, no hedging, translatability pass (cut idioms and phrasal verbs), acronyms spelled on first use, warmth intact (do not sand off the story or the P.S. humour). Verify every number or carry its `⚠️` flag into the header block. Then present article and post together, ask for edits, iterate in conversation, and write files at her confirmed milestone.
