---
name: daily-brief
description: Produce a scannable morning briefing for Ane (Senior MEL/SRHR Specialist at IPPF). Use when the user asks for "daily brief", "morning briefing", "start of day", "what's on today", "plan my day", or similar. Assembles today's priority, calendar, overdue items, pending decisions, and an energy check. Operates on user-provided inputs by default; richer when calendar/email MCP servers are connected.
---

# Daily Brief

Produces a 60-second morning briefing. Outputs in a fixed structure so Ane can scan and act without re-parsing formatting every day.

## When to use

Trigger when the user opens the day, mentions a morning briefing, or asks what today looks like. Do not use for end-of-day summaries — route to `journal-reflection` for that.

## Required inputs

If no MCP is connected, ask the user for any of these that are missing before producing output. Ask in one batch, not iteratively.

1. Today's calendar (times, attendees, purpose)
2. Top 1-3 priorities carried from yesterday or the week plan
3. Overdue or blocked items (what is stuck, since when)
4. Decisions pending (what needs a call from Ane, by when, for whom)
5. Energy state in one word (fresh / tired / scattered / focused)

If calendar MCP or email MCP is available, pull directly instead of asking.

## Output format

Produce exactly these sections, in this order, each under the named heading:

**Top priority today**
One sentence. The single most important thing. Lead with the verb.

**Calendar**
Chronological list. For each: time, meeting, one-line prep note (who, goal, what Ane owns going in). Skip pure-FYI meetings.

**Overdue / blocked**
Bulleted. For each: what it is, what is blocking it, the next action and owner. Flag any item stuck more than 7 days.

**Decisions pending**
Bulleted. For each: the decision, by when, what Ane needs to decide, what information is missing.

**Energy check**
One sentence matched to the state the user reported. If "scattered", propose the one thing to drop today. If "tired", propose the one meeting to protect and the one to reschedule. If "fresh", propose the hardest thing to front-load.

**Data gaps**
List anything the user did not provide that meaningfully affects the brief. Use the format: `⚠️ Data gap: [what is missing] — [why it matters] — [recommended action]`. Omit this section if there are no gaps.

## Writing rules

Follow the house style from CLAUDE.md: active voice, sentences under 25 words, no em-dashes, no hedging, no performative softeners. Lead every line with the actor or the action. No abstract openings.

## Limitations

Do not invent calendar items, decisions, or blockers. If the user did not provide a section's inputs and no MCP supplies them, leave the section empty and flag it as a data gap. Do not pad.
