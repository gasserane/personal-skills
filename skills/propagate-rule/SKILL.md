---
name: propagate-rule
description: Fan out a governance rule from anework-package's single canonical source to all downstream surfaces. Use when Ane types /propagate-rule, or asks to "propagate a rule", "add a standing rule everywhere", "sync the governance rule", "update a cross-surface rule", or "change a rule on all surfaces".
---

# Propagate Rule

Governance rules live once, in `governance-rules.md` at the anework-package repo root. This skill walks through every step to push a rule change or addition to all downstream surfaces without drift.

## Step 1 — Edit the canonical source

Open `governance-rules.md` in the anework-package repo root. Each standing rule sits between a pair of HTML comment markers:

```
<!-- governance:<id>:start -->
...rule text...
<!-- governance:<id>:end -->
```

To **change** a rule: edit only the content between the existing markers for that `<id>`. Do not move or reformat the markers.

To **add a brand-new rule**: append a new `## <id>` section with a new marker pair. Then manually add the matching empty marker pair into each in-repo target (`CLAUDE.md` and `mel-framework-reference.md`) once — the sync script only fills regions whose markers already exist.

## Step 2 — Run the sync script

```
python sync_governance_rules.py
```

The script injects each canonical region into the in-repo targets (`CLAUDE.md` and `mel-framework-reference.md`) and refreshes the claude.ai mirror under `claude-ai-shareable-export/`. Verify the diff looks as expected before proceeding.

## Step 3 — Run the test harness

```
python tests/run_tests.py
```

The check `check_governance_rules_sync` fails if any surface drifts from the canonical text. Do not proceed until the full harness passes.

## Step 4 — Update the two manual surfaces

The sync script cannot reach these surfaces from a normal session. They require manual action.

**a. gasserane/claude-config (user-level laptop copy)**

Copy the updated marked region into the matching region of `CLAUDE.md` in the `gasserane/claude-config` repo. Open a pull request. Once merged, `restore-to-local.sh` carries the change to `~/.claude/CLAUDE.md`.

**b. claude.ai project knowledge**

Re-paste the full `mel-framework-reference.md` into the claude.ai Project (chat, Desktop, and cowork surfaces). Use `claude-ai-shareable-export/VERSION.txt` to confirm you are pasting from the current source commit and timestamp, not a stale export.

## Reminder

`gasserane/claude-config` and the claude.ai project knowledge cannot be written automatically from a normal session. Both require either a manual paste or a repo-scoped session with the relevant credentials. Do not mark the propagation complete until both are done.
