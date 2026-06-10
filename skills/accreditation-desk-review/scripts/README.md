# deskreview.py — toolkit usage

The model does the judgement; this script does the Word document reliably. Always run with
`PYTHONUTF8=1` (Romanian/French diacritics). Needs `python-docx`, `pypdf`, `openpyxl`.

## Typical run

```bash
# 1. See what is in the template (content-based; survives Word table merges)
python deskreview.py locate "DRAFT Desk-review MA.docx"

# 2. Extract evidence to text + a manifest that flags scans/binaries as data gaps
python deskreview.py extract "Evidence MA/" "work/evidence_txt/"

# 3. Author judgement as conclusions.json (see schema below), then write it in.
#    'apply' backs up first and refuses if the file is open in Word.
python deskreview.py apply "DRAFT Desk-review MA.docx" conclusions.json --mode insert --tag P3
#    On a second pass over cells you already wrote, use --mode replace (removes the old
#    REVIEWER CONCLUSIONS block, keeps the MA text, writes the new block).

# 4. Verify every targeted cell has exactly one block (content-based, not lxml id)
python deskreview.py verify "DRAFT Desk-review MA.docx" conclusions.json

# 5. Companion outputs
python deskreview.py standalone "DRAFT Desk-review MA.docx" conclusions.json "PRINCIPLE 3 MA.docx" --principles 3
python deskreview.py interview interview_items.json "Pre-interview + interview questions MA.docx"
```

## conclusions.json

```json
{
  "STD": {
    "3.1": {"status": "Met - with a monitoring gap",
            "body": ["First synthesis paragraph...", "Second paragraph..."],
            "questions": ["Question one?", "Question two?"]}
  },
  "CHK": {
    "3.1.1": {"status": "Met",
              "body": "The MA reports X (self-assessment). Reviewer: Y.",
              "questions": ["Confirm Z."]}
  }
}
```

- `STD` keys are standard ids (`3.1`); the block lands in that standard's DESCRIPTION cell.
- `CHK` keys are check numbers (`3.1.1`); the block lands in that check's Evidence cell.
- `body` may be a string or a list of paragraphs.
- Only refs present in the template are written; `apply` reports any it could not locate.

## interview_items.json

```json
{
  "title": "MA ARV — pre-interview requests + interview questions",
  "pre_interview": [
    {"principle": "Principle 4 — Transparent and Accountable"},
    {"ref": "4.1.4", "type": "CL", "item": "Provide the Donor Accountability policy (not in the package)."}
  ],
  "interview": [
    {"principle": "Principle 5 — Well Managed"},
    {"ref": "5.2", "type": "NC", "item": "Agree a time-bound plan for the IT-security fixes.", "to": "ED / Board"}
  ]
}
```

`type` is `NC` (non-compliance/gap) or `CL` (clarification). Rows with a `principle` key render
as a banner; other rows render as table rows.

## Why each guard exists

See `../references/reliability-playbook.md`. Short version: Word merges tables on save (locate by
content), lxml `id()` is unreliable (verify by content), scans/`.doc`/images cannot be read (data
gaps), and a write to a Word-locked file fails (lock check + backup before every edit).
