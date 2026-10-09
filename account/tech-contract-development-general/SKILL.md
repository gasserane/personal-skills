---
name: tech-contract-development-general
description: "Use this skill whenever a user needs to draft, review, redline, or finalise a technology services contract, software development agreement, or digital consultancy agreement — in any sector, organisation type, or country context. Triggers include: uploading a contract for review, asking to draft a contract from scratch, asking to check or fix contract clauses, asking about IP ownership in tech contracts, asking about data protection obligations in vendor agreements, asking what a tech contract should contain, or asking to prepare a data processing agreement (DPA). Also triggers for phrases like \"help me build this contract\", \"can you redline this\", \"what's missing from this agreement\", \"is this clause OK\", \"how do I handle IP\", or \"we need to contract a developer\". Always start with the decision branch to determine mode. Use with the docx skill when a Word output is required. Not for the ToR or RFP (use rfp-digital-services) or offer review (use tech-proposal-review-general).\n"
---

# Tech Contract Development Skill (General)

## Purpose

This skill guides users through building or reviewing technology services contracts. It is designed for non-lawyers who need to produce legally sound, practically enforceable agreements with external developers, software vendors, or technology consultants.

It works across any sector, organisation type, or country context. The calibration questions at the start adapt the contract structure and emphasis to the specific situation.

It covers two modes: drafting a new contract from scratch, and reviewing and redlining an existing draft.

---

## Step 0: Decision branch — which mode?

Ask the user:

> "Are you (A) drafting a new contract from scratch, or (B) reviewing and improving an existing draft?"

If A → go to Section 1: Drafting Mode.
If B → go to Section 2: Review and Redline Mode.

If the user is unsure: "Do you have a document already, or are you starting from a blank page?" Then route.

---

## Section 1: Drafting Mode

### 1.1 Gather context before drafting

Ask these questions before writing any contract text. You can ask them all at once.

1. Who are the two parties? (Full legal names, registration numbers if known, country of registration)
2. What is the vendor being contracted to deliver? (Software, data tool, platform, website, advisory service — be specific)
3. Who will own the IP in the outputs? (Client, vendor, or shared — if unsure, the default should be client)
4. What data will the vendor handle? Does it include personal data about identifiable individuals?
5. What is the approximate contract value and currency?
6. What country's law should govern the contract? (Default: the client organisation's country of registration)
7. Is there a funding source that must be named? (Donors, grants, or restricted funds often require explicit citation)
8. What is the expected duration?
9. Is there a dispute resolution body or arbitration institution the organisation normally uses? (If not, we will recommend one appropriate to the governing law)

Wait for answers. Do not draft until you have at least items 1, 2, 3, and 5. Flag any gaps explicitly in the draft.

---

### 1.2 Adapt the contract to jurisdiction

Before drafting, note the governing law from question 6 and flag the following jurisdiction-specific considerations:

**EU / EEA (including Belgium, France, Netherlands, etc.):**
- GDPR Article 28 compliance is mandatory if personal data is processed. Include a full DPA.
- Non-compete clauses for service providers (not employees) must be reasonable in scope, duration, and geography to be enforceable. Absolute prohibitions are void in most EU jurisdictions.
- Standard arbitration bodies: CEPANI (Belgium), ICC (international), DIS (Germany), LCIA (UK/international).

**UK:**
- UK GDPR applies post-Brexit. Obligations are substantively identical to EU GDPR.
- Non-competes are enforceable if reasonable. Courts will blue-pencil (narrow) but not rewrite.
- Standard arbitration: LCIA or ICC.

**US:**
- Data protection varies by state (CCPA in California; others emerging). Flag applicable state law.
- Non-competes are banned or heavily restricted in California, Minnesota, and others. Check state law before drafting.
- Standard arbitration: AAA or JAMS.

**Other jurisdictions:**
- Identify whether a data protection law exists and cite it. If none, apply the principle of data minimisation and breach notification as good practice.
- Identify whether non-competes are enforceable under local law before including them.

If governing law is unclear or cross-border, recommend the client takes legal advice before signature. Flag this explicitly.

---

### 1.3 Standard clause architecture

Every technology services contract must include these sections. Do not omit any.

**1. Parties** — Full legal names, registration details, addresses, roles (Client / Service Provider).

**2. Recitals / Background** — Brief statement of purpose. If the work is funded by a named grant or donor, state this here.

**3. Definitions** — Define all capitalised terms. Ambiguity in definitions is the primary source of contract disputes.

**4. Scope of Services** — What the vendor will deliver. Be specific. Reference a Schedule or Annex for detailed deliverables rather than embedding them in the body.

**5. Deliverables and Milestones** — Named outputs, delivery dates, acceptance criteria, number of revision rounds, and consequences of missed milestones.

**6. Fees and Payment** — Total contract value, payment schedule (linked to milestones, not time alone), currency, invoicing procedure, late payment consequences, VAT/tax treatment.

**7. Intellectual Property** — Who owns:
- (a) outputs created under this contract
- (b) pre-existing materials the vendor brings in (define these explicitly)
- (c) modifications to pre-existing materials

If IP is assigned to the client, the clause must use the word "assigns" not "licenses." If the vendor retains pre-existing IP, the client must receive a perpetual, royalty-free, irrevocable licence to use it as embedded in the deliverables.

**8. Data Protection** — If personal data is involved:
- In the EU/EEA/UK: include a full GDPR Article 28-compliant DPA, either in the body or as an annex.
- Minimum content of the DPA: purpose limitation, data subject rights procedure, sub-processor restrictions, security obligations, breach notification timeline (72 hours to notify client; client then notifies regulator within 72 hours), deletion/return on termination.
- In other jurisdictions: include equivalent obligations as a matter of good practice, citing applicable local law where it exists.

**9. Confidentiality** — Mutual or asymmetric; duration (typically 3–5 years post-termination); carve-outs for public domain, pre-existing knowledge, and legal compulsion.

**10. Restrictions on Deployment (if applicable)** — If the tool is sensitive (handles personal data, serves a specific beneficiary group, or could cause harm if deployed for hostile parties), include a clause restricting the vendor from deploying the same or substantially similar tool for competitors or hostile parties. Scope by time, geography, and nature of use to maximise enforceability under governing law.

**11. Term and Termination** — Start date, end date, termination for cause (with cure period), termination for convenience (with notice and payment for work completed to date). State what happens to data, deliverables, and access credentials on exit.

**12. Warranties** — Vendor warrants that: deliverables conform to specification; vendor has the right to assign IP; work does not infringe third-party rights; deliverables are free from material defects for a defined period after delivery (minimum 3 months; 6–12 months recommended for complex systems).

**13. Liability** — Cap on total liability: typically 100–200% of contract value. Carve-outs (uncapped) for: IP infringement, data protection breaches, fraud, wilful misconduct, and death/personal injury.

**14. Insurance** — Specify minimum coverage proportionate to contract value and data sensitivity:
- Professional indemnity: at minimum equivalent to the contract value; for complex or high-risk work, 2–3× contract value.
- Cyber insurance: required if vendor handles personal or sensitive data.
- Require proof (certificate) on request.

**15. Dispute Resolution** — Governing law, jurisdiction, escalation path (negotiation → mediation → arbitration/litigation). Name the arbitration body if arbitration is included. State the language of proceedings.

**16. General Provisions** — Entire agreement, severability, no waiver, amendment procedure (written only, signed by both parties), notices, force majeure.

**17. Schedules / Annexes** — Deliverables list, milestone/payment table, DPA (if separate), technical specifications, any applicable ethics or governance protocol.

---

### 1.4 Funding source discipline

If the contract is grant- or donor-funded:

- Name the funding source in the Recitals.
- Do not condition payment on funder approval in the payment clause — this creates an unintended tripartite obligation.
- Check whether the funder's grant agreement imposes IP requirements (open licensing, funder ownership, public access). Ensure the contract's IP clause is consistent.

---

### 1.5 Source code and repository access

If the deliverable includes software:

- Specify who holds admin rights to the code repository (e.g. GitHub, GitLab). The client should hold admin rights, with the vendor having contributor access.
- State what happens to the repository at contract end: transfer of admin rights, delivery of full codebase, or escrow.
- If the vendor uses a private repository, the client must have read access at all times during the contract.

---

## Section 2: Review and Redline Mode

### 2.1 Read the full document first

Do not begin commenting until you have read the entire contract. Many clause-level problems only become visible once you understand the document as a whole.

### 2.2 Ask four calibration questions

Before reviewing, ask the user:

1. What country's law governs this contract?
2. Does this contract involve personal data?
3. Is this donor- or grant-funded?
4. What is the approximate contract value and currency?

These answers determine which checks are mandatory vs. advisory.

### 2.3 Run the 20-point review checklist

For each item, state: **Present and adequate / Present but weak / Missing**.

**Parties and definitions**
- [ ] Both parties fully identified with legal names and registration details
- [ ] All capitalised terms defined and used consistently

**Scope and deliverables**
- [ ] Scope of services is specific, not generic
- [ ] Deliverables are named outputs with acceptance criteria
- [ ] Milestones exist and are linked to payment

**Financial**
- [ ] Total contract value stated in a specific currency
- [ ] Payment schedule linked to milestones, not time alone
- [ ] Invoicing procedure specified
- [ ] Ongoing/operational costs addressed or explicitly excluded

**IP**
- [ ] Ownership of outputs assigned or licensed — unambiguously
- [ ] Pre-existing IP defined and licensed to client for use within deliverables
- [ ] Deployment restrictions present (if applicable to the tool's sensitivity)
- [ ] Source code / repository access and transfer defined

**Data protection**
- [ ] Data protection obligations present and proportionate to governing law
- [ ] Sub-processor restrictions present (if personal data involved)
- [ ] Breach notification timeline stated (≤72 hours for GDPR-governed contracts)
- [ ] Data deletion/return on termination specified

**Risk and governance**
- [ ] Liability cap stated; uncapped carve-outs for IP, data, fraud, wilful misconduct
- [ ] Insurance minimums specified (not just "appropriate coverage")
- [ ] Termination for cause and convenience both present
- [ ] Dispute resolution clause with governing law, jurisdiction, and named body
- [ ] Exit provisions: data, deliverables, access credentials, repository transfer

### 2.4 Produce a tiered issue log

**Blocker** — Contract cannot be signed as written. State what must change and provide proposed replacement language.
**Significant** — Requires negotiation or redrafting before signature.
**Minor** — Recommended improvement; not a dealbreaker.

For each issue, state: the problem in one sentence, why it matters, and the specific change required. Provide redline language in this format:

> **Original:** [existing text]
> **Proposed:** [replacement text]
> **Reason:** [why this change matters]

### 2.5 Cross-reference integrity check

Before finalising:
- Verify every internal cross-reference points to a real and correctly numbered section.
- Verify every defined term is actually defined.
- Verify that payment amounts in the payment schedule match amounts stated in the body.
- Verify that schedule/annex titles match what is referenced in the body.

### 2.6 Blank fields check

Before flagging a contract as ready to sign, confirm no fields remain as placeholders:
- Party registration numbers
- Execution date
- Any version numbers or document references cited in the body (e.g. a referenced Data Ethics Protocol, security standard, or technical specification)

---

## Tone and output guidance

This skill serves broad teams including non-specialists. Define legal and technical concepts briefly on first use. Do not assume the reader knows what GDPR Article 28 requires, what a liability cap means, or how open-source licences work.

Use active voice throughout. If the user requests a Word document, apply the docx skill.

---

## Reference: common patterns that lead to contract problems

These patterns recur across real technology contract reviews across sectors.

- "IP assigned to client" with an undefined pre-existing materials carve-out can nullify the entire assignment. Define pre-existing IP before the contract is signed.
- Non-compete clauses drafted as absolute prohibitions are void or unenforceable in most jurisdictions. Scope by time, geography, and nature of use.
- GitHub repository default settings may give the developer admin rights even after contract end. Specify access levels and transfer procedures explicitly.
- "The vendor will maintain appropriate insurance" is unenforceable. Specify minimum values and require certificates.
- "Dispute resolution: [governing law] courts" without naming a specific court or arbitration body is frequently inadequate for cross-border contracts. Name the body.
- Data processing agreements written at a high level ("the vendor will protect data responsibly") do not satisfy GDPR Article 28. The DPA must name sub-processors, specify security standards, and state breach notification timelines.
- Ongoing operational costs (hosting, API fees, licence renewals, maintenance) are frequently omitted from both proposals and contracts. A tool that costs €20K to build may cost €5K–€10K per year to run. Address this explicitly or exclude it explicitly.
- Payment schedules front-loaded to the vendor (e.g. 50% on signature) without milestone triggers shift all financial risk to the client. Link payments to deliverable acceptance.
- Exit provisions are routinely absent. What happens to data, code, credentials, and repository access when the contract ends must be specified — not left to negotiation at the time of exit.
