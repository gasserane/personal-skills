# The two modes, and what actually differs

One weighted scoring engine, two modes. The arithmetic is identical. What changes
is what the source is, what may be left unstated, and what the workbook is for.

## `procurement`

The published award criteria of an open-market procurement, matching the ToR
exactly. This is the strict mode, and the strictness is the point: an award that
cannot show where each weight came from is an award that can be challenged.

Refused unless stated:

| Field | Why it cannot be defaulted |
|---|---|
| `source` | Without it the workbook cannot say which document the criteria came from, and the audit trail for "why is this worth 35" disappears |
| `criteria` with real `max_points` | A blank weight scores every proposal identically and still reads as a criterion |
| `threshold` | The single number deciding who stays in the process |
| `financial_max` when a financial stage exists | A financial stage worth no points is a stage that does nothing |
| `panel` of 2 or more | Independent scoring is the control; one scorer removes it |

If the ToR genuinely sets no threshold, say so explicitly by setting one at 0
rather than leaving it null, and record why in `notes`.

## `appraisal`

Generic multi-criteria decision analysis: an options paper, a tool or vendor
comparison, a value-for-money assessment. Reference runs, both built ad hoc
before this skill existed: the Claude vs Copilot platform evaluation
(2026-06-26) and the value-for-money 4Es rubric for ROM MA accreditation
(2026-06-22).

What relaxes:

- **`threshold` may be null.** An appraisal usually ranks rather than qualifies.
  With no threshold the workbook reports "Scored" instead of "Qualified".
- **A single appraiser is allowed.** One person comparing four tools is a real
  appraisal. One person awarding a contract is not, which is why procurement
  mode refuses it.
- **No financial stage is normal.** Drop `financial` from `stages` and the sheet
  is not written at all.

What does not relax: every criterion still needs a stated weight, and `source`
still has to name where the criteria came from — a decision memo, a meeting, a
framework. "We agreed these in the 12 June team meeting" is a source. Nothing is
a source is not.

Set `subject_label` to what is being compared: `"Option"`, `"Tool"`, `"Vendor"`,
`"Supplier"`. It renames every column and note in both workbooks.

## The hard gate

`gates` are pass-or-fail statements that exclude regardless of score — a
do-no-harm or safeguarding requirement, a mandatory certification, a data
protection condition. They sit beside the compliance checks on `05 Stage 1` and a
single failure excludes.

Keep them out of `criteria`. A gate scored as a weighted criterion can be
outweighed by a strong technical proposal, which is precisely what a gate exists
to prevent. If it can be traded off, it is a criterion; if it cannot, it is a
gate.

## Choosing a spread trigger

`spread_trigger` is the point difference across the panel that means the panel
read the same submission differently. The default of 15 came from a 90-point
technical scale. Scale it: roughly one sixth of `technical_max` is a reasonable
starting point, and lower it if the panel is large or new to each other.

It is a discussion prompt, not a rule. Nothing is excluded or recomputed on a
wide spread; the cell shades and the panel talks.
