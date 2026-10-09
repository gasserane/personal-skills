# MEL Working Discipline (`mel-discipline`): release note, 9 October 2026

**One text now works everywhere.** The skill runs the same in a plain claude.ai chat and in Claude Code. You no longer need a separate "team" version. Upload `mel-discipline.zip` once and it covers every surface.

**What the skill does.** It makes any Claude model follow five checks before it hands you a Monitoring, Evaluation and Learning (MEL) or Sexual and Reproductive Health and Rights (SRHR) brief, indicator set, Theory of Change or evidence review:

1. Scope the task first.
2. Open every source it cites.
3. Argue against its own recommendation.
4. Verify the finished draft.
5. Report plainly what it checked and what it could not check.

## What changed in this release

1. **The checks now use real tools.** When Claude can run code or save a file, it uses that to search the draft for long dashes, count the words and recompute the numbers. It checks by eye only when no tool is available, and then it tells you which checks were done that way. In testing, an earlier draft of this release estimated its word count and skipped the dash search, which is the exact failure this skill exists to prevent.
2. **Next steps that settle the question.** For each rival explanation, Claude now names the cheapest piece of evidence that would tell it apart from its own explanation. It also states which result would change its recommendation. In the test case, it asked the Member Association for clinic visits by time slot instead of a vague "monitor further".
3. **The source itself, not a summary.** Claude now opens the full document for any claim about what a source says. If it can only reach a summary page, it cites the source at that level and says so.
4. **The verdict comes first.** Nothing sits above the recommendation in the deliverable.
5. **Optional extras stay optional.** Standing instructions, a knowledge wiki, a resource library or a quality gate are used if your setup has them. The five checks work without any of them.

## How we tested it

We gave the old and new versions the same management brief, and Ane read both outputs without knowing which was which. The first draft lost; we found the causes, fixed them, and the second draft won. In a colleague test, the new version ran correctly in plain claude.ai chat. One limit: each version ran once per round, so treat the comparison as a strong signal, not proof.

## What you need to do

In claude.ai, open Customize > Skills. If you have an older `mel-discipline` or `mel-discipline-2` installed, delete it, then upload the new `mel-discipline.zip`. Then ask for any MEL deliverable as usual.

---

Release record: `gasserane/personal-skills`, commit `369e48c`. Before and after test runs: `evals/mel-discipline/runs/2026-10-09` and `runs/2026-10-09-2`.
