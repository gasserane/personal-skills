---
name: srhr-map
description: SRHR interactive map skill (pilot). Refresh mode turns new internal drop-in files into a short review workbook, then writes a colleague's answers into a new map register edition. Publish mode arrives in a later phase. Call by name only.
disable-model-invocation: true
---

# SRHR interactive map skill (pilot)

This skill keeps the SRHR interactive map's data up to date. It has two modes:

- **Refresh** (ready): new files come in, a person checks what changed, and the answers go into a new edition of the map register.
- **Publish** (not ready yet, phase d): the map itself is rebuilt from an approved register edition. If someone asks to publish, say it is not ready yet and stop.

**What this folder must never hold.** This repository is public. No register rows, organisation or country names, fund names, amounts, codes, or local file paths. The register, the drop-in files and the two config tables live in the organisation's own "SRHR map data" folder, never here.

## Before you start

You need the path to the "SRHR map data" folder. If the person has not given it and `SRHR_MAP_ROOT` is not set, ask: "Where is the SRHR map data folder?" Do not guess a path.

The folder holds:

- `drop_in/<reporting year>/`: the new files, one subfolder each: `dhis2/` (service statistics export), `subgranting/` (grant ledger), `business_plans/` (business-plan focus coding sheet).
- `intelligence_tool/`: the latest Intelligence Tool snapshot, `master_countries.csv`, and optionally `source_register.csv`.
- `config/`: `streams.csv` (grant stream names and legend labels) and `ma_codes.csv` (organisation codes, ticked by the map owner). Optional: `country_aliases.csv` (ledger spellings of a country) and `stream_overrides.csv` (for one country and one edition, show a ledger stream as a different map stream). Only rows the map owner ticked are used; an override row counts only for its own edition.
- `map_register/`: one register file per map edition. An existing edition is never changed.
- `review/`: the review workbooks and run files this skill writes.

The scripts are in this skill's `scripts/` folder. Every command takes `--map-root <folder>` (or uses `SRHR_MAP_ROOT`) and `--year <reporting year>`. The edition built is the next year unless `--edition` says otherwise.
On Windows, give `--map-root`, `SRHR_MAP_ROOT` and `SRHR_MASTER_COUNTRIES` as Windows paths with a drive letter, not `/c/...`. Python does not read a Git Bash `/c/...` path in an environment variable, so the tests' `public_repo_clean` check then fails with "not set or not found".

## Refresh mode, for a colleague

1. **See what files are needed.** Run `python refresh.py list --year <year>`. It names each file expected in `drop_in/<year>/` and says which are already there. Ask the person to put any missing file there.
2. **Check the files.** Run `python refresh.py check --year <year>`. If a file does not match its contract, the command stops with one line starting `Stopped:`. Read that line to the person in plain words, ask them to fix or replace the file, and run check again. Never edit a drop-in file yourself.
3. **Make the review workbook.** Run `python refresh.py review --year <year>`. It prints the path of a workbook in `review/`. Tell the person how many lines are on "Must check" and pass on every `note:` line (for example an organisation code nobody has ticked yet).
4. **The person answers.** They open the workbook, type their name and the date on "How to use", and for each line on "Must check" open the link, compare, and choose Correct, Wrong (with the right value) or Not sure. They save the file. A line that stands for several values takes Correct or Not sure only: Wrong there leaves them unanswered, because one right value cannot fit each of them.
5. **Write the answers.** Run `python refresh.py apply --year <year> --workbook <path>`. A line starting `Refused` or `Stopped` means nothing was written: say why and what to fix (often the name or date cell is empty, or the file is open in Excel). A workbook from an earlier review is refused once review has run again for its topic: ask the person to answer the newest workbook. Otherwise report how many rows were ticked and how many still need a tick.
6. **Approval (map owner only).** Run `python refresh.py approve --year <year> --by "<name>"`. It refuses while any change still needs a person's tick and lists those changes.

Rules that hold in every step:

- A person ticks every change. Never write a tick, a name or a date into the register yourself.
- Never open an existing register edition for writing. `apply` writes the new edition and backs it up before any rewrite.
- Use `--topic HIV` or `--topic funding` to refresh one topic only.
- Refresh never adds a country to the map. A country in the new files with no row in the last edition is listed as a note; adding it is a publish decision for the map owner.

## Where refresh runs: Claude Code

Refresh runs in Claude Code, not Cowork: Cowork could not open the synced "SRHR map data" folder. Start Claude Code from your usual work folder, never from inside "SRHR map data", and pass `--map-root` to every command.

The review workbook gets the full IPPF brand (logo, header and footer) when the organisation's reporting package is found: set `WORK_FOLDER_ROOT` to the work folder, or run from inside it. Without that package, the workbook uses the brand colours and font without the logo.

## Other scripts here

- `dropin_check.py`: checks one drop-in file against its contract (used by `check`).
- `derive_rows.py`, `compare_register.py`, `review_workbook.py`, `apply_answers.py`: the steps `refresh.py` chains.
- `config_tables.py`: reads and validates the two config tables.
- `register_deck_check.py`: compares a register edition with the published map decks.
- `shared/srhr_data_contract.v1.json`: a byte-identical copy of the data contract shared with the SRHR Intelligence Tool. Never edit it here.
- `contracts/`: one contract per drop-in file. They name columns and rules only.
