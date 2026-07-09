---
name: check-deliverable
description: 'Run the qa-reviewer maker-checker gate against one finished text deliverable, without a full Ann orchestration. Use when Ane types "/check-deliverable <file>", or says "check this deliverable", "run the qa gate on this file", "qa-review this brief", "run qa-reviewer on this file", or wants a finished markdown brief checked against the full qa gate on its own. Spawns the existing qa-reviewer agent alone against a single markdown or text file, sets the audience tier (default Tier 1 / colleague; override with --tier 2 and --subgroup), and returns a BLUF verdict plus the full qa_block. Read-only: it rewrites nothing and writes nothing to disk. Not for producing a deliverable (use /ann), not for voice rewriting (use /ane-voice), not for code review (use /code-review). Refuses Office binaries (.docx/.xlsx/.pptx) because qa-reviewer cannot parse them.'
---

# /check-deliverable — standalone qa gate

Run the existing **qa-reviewer** agent against ONE finished text deliverable on demand, without a full Ann/Vi orchestration. Reuse qa-reviewer wholesale: add no new checking logic, rewrite nothing, write nothing to disk.

## Lane — when this skill, not another
- **/check-deliverable** (this): *checks* an existing finished file against the qa gate. One file, one qa-reviewer spawn.
- **/ann**: *produces* a deliverable through the full pipeline. Use when the goal is the artefact.
- **/ane-voice**: audits and rewrites prose voice. Use to fix tone, not to run the full gate.
- **/code-review**: reviews code diffs, not MEL prose deliverables.

## Arguments

`/check-deliverable <file> [--tier 1|2] [--subgroup colleague|ma-staff|partner-ngo|management|junior-mel|peer-review]`

- `<file>` (required): path to the deliverable.
- `--tier` (default `1`).
- `--subgroup` (default `colleague`).

Derive voice positioning from the subgroup:
- `management` to `directive`
- `junior-mel` to `collaborative-pedagogical`
- all other subgroups to `collaborative`

## Steps

1. **Validate the file.** Resolve the path. If the extension is not `.md`, `.txt`, or `.markdown`, STOP and return exactly this, then spawn nothing:

   > qa-reviewer can only inspect text. For Word, Excel, or PowerPoint deliverables run the full `/ann` pipeline so the brand and format checks apply.

2. **Spawn qa-reviewer** via the Agent tool with `subagent_type: "qa-reviewer"`. Pass this prompt, substituting the bracketed values:

   ```
   ## Standing instructions
   Audience tier: [Tier 1|Tier 2]; subgroup: [subgroup]; voice positioning: [positioning]

   ## Task
   Standalone single-file review. Review the deliverable at this path:
   [absolute file path]

   There is NO Ann plan, NO Definition-of-done criteria, and NO P1 wiki block.
   Cold-load the wiki per your session-start fallback (qa-block-schema.md,
   domain-standards.md, calibration.md) and omit the Definition-of-done subsection.
   Read and Grep the file directly to run every mandatory check (tier register,
   em-dash, citation, lens, power-shift, edge-case probe). Populate the qa_block,
   add reconciliation notes, and close with your VERDICT line.
   ```

3. **Reformat the result BLUF-first:**
   - Line 1: the verdict (`APPROVED` / `PASS_WITH_GAPS` / `REJECTED — reason`).
   - Then the load-bearing findings in plain prose: hard FAILs first, then gaps, then soft flags.
   - Then the full verbatim qa_block under a `### Full qa_block` heading.

   Reformat only. Never override, soften, or reinterpret a qa-reviewer finding.

## Boundaries
- One file, one qa-reviewer spawn. No reader-position-reviewer.
- No prose rewriting (that is `/ane-voice`).
- No writes to the deliverable or anywhere on disk.
