---
name: decision-debate
description: 'Run a formal multi-perspective debate on a single contested MEL/SRHR design decision, then hand Ane a readable synthesis she decides on. Three to five persona agents, each mapped to a real specialist lens, research the call independently and blind to each other, then debate one round, then a synthesis is written in the decision-memo shape (context, options, recommendation, risks, reversibility) with agreements and genuine disagreements both kept visible. Use when Ane says "debate this", "run a decision debate", "I cannot decide between X and Y", "argue both sides of this design call", "get me independent perspectives on this", or names a genuinely contested MEL design choice where reasonable experts would disagree. Token-heavy by design: reserve for real decisions. Not for sharpening a design Ane already leans on (use /grill-mel), not for net-new builds (use brainstorming), not for a plain options paper on a call you do not need debated (use /decision-memo), and never for building anything.'
---

# Decision-debate (MEL/SRHR)

A formal debate that brings independent perspectives TO Ane on one contested MEL/SRHR design call. It operationalises the CLAUDE.md three-perspective rule: several agents research the same decision from different lenses, argue once, and the result is synthesised for Ane to decide on. It decides nothing itself.

## Lane — when this skill, not another

The grill family differs by direction, not topic:
- **decision-debate** (this): brings perspectives *to* Ane. Independent agents research and argue a contested call Ane did not answer herself. Use only when the answer is genuinely uncertain and reasonable experts would disagree.
- **/grill-mel**: pulls *from* Ane. Interviews her one question at a time to sharpen a design she already leans on.
- **brainstorming** (superpowers): for net-new *builds* headed to a code spec.

Reserved for genuine, consequential, contested decisions. Never for building. If the answer is already known, use /grill-mel or /ann. If the task is to produce a deliverable, use /ann.

## Gate before running

Confirm two things before spawning agents, because this is token-heavy:
1. The decision is **genuinely contested** (reasonable experts would split), not just unfamiliar to Ane.
2. It is a **decision**, not a build or a deliverable.

If either fails, stop and route to /grill-mel, /ann, or brainstorming.

## Method — three stages

State the decision in one sentence, confirm it with Ane, then run:

### Stage 1 — independent, blind research

1. Pick the personas. **3 by default, 5 for a high-stakes call.** Each persona maps to a real specialist lens from `agent-improvements/agent_registry.md`, not an invented character. The default trio:
   - **Method** (evaluation-design / contribution-plausibility stance): what can the evidence actually carry?
   - **Political economy and decolonial** (political-economy-reviewer stance): whose knowledge counts, what power sits in the data?
   - **Operational feasibility** (ma-priorities / reader-position stance): can the people on the ground do this, and does it serve the MA?
   For a 5-persona run, add the two lenses most load-bearing for the specific call (for example gender-transformative, safeguarding, or a costing/efficiency lens).
2. Spawn the personas **in a single message** so they run in parallel (the Vi parallel fan-out mechanism). Each gets the **same decision brief** but a **different lens mandate**, and researches **independently and blind to the others** using WebSearch, the knowledge MCP, and the MEL Wiki.
3. Each persona returns: its position, its one load-bearing reason, and the evidence behind it. Apply the citation standard. Flag any unsourced fact with `⚠️` rather than inventing it.

### Stage 2 — one debate round

Give each persona the others' Stage 1 positions. Each writes a short rebuttal: where it concedes, where it holds, and why. **One round only.** No endless back-and-forth.

### Stage 3 — synthesis Ane decides on

Write one readable Tier 1 brief in the `decision-memo` shape:
- **Context** — the decision in one sentence and why it is contested.
- **Options** — each live option with its strongest case, drawn from the personas.
- **Points of agreement** — where the personas converged.
- **Genuine disagreements** — kept visible, not smoothed over. This is the value of the debate.
- **Recommendation** — the recommended option, with the dissent recorded next to it.
- **Risks and reversibility** — what the recommendation costs and how hard it is to undo.

## The no-write gate

The debate decides nothing. The synthesis ends with this exact line:

> **DECISION REQUIRED, this is a recommendation not a decision.**

The skill **writes nothing to any canonical file**: no wiki edit, no registry change, no committed document. It returns the brief to Ane and stops. Ane decides; acting on the decision is a separate step she takes.

## Scale escalation

For an unusually large debate where deterministic token control matters, run the same three stages through the Workflow tool's judge-panel/parallel pattern instead: parallel persona agents in Stage 1, a debate stage, a synthesis stage, with `budget` bounding the spend. The Workflow route needs explicit opt-in each time; this skill is the routable default.

## Close

Hand Ane the synthesis brief and stop. Do not adopt the recommendation, edit any file, or start building. If Ane decides and wants the decision acted on, that is a fresh task for /ann or the right builder skill.
