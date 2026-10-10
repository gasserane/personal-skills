# Indicator Designer (`indicator-designer`): release note, 10 October 2026

**One text now works everywhere.** The skill runs the same in a plain claude.ai chat and in Claude Code. Upload `indicator-designer.zip` once and it covers every surface.

**What the skill does.** It designs Monitoring, Evaluation and Learning (MEL) indicators for Sexual and Reproductive Health and Rights (SRHR) work to IPPF, UNFPA and UNAIDS standard. You get output, outcome and impact indicators kept apart, a full disaggregation plan (age, gender identity, disability, geography), an integrity tier for each indicator, a measurement mechanism and any data gaps flagged.

## What changed in this release

1. **Sources are checked on the web by default.** Claude now searches for the current edition of each standard before it cites it, and links the page it found. Searching is no longer optional. If search fails, Claude says so instead of claiming a source is current.
2. **It cites only what an indicator rests on.** A short list of sources the set truly depends on replaces a long list of general references.
3. **A new section, "What this set cannot tell you".** Claude states the limits of the indicator set in plain words, so a reader does not over-read the numbers.
4. **One table per indicator set.** For each indicator it shows how it is measured and what role it plays (for example, tracking a change or checking a risk).
5. **A short AI-use line.** The output says that Claude drafted it and that a person must verify the sources.
6. **The answer comes first.** The indicator set opens the output. Method and caveats follow.
7. **A wrong citation is removed.** An earlier version cited a "WHO/UNFPA 2023" sexual health indicators update. We could not find that document, so the skill now cites WHO (2010) *Measuring sexual health* (WHO/RHR/10.12).
8. **Your own setup is optional.** Standing instructions, a knowledge wiki or an edit-preservation rule are used if you have them. The skill works without any of them.

## How we tested it

We gave the old and new versions the same request, and Ane read both outputs without knowing which was which. The first rewrite lost, because it made web search optional and wrote a "no newer edition found" line without searching. We found the causes, fixed them, and the second rewrite won ("comprehensive"). In a colleague test, the new version ran correctly in a plain claude.ai chat when we named it. One limit: each version ran once per round, so treat the comparison as a strong signal, not proof.

## What you need to do

1. In claude.ai, open Customize > Skills.
2. If you have an older `indicator-designer` or `indicator-designer-draft` installed, delete it.
3. Upload the new `indicator-designer.zip`.
4. Ask for indicators as usual. If another skill answers instead, write "Use the indicator-designer skill to ..." in your request. The `mel-discipline` skill mentions indicator sets in its description and can fire first in a plain chat.

## Known limits

- The line "no superseding edition as of 2026-10" is a dated claim. Recheck it at the next standards review.
- A few sentences in the optional "If available" section are long. They only matter if you keep your own edit-preservation rules.

---

Release record: `gasserane/personal-skills`, commit `2d91ee2`. Before and after test runs: `evals/indicator-designer/runs/2026-10-09` (first rewrite, lost) and `runs/2026-10-09-2` (second rewrite, won).
