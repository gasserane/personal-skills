---
name: tech-proposal-review-general
description: "Use this skill whenever a user submits a technical and/or financial proposal from a vendor, developer, or consultancy for review — in any sector, organisation type, or country context. Triggers include: uploading a proposal document, asking to evaluate or assess a tech vendor submission, asking to score or critique a software development bid, asking what to look for in a tech proposal, or asking how to compare competing proposals. Also triggers for phrases like \"can you review this proposal\", \"help me evaluate this vendor\", \"is this a good deal\", \"what are the risks in this proposal\", or \"does this proposal cover everything it should\". The output format is always confirmed with the user before generating anything. Use in combination with the docx or xlsx skill if a formatted output is requested. Not for panel scoring workbooks (use selection-toolkit), checking an offer against an IPPF ToR (use procurement-offer-review), or scoring a proposal IPPF sends to a donor (use donor-proposal-scoring).\n"
---

# Tech Proposal Review Skill (General)

## Purpose

This skill helps users — including non-specialists — rigorously review technical and financial proposals from external vendors, developers, or consultants. It works across any sector, organisation type, or country context.

It surfaces risks, flags weak commitments, and produces a structured critique that supports an informed contracting decision. The calibration questions at the start adapt the review to the specific context rather than applying a one-size template.

---

## Step 0: Single vendor or multi-vendor comparison?

Before anything else, ask:

> "Are you reviewing one proposal, or comparing two or more proposals from different vendors?"

**If one vendor → go to Section A (Single Vendor Review).**
**If two or more vendors → go to Section B (Multi-Vendor Comparison).**

---

## Section A: Single Vendor Review

### Step A0: Confirm output format

Before beginning, ask:

> "What format would you like the output in? Options: (1) inline analysis in chat, (2) structured Word document, (3) scored scorecard in Excel, or (4) something else — tell me."

Wait for the answer. Then proceed.

If they choose Word → apply the docx skill.
If they choose Excel → apply the xlsx skill.
If they choose inline → write the review directly using the structure below.

---

### Step A1: Gather context — four calibration questions

Ask these before reading the proposal. They determine how to weight the review dimensions.

1. **What does your organisation do, and what is this tool or service for?** (One sentence each is enough.)
2. **Does this contract involve personal data — data about identifiable individuals?** (Yes / No / Unsure — if unsure, treat as yes.)
3. **Is this funded by a donor, grant, or restricted fund — or by core/unrestricted budget?** (Affects what needs to appear in the contract.)
4. **What is the approximate contract value, and in what currency?** (Calibrates what insurance and liability levels are proportionate.)

Wait for answers before proceeding. If the user cannot answer all four, proceed with what they know and flag assumptions explicitly in the review.

---

### Step A2: Read the proposal thoroughly

Read the full document before writing any output. Do not skim. Note:

- What the vendor claims they will deliver
- What they do not address (gaps are as important as what is present)
- Any language that is vague, conditional, or hedged ("may", "aims to", "subject to", "to be confirmed")
- Numbers: costs, timelines, team composition, licensing terms, support hours

---

### Step A3: Review across six dimensions

Assess each dimension and assign a rating: **Strong / Adequate / Weak / Missing**.

### 3.1 Technical Fit
Does the proposed solution match what the organisation actually needs?

Check:
- Does the architecture align with the stated technical requirements (hosting, authentication, data handling, integrations)?
- Is the technology stack appropriate, current, and maintainable by a typical in-house team?
- Does the proposal explain how the tool will be handed over and sustained after delivery?
- Are AI components (if any) explained — what model, what data, what human oversight?
- Is the proposal specific to this client's context, or does it read like a recycled template?

Flag: Generic architecture descriptions that could apply to any client. Missing handover or maintenance plan. AI components with no explanation of how they work or how outputs are validated.

### 3.2 Team and Capacity
Can this vendor actually deliver?

Check:
- Are named individuals specified, or only roles?
- Do CVs or track records match the complexity of the work?
- Is the team size realistic for the scope and timeline?
- Is there a named technical lead and a named project manager?
- What happens if a key person leaves mid-project?

Flag: Proposals where the impressive person presents but unnamed junior staff deliver. Single-person shops without succession or risk coverage. No mention of subcontractors when the scope implies one team cannot do it all.

### 3.3 Deliverables and Milestones
Is it clear what will be produced, by when, and to what standard?

Check:
- Are deliverables specific named outputs (not activities)?
- Does the timeline account for review and feedback cycles from the client?
- Are milestones tied to payment? (They should be.)
- Is there a definition of "done" or acceptance criteria for each deliverable?
- Are there provisions for what happens if milestones are missed?

Flag: Milestone-free timelines. Payment schedules front-loaded to the vendor. Deliverables described as activities ("will conduct workshops") rather than outputs ("will deliver a validated training module").

### 3.4 IP, Licensing, and Data
Who owns what, and what are the long-term implications?

Check:
- Who owns the IP of all outputs (code, documentation, data models, training data)?
- If the vendor retains IP, what licence does the client receive? Is it perpetual? Can the client modify the tool?
- Are there open-source components? What are their licences (and do any restrict commercial or organisational use)?
- How is client data handled — where is it stored, who can access it, what are the deletion terms?
- If personal data is involved (per Step 1): does the proposal reference data protection obligations?

Flag: "Vendor retains all IP" with no licence grant. SaaS tools where client data sits on vendor servers with no data processing terms. "IP assigned to client" language that contains a pre-existing materials carve-out broad enough to nullify the assignment. Silence on open-source licensing.

### 3.5 Cost Structure and Value
Is the financial proposal transparent, proportionate, and correctly scoped?

Check:
- Is the cost breakdown itemised (by phase, role, or deliverable)?
- Are rates explicit and reasonable for the market and team seniority?
- Are ongoing costs identified — hosting, licences, API fees, maintenance, future updates?
- What is explicitly excluded? (Exclusions matter as much as inclusions.)
- Is VAT or applicable tax addressed?
- Is the currency and invoicing method clear?

Flag: Lump-sum proposals with no breakdown. "Ongoing costs TBD." Proposals that ignore post-delivery operational spend entirely. Hidden costs buried in vague "additional services" language.

### 3.6 Risk and Governance
What can go wrong, and is there a plan?

Check:
- Does the proposal identify risks and mitigations?
- What is the change request / variation process?
- What are the termination provisions?
- What warranties are offered on deliverables?
- What liability limits apply?
- Is there professional indemnity or cyber insurance?

Flag: No mention of risk. No change request process. Liability limited to a fraction of contract value with no carve-outs for serious breaches. No warranty period after delivery.

---

### Step A4: Produce the issue log

List all concerns using three tiers:

**Blocker** — Must be resolved before contract signature. The proposal cannot proceed as written.
**Significant** — Requires negotiation or clarification. Not a dealbreaker, but creates real risk if unaddressed.
**Minor** — Worth flagging; can be addressed in the contract or by side agreement.

For each issue, state:
- What the problem is (one sentence)
- Why it matters
- What the client should request or require

---

### Step A5: Calibrated flags based on context

Apply these additional checks based on the calibration answers from Step 1.

**If personal data is involved:**
Flag any absence of: data processing agreement terms, sub-processor restrictions, breach notification provisions, and data deletion/return obligations. These are legal requirements under GDPR (EU/EEA) and equivalent frameworks elsewhere — not optional good practice.

**If donor/grant funded:**
Check whether the proposal or accompanying contract terms are consistent with the funder's IP requirements (some donors require open licensing or retain rights). Flag if the funding source is not named anywhere.

**If contract value is high (use judgment relative to context):**
Insurance minimums matter more. Professional indemnity should be proportionate to the contract value and the risk of errors. Cyber insurance is essential if personal or sensitive data is handled. Flag vague insurance language ("the vendor will maintain appropriate coverage") as unenforceable.

**If the tool handles sensitive data (health, political, financial, identity):**
Flag absence of: security standards reference (e.g. ISO 27001, OWASP), access controls, audit rights, and any restriction on the vendor deploying the same tool for parties hostile to the client's interests.

---

### Step A6: Overall assessment

Write a short paragraph (5–8 sentences) that states:
1. Whether the proposal is fundable/contractable as written
2. The one or two issues that most need resolution
3. What the proposal does well
4. A recommended next step (proceed, negotiate, reject, request resubmission)

---

## Tone and audience guidance

This skill is used by broad teams including non-specialists. Explain technical and legal concepts briefly on first use. Do not assume the reader knows what GDPR Article 28 means, what a liability cap is, or what open-source licensing implies — define on first use.

Write in active voice. Use specific verbs. Avoid hedging.

---

## Reference: common patterns that lead to contract problems

These patterns recur across real procurement reviews. Use them as calibration.

- "IP assigned to client" clauses frequently contain a carve-out for "pre-existing materials" — if this term is undefined and broad, it can nullify the entire assignment. Always check what pre-existing materials the vendor will bring and whether the carve-out is scoped.
- Timeline estimates for technical integrations (authentication, APIs, data pipelines) are routinely underestimated. Ask for evidence of prior delivery of similar integrations.
- "Hosting costs to be confirmed" is a red flag. Cloud infrastructure costs are estimable. The vendor should provide a range at proposal stage.
- Proposals from small consultancies often feature a senior lead in the pitch but deliver via unnamed junior staff or subcontractors. Ask explicitly who will do the work day-to-day.
- Insurance language that says "the vendor will maintain appropriate insurance" is effectively unenforceable. Require specific minimum values and the right to request certificates.
- Ongoing operational costs (hosting, API fees, maintenance) are frequently absent from proposals. A tool that costs €20K to build may cost €5K–€10K per year to run. This must be budgeted.
- Silence on what happens at contract end — to data, code, access credentials, and documentation — is a governance risk. The proposal should address exit explicitly.

---

## Section B: Multi-Vendor Comparison

Use this mode when the user has two or more proposals to compare and must select one vendor.

### Step B0: Confirm output format

Ask the user:

> "What format would you like the comparison in? Options: (1) comparative table with narrative inline in chat, (2) Word document with scoring matrix and recommendation, (3) Excel scorecard with weighted scores per vendor, or (4) something else — tell me."

If they choose Word → apply the docx skill.
If they choose Excel → apply the xlsx skill.
If they choose inline → write the comparison directly using the structure below.

---

### Step B1: Establish the evaluation baseline

Before reading any proposal, ask:

> "Are all vendors responding to the same brief or specification? If yes, I will hold them to the same standard. If no, tell me what each vendor was asked to deliver — I will adjust the comparison accordingly."

Also confirm the four calibration questions from Step A1 (organisation context, personal data, funding source, contract value) — these apply equally to the comparison.

Confirm vendor names upfront so the comparison is labelled consistently throughout.

---

### Step B2: Read all proposals before scoring anything

Read every proposal in full before producing any output. Do not score vendor A before reading vendor B — early scores anchor judgement and bias the comparison. Note, per vendor:

- What they claim they will deliver
- What they do not address
- Hedged or conditional language
- All numbers: costs, timelines, team size, licensing terms

---

### Step B3: Score each vendor across six dimensions

Use a 1–5 scale per dimension. Apply the same criteria as Section A Step A3.

| Dimension | Vendor A | Vendor B | Vendor C (if applicable) |
|---|---|---|---|
| 1. Technical fit | /5 | /5 | /5 |
| 2. Team and capacity | /5 | /5 | /5 |
| 3. Deliverables and milestones | /5 | /5 | /5 |
| 4. IP, licensing, and data | /5 | /5 | /5 |
| 5. Cost structure and value | /5 | /5 | /5 |
| 6. Risk and governance | /5 | /5 | /5 |
| **Total /30** | | | |

For each score, write one sentence of justification. Do not assign scores without justification — the reasoning is the value, not the number.

If the user signals that certain dimensions matter more (e.g. "IP is critical for us" or "we have a fixed budget"), apply weighting before totalling. State the weights explicitly so the user can challenge them.

Apply the calibrated flags from Step A5 conditionally — if personal data is involved, weight dimension 4 (IP, licensing, and data) more heavily in any weighting exercise.

---

### Step B4: Comparative flags

After scoring, identify the three most consequential differences between vendors. These are the dimensions where the choice actually matters — not marginal differences, but structurally significant ones. For each, state:

- What the difference is
- Which vendor has the stronger position
- What risk the weaker position creates if that vendor is selected

---

### Step B5: Blockers check

Apply the blocker criteria from Step A4 to each vendor. A vendor with a blocker issue is not contractable as proposed, regardless of their score. Flag this explicitly:

> "Vendor X has a blocker issue on [dimension]. Even if they score highest overall, this must be resolved before a contract can be signed."

---

### Step B6: Recommendation

State a clear recommendation in the first sentence. Do not hedge. Then explain:

1. Why the recommended vendor is the stronger choice
2. What conditions or negotiations should accompany the selection
3. Whether any runner-up vendor should be kept as a contingency
4. What the recommended next step is (e.g. request clarification on issue X, then proceed to contract)

If no vendor is contractable as proposed, say so directly and state what each would need to fix before resubmission.

