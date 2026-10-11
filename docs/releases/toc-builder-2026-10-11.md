# Theory of Change Builder (`toc-builder`): release note, 11 October 2026

**One text now works for any user.** The skill no longer assumes one person's setup. Your own standing instructions, wiki or edit-preservation rule are used if you have them, and the skill works without any of them. Upload `toc-builder.zip` once.

**What the skill does.** It builds a Theory of Change (ToC) for Monitoring, Evaluation and Learning (MEL) work on Sexual and Reproductive Health and Rights (SRHR) programmes. A ToC is an argument about how change happens, with every assumption visible and testable. You get a vision, preconditions by time horizon, causal claims with assumptions, a power analysis, rival explanations, a contribution question and an evidence plan.

## What changed in this release

1. **Two citations are corrected.** Mayne (2019) is now cited as "Revisiting contribution analysis", *Canadian Journal of Program Evaluation* 34(2), 171-191. An earlier version gave a different title and journal. The van Eerdewijk et al. (2017) entry now carries the full author list, the publisher (KIT) and a link.
2. **The evidence plan has a new column: "What we will do if this assumption fails".** Each assumption now comes with a planned response, not only a way to test it.
3. **The pathway is always a Mermaid diagram plus a plain-text reading.** Mermaid is a text format that many tools draw as a flowchart. One plain sentence reads the main pathway, for viewers that do not show diagrams.
4. **Backlash from male gatekeepers is handled.** Where fathers, husbands or leaders hold power over women and girls, the skill names the backlash risk. It says how a programme activity reduces it. This appears in Step 4 and in section 6.
5. **Month-1 rapid power mapping.** When the power analysis cannot be answered from your input, the skill adds a named milestone, "Month 1: rapid power mapping", and lists it as a short-term precondition. The mapping asks who decides, who benefits, who can block the change and which voices are missing.

## How we tested it

We ran two rounds. Ane read each pair of outputs without knowing which was which.

- **Round 1 (10 October):** the first rewrite against the original. The rewrite won ("flows logically, comprehensive bibliography"). The original had plainer language and some useful extra assumption ideas.
- **Round 2 (11 October):** Ane asked for four improvements (items 2 to 5 above). The revised version against the original won ("comprehensive").
- **Colleague test:** on claude.ai, the draft skill ran when named in the chat, and passed.

One limit: each version ran once per round, so treat the comparison as a strong signal, not proof.

## What you need to do

1. In claude.ai, open Customize > Skills.
2. If you have an older `toc-builder` or `toc-builder-draft` installed, delete it.
3. Upload the new `toc-builder.zip`.
4. Ask for a Theory of Change as usual. If another skill answers instead, write "Use the toc-builder skill to ..." in your request. The `mel-discipline` skill names ToC work in its description and can fire first in a plain chat.

## Known limits

- One sentence in the gatekeeper-backlash guidance is exactly at the 25-word limit.
- The "Causal claim" column in the pathway table does not repeat the one-sentence rule.
- The skill gives no hint on quoting Mermaid labels that contain brackets or colons, which can break the diagram.
- The backlash example reads as a fact and carries no safety caveat. Adapt it to your context.
- The new backlash and month-1 mapping items have no matching "if this fails" row in the evidence plan.

A later version will add a branded Word output with the pathway drawn natively in Word.

---

Release record: `gasserane/personal-skills`, commit `983224d`. Test runs: `evals/toc-builder/runs/2026-10-10` (round 1) and `runs/2026-10-11` (round 2).
