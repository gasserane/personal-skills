# IPPF ARV — principles, standards, vocabulary, template anatomy

Authoritative source for the live cycle: **IPPF EN Internal Guidelines (Cycle 4 ARV,
2023-2026)** — read the actual guideline document for the exact check wording and any
cycle-specific scoring rules. This file is a working map, not a substitute. Verify against the
guideline each review; cycles change.

## The 10 accreditation principles

1. **Open and Democratic** — civil society status, volunteer involvement, non-discrimination,
   conditions of membership, governing-body rotation.
2. **Well Governed** — governing-body diversity, integrity, strategy/policy, appointment and
   evaluation of the Executive Director, oversight, body review and renewal.
3. **Strategic and Progressive** — strategic plan, promotion of SRHR.
4. **Transparent and Accountable** — accountability to donors, accountability to stakeholders.
5. **Well Managed** — effective management, risk management.
6. **Financially Healthy** — financial regulations, accounting systems, audit, sustainability.
7. **Good Employer** — recruitment, HR policies, treatment of staff.
8. **Committed to Results** — monitoring and evaluation, use of data.
9. **Committed to Quality** — access to services, providers' rights and needs, monitoring
   quality, supply management, inclusivity of services.
10. **A Leading SRHR Organization** — influencing agenda, collaborative partnerships.

Standards sit under each principle (e.g. 1.1–1.5); checks sit under each standard
(e.g. 1.2.1–1.2.4). The desk-review template usually includes only a curated subset of checks
per standard — comment only on the checks that are present.

## Compliance / status vocabulary

The ARV form uses these MA verdicts in the answer column: **Yes**, **No**,
**More information needed**, **Not Applicable**, **Non-Compliance with Justification**.

Mirror them in your reviewer status label, but be more granular so the interview team can
triage:

| Reviewer status | Use when |
|---|---|
| `Met` | Evidence substantiates the check; no concern. |
| `Met - <minor qualifier>` | Met, but a small development point (e.g. `Met - minor development`, `Met - practice-based`). |
| `Partially met - clarify at interview` | Some elements evidenced, others not; the MA itself often flags this. |
| `Not met - area for development` | A genuine gap; the standard is not satisfied. |
| `More information needed at interview` | Cannot judge on desk evidence; need confirmation. |
| `Non-compliance with justification` | Standard not met but the MA gives a credible reason / remediation. |
| `Not applicable` / `Applicability to confirm` | Out of scope — but test the basis; do not accept N/A at face value, especially in Principle 9. |

Leave the MA's own answer-column verdict untouched; your view lives in the reviewer block.
If the evidence contradicts the MA verdict, say so and explain — do not silently overwrite.

## Desk-review template anatomy

Each standard block is a table (or part of a merged table) running:

```
Standard X.Y   <title>                         <- header row (use to set "current standard")
<standard description …> Is the Association considered to comply with this Standard? <verdict>   <- DESCRIPTION cell (standard-level conclusion goes here)
Comment Type | Description
MA Comment   | <MA's standard-level note>
Check        | … | Evidence                    <- column header row
X.Y.1 | <check question> | <Yes/No/…> | <MA evidence text>   <- check rows
X.Y.2 | …
```

- **Evidence column = the last (merged) column** of a check row → check-level conclusion.
- **Standard DESCRIPTION cell** = the cell containing "comply with this Standard" → the
  elaborated standard-level conclusion (the IPPF reader reads only this).
- Checks for one standard can spill across table boundaries after Word merges tables, so always
  locate by content (`deskreview.py locate`), never by fixed table/row index.

## Two-reviewer split

Reviews are typically divided between two reviewers (e.g. one takes principles 2, 6, 7, 10; the
other takes 1, 3, 4, 5, 8, 9). Earlier reviewer comments may already sit in some cells (look for
initials such as "RT"). Add your layer below; never delete another reviewer's text.

## Lenses

Apply the feminist, decolonial, intersectional and participatory lenses substantively, not as
labels: whose voices shaped the strategy; whether a "marginalised groups" strategy reaches
disability and LGBTQI people or only names them; whether youth participation is co-design or
consultation; whether the service model centres the most excluded. Keep the signposting
invisible in the working-brief prose; the analysis does the work.
