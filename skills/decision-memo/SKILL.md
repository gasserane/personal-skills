---
name: decision-memo
description: Draft a structured decision memo for Ane. Use when the user asks for a "decision memo", "decision doc", "options paper", "recommendation brief", or equivalent. Produces a scannable document with context, options, recommendation, risks, and reversibility. Applies Ane's CLAUDE.md writing style automatically.
---

# Decision Memo

One page, always. Built for decisions that need a record, not decisions someone can make in their head.

## When to use

Trigger on requests for decision documents, options analyses, recommendations, or choice briefs. Do not use for status reports or informational summaries.

## Required inputs

Ask for any missing inputs in one batch. Do not draft without the first three.

1. The decision to be made, stated as a question (required)
2. Who makes the decision, by when (required)
3. Current context: what changed, what is forcing the decision now (required)
4. Options already considered (optional; if provided, use them; if not, generate 2-4)
5. Constraints: budget, legal, political, capacity (optional but usually needed)
6. Success criteria: how will Ane know later whether the decision was right (optional)

## Structure

Produce a memo with these sections, in this order, each under the named H2. Target length: one page, 400-500 words.

### Decision required
One sentence ending in a question mark. Name the decider.

### Context
Three to five sentences. What changed, why it matters now, what happens if no decision is made. No backstory that predates the triggering change.

### Options
Two to four. Never just two unless the user specifies binary. For each:

- **Option label**: short noun phrase
- **What it is**: one sentence
- **Pros**: 2-4 bullets, specific, no generic benefits
- **Cons**: 2-4 bullets, including the worst realistic case
- **Reversibility**: one of *fully reversible*, *reversible with cost*, *effectively irreversible*. Explain in one clause.
- **Cost**: money, time, political capital, or capacity, in the currency that matters most

### Recommendation
One option, named. Two-sentence reasoning. No hedging. If the recommendation is weak, say the recommendation is weak and name the deciding factor.

### Risks
Three to five. Not the cons from above — the second-order risks specific to the recommendation. For each: the risk, the probability (low/medium/high), the mitigation, the owner of the mitigation.

### Next steps
Numbered list. Who does what, by when. Start with the decision itself: "Decide by [date], route via [channel]." End with the first action after the decision.

### Open questions
Optional. Use only if there is information the decider needs that this memo cannot provide. Use the `⚠️ Data gap:` format from CLAUDE.md.

## Writing rules

Follow CLAUDE.md writing style strictly:
- Active voice. Subject + verb + object.
- Sentences under 25 words. Split with periods if longer.
- Specific verbs: "approve" not "consider approving".
- No filler: no "in order to", "it should be noted", "as per".
- No nominalizations: "decide" not "make a decision".
- No hedging unless uncertainty is real.
- No em-dashes.
- No rhetorical questions.
- State the main point first in every paragraph.

## Tone

Candid, not deferential. If the recommendation is obvious, say so. If the options are all bad, name that. If the decision can be delayed without cost, recommend delay. The memo serves the decider, not comfort.

## Limitations

Do not invent facts, figures, or prior decisions. If a fact is needed and not provided, flag it with `⚠️ Data gap:`. Do not pad to reach a target length. A 250-word memo is fine if the decision is clean.
