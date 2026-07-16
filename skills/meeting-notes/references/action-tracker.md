# Centralised action tracker

One Excel workbook collects every action, decision and pending item from all meeting notes, so Ane tracks execution in one place instead of reopening individual notes. Default location: `C:/Users/AGasser/OneDrive/1. Ane's PROJECTS/Ane Plans/Meeting actions tracker.xlsx`.

## When to update it

After ANY note is confirmed and written (dictation, handwritten, transcript modes), run the bundled updater as the last step:

```
python <skill>/scripts/update_tracker.py --note "<the new note .md>" --workbook "<tracker .xlsx>"
```

Prep mode reads the tracker first: the Status column is Ane's live progress record and beats the older note text for the status pass pre-fill.

## Workbook layout

- **Guide** tab: how to use it, which columns are Ane's to edit, status meanings (the plain-language rule: every workbook explains itself).
- **One tab per person**: that person's actions. Ane's tab is what she owes; another person's tab is her chase list with them. Columns: ID, Added, Meeting date, Counterpart, Topic, Action, Deadline, Status (drop-down: Open / In progress / Blocked / Done / Dropped), Progress notes, Last updated.
- **Decisions** tab: the decision log across all meetings (ID, Meeting date, Counterpart, Topic, Decision, Notes). Citable: "see decision 2026-07-16-T3-...".
- **Pending** tab: open and parked items with their resurface trigger and a Watching / Closed status.

## Ownership rules (why the updater only appends)

The workbook is Ane's working file: she edits Status, Progress notes and Notes by hand, possibly daily. The updater therefore NEVER modifies an existing row; it only appends rows whose stable ID (meeting date + topic + text hash) is not yet present. Re-running it on the same note is safe and adds nothing. This is the edit-preservation protocol applied to Excel: her manual state survives every update.

If a note is later corrected (an action reworded), the updater will add the reworded action as a new row; mark the old row Dropped with a note rather than deleting it, so history stays audit-able.

## Parsing contract

The updater parses the canonical note template from SKILL.md: the `## Next actions at a glance` person tables (Deadline | Topic | Action), per-topic `### Decisions` numbered items, and `### Open / parked` bullets. Notes that deviate from the template parse partially; the updater prints what it added, so check the count line and fill genuine gaps by hand or fix the note structure.
