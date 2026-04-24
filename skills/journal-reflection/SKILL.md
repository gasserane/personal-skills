---
name: journal-reflection
description: Guide Ane through structured reflection at end of day, end of week, after a decision, or after encountering new learning material. Use when the user says "journal", "reflect on today", "weekly review", "what did I learn", "after-action review", or references writing to the MELdigitalgarden vault. Produces Obsidian-compatible markdown; writes directly to the vault when filesystem MCP is connected, otherwise returns content for manual save.
---

# Journal Reflection

Structured reflection without the usual journaling bloat. Four modes. Pick one and run it tight.

## When to use

Trigger when the user asks to reflect, review, or capture learning. Not for morning briefings — route to `daily-brief` for that.

## Mode selection

Ask once, in one prompt, which mode applies. Default to end-of-day if the user says "journal" without specifying.

1. **End-of-day** (5 min): today in 3 questions
2. **End-of-week** (15 min): week in 5 questions plus a pattern scan
3. **Decision review**: one past decision in 4 questions
4. **Learning log**: one new framework or concept, linked to what Ane already knows

## Prompts by mode

### End-of-day

Ask these three, one at a time, waiting for each answer:

1. What got done today that mattered? (not a task list — what *moved*)
2. What got in the way, and what did it cost?
3. What does tomorrow need from you that today did not get?

Close with: one commitment for tomorrow, one sentence, verb-first.

### End-of-week

Ask these five, one at a time:

1. Against this week's stated goals, what is the honest progress? (percentage-free language)
2. What patterns showed up this week that also showed up last week?
3. What did you learn about the work, or about yourself doing the work?
4. What will you change next week? Specific, small, testable.
5. What deserves to be named as a win that you have not named yet?

Close with: one pattern-to-watch next week.

### Decision review

Ask:

1. What was the decision, and when did you make it?
2. What did you know at the time, and what were you guessing?
3. What happened in the days or weeks since?
4. What would you do differently if the decision arrived today?

Close with: one rule to carry forward, written as an if-then.

### Learning log

Ask:

1. What is the concept or framework? Cite author and year if it has one.
2. What problem does it solve that older frameworks do not?
3. How does it connect to something Ane already uses?
4. Where will Ane apply it first?

## Output format

Write Obsidian-compatible markdown with YAML frontmatter:

```yaml
---
date: YYYY-MM-DD
type: [daily | weekly | decision-review | learning-log]
tags: [journal, ...domain tags]
dg-publish: false
---
```

Use `[[wiki-links]]` for people, concepts, frameworks, and projects. Default `dg-publish` to false. If the user says the note is publishable, set to true and ask for the permalink stub.

Body structure: one H2 per prompt, the answer as plain prose under it, no bullets unless the content is a list.

## File placement

If filesystem MCP to `MELdigitalgarden` is connected:
- End-of-day: `src/site/notes/Journal/Daily/YYYY-MM-DD.md`
- End-of-week: `src/site/notes/Journal/Weekly/YYYY-Www.md`
- Decision review: `src/site/notes/Journal/Decisions/YYYY-MM-DD-<slug>.md`
- Learning log: `src/site/notes/Journal/Learning/<slug>.md`

If MCP is not connected, return the markdown as an artifact and name the target path so the user can save it manually.

## Writing rules

Follow CLAUDE.md house style. One exception: in journal answers, passive and reflective phrasing is acceptable when Ane's answer is itself reflective. Do not rewrite her words into active voice — preserve her voice exactly.

## Limitations

Do not invent reflections. Do not auto-answer the prompts. Prompts go to the user and wait. If the user skips a prompt, mark the section `(skipped)` and move on. Do not lecture.
