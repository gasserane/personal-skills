---
name: rfp-digital-services
description: "Use this skill whenever a user wants to write, draft, prepare, or develop a Request for Proposal (RFP), Terms of Reference (ToR), or procurement brief for digital development services — including software tools, data platforms, dashboards, AI-powered systems, websites, or any technology product commissioned from an external vendor. Triggers include: \"help me write an RFP\", \"I need to procure a tool\", \"how do I brief a developer\", \"we want to commission a digital system\", \"draft a ToR for a tech consultancy\", \"we need a call for proposals for our platform\", or \"help me describe what we need built\". Always conduct a structured interview before drafting. Use with the docx skill when a Word document output is requested. Not for drafting or grading a general consultancy ToR (use tor-procurement) or for scoring supplier offers (use selection-toolkit or procurement-offer-review).\n"
---

# RFP for Digital Development Services

## Purpose

This skill helps IPPF EN staff — including those with no technical background — write a Request for Proposal (RFP) that is clear, complete, and fair. A good RFP does three things: it communicates what you actually need (not what you think the technical solution is), it gives vendors enough information to price and plan honestly, and it creates the basis for evaluating and comparing responses.

The most common failure in NGO procurement is an RFP that is either too vague (vendors invent their own interpretation of the scope) or too prescriptive (staff accidentally describe a specific technical solution rather than the problem it must solve). This skill steers between both failure modes.

The output is a structured RFP document. The process is a guided interview — you answer questions, Claude drafts the document.

---

## Step 0: Confirm output format

Ask the user:

> "Would you like the RFP as a Word document (.docx), as an inline draft in chat, or both?"

If Word → apply the docx skill after drafting. Font: Book Antiqua 11pt.
If inline → produce the full RFP as structured markdown in the conversation.

---

## Step 1: Structured interview — gather everything before drafting

Conduct this interview in one go. Present all questions together so the user can answer in their own order. Explain briefly why each question matters — non-technical users often don't know what information is relevant.

Tell the user:

> "I will ask you a set of questions. You don't need to know the technical answers — describe what you need in plain language and I will translate it into the right RFP language. If you're unsure about something, say so and I'll help you think through it."

---

### Block 1: Organisational context

1. **What does your organisation do, and what programme or project is this tool for?**
   *(Vendors need to understand the mission context. An intelligence platform for a human rights network has different requirements from a fundraising database.)*

2. **Who commissioned this work — is it internally funded, donor-funded, or grant-funded?**
   *(If donor-funded, the funding source must appear in the RFP and the contract. Some donors impose IP or open licensing conditions.)*

3. **Who will use the tool? Describe the users in plain terms.**
   *(e.g. "5 staff in our Brussels office + 20 partner organisations in 15 countries, some with limited IT support." This determines hosting, language, accessibility, and support requirements.)*

4. **Does your organisation have an existing IT infrastructure the tool must connect to?**
   *(e.g. Microsoft 365, Azure, SharePoint, Power BI, Salesforce, existing databases. If yes, the vendor must know this upfront — integration requirements affect scope and cost significantly.)*

---

### Block 2: The problem and the tool

5. **Describe the problem you are trying to solve. What is not working now, or what capability do you not yet have?**
   *(Describe the problem, not the solution. "We receive intelligence about threats from 40 countries but cannot analyse or share it systematically" is a problem statement. "We need a dashboard" is already a partial solution — it may or may not be the right one.)*

6. **What should the tool enable users to do? List the most important things it must do.**
   *(These become your functional requirements. Write them as user actions: "Users must be able to upload documents", "Staff must be able to tag entries with a classification system", "Partner organisations must receive automated alerts." Aim for 5–10 core functions.)*

7. **Are there things the tool must NOT do, or constraints it must operate within?**
   *(e.g. "Must not store personal data on servers outside the EU", "Must not require users to install software on their computers", "Must work on low-bandwidth connections", "Must be accessible on mobile devices.")*

8. **Does the tool involve personal data — information about identifiable individuals?**
   *(Yes / No / Unsure. If unsure, treat as yes. This triggers GDPR requirements that must appear in the RFP.)*

9. **Does the tool involve sensitive data — health information, political activity, financial data, or information that could put individuals at risk if exposed?**
   *(If yes, security requirements and do-no-harm provisions must be explicit in the RFP.)*

---

### Block 3: Scale, timeline, and budget

10. **How many users will use the tool, and in how many countries?**
    *(Affects hosting architecture, access control design, and language requirements.)*

11. **What is your target timeline? When do you need the tool to be operational?**
    *(Be honest — vendors will flag if a timeline is unrealistic. It is better to know early than to receive proposals built on false assumptions.)*

12. **What is your indicative budget range?**
    *(You do not need an exact figure. A range is enough — e.g. "€20,000–€50,000 for development, with a separate ongoing operational budget TBD." Without a budget signal, vendors cannot calibrate their proposals and may either over-engineer or under-deliver.)*

13. **Do you expect to pay for ongoing costs after delivery — hosting, maintenance, updates, support?**
    *(If yes, say so in the RFP. Vendors should include ongoing cost estimates. If you do not ask, they will not include them, and you will face an unbudgeted bill after delivery.)*

---

### Block 4: IP, ownership, and governance

14. **Who should own the tool and its code after delivery — your organisation, a partner organisation, or the vendor?**
    *(Default for NGO procurement: the commissioning organisation owns all outputs. If a partner hosts the tool — e.g. a Member Association — clarify who holds legal ownership and who receives a licence. This must be stated in the RFP so vendors price it correctly.)*

15. **Should the vendor be restricted from deploying a similar tool for organisations with opposing interests?**
    *(Relevant if the tool handles sensitive intelligence, advocacy strategy, or beneficiary data. If yes, state a deployment restriction in the RFP — vendors must agree to this condition to be eligible.)*

16. **Will the tool be open source, or proprietary?**
    *(Open source means the code is publicly available and reusable; proprietary means it is not. Most NGO tools are proprietary by default. If your donor requires open source, state this explicitly.)*

---

### Block 5: Vendor requirements

17. **Are there minimum qualifications you require from vendors?**
    *(e.g. "Must have delivered a similar data platform in the NGO sector", "Must have GDPR compliance experience", "Must be registered in an EU/EEA country", "Must carry professional indemnity insurance of at least €X.")*

18. **Do you have a preference for the technology stack, or are you open to vendor recommendation?**
    *(If you have existing infrastructure — e.g. Azure, Power BI — say so and ask vendors to align. If you have no preference, state that vendors should justify their choice. Do not prescribe a technology unless you have a specific reason — it limits competition and may exclude better solutions.)*

19. **Will you require vendors to present their proposal in person or by video call before evaluation?**
    *(Useful for complex scopes. If yes, state it in the RFP so vendors plan for it.)*

---

### Block 6: Evaluation

20. **How will you evaluate proposals? What matters most — technical quality, price, team experience, timeline?**
    *(You do not need a formal weighting system for small procurements, but you need a clear priority. For larger contracts, a weighted scorecard — e.g. 40% technical quality, 30% team experience, 20% price, 10% timeline — reduces subjectivity and is defensible to donors.)*

---

## Step 2: Draft the RFP

Once the user has answered the interview questions (partial answers are fine — flag gaps explicitly in the draft), produce the RFP using this structure. Do not deviate from the structure — each section serves a specific purpose for vendors.

---

### RFP Structure

**Cover page**
- Issuing organisation (full legal name)
- Title of the RFP
- Reference number (if applicable)
- Issue date
- Submission deadline
- Contact person and email for queries

---

**Section 1: Background and context** *(~300 words)*

Describe the organisation and the programme. Explain why this tool is needed — the problem it solves, not the solution. Include the funding source if applicable. Write this for a vendor who has never heard of your organisation.

---

**Section 2: Objectives** *(~150 words)*

State what the tool must achieve. Use outcome language: "The tool will enable Hub staff to classify and retrieve intelligence entries across 40 countries in real time" — not feature language: "The tool will have a search bar."

---

**Section 3: Functional requirements** *(structured list)*

List what the tool must do, organised by user type or by function. Use the format:

> **[User type] must be able to [action].**

Distinguish between:
- **Must have** — non-negotiable requirements
- **Should have** — important but negotiable
- **Nice to have** — desirable if budget allows

This distinction prevents vendors from padding proposals with features you don't need, and prevents you from rejecting proposals that meet your real requirements but omit a peripheral feature.

---

**Section 4: Technical requirements** *(structured list)*

State the non-negotiable technical constraints:
- Hosting: where data must be stored (e.g. EU-based servers, IPPF Azure infrastructure)
- Authentication: how users will log in (e.g. Microsoft Entra ID / OAuth, email/password)
- Integrations: what existing systems the tool must connect to
- Data protection: GDPR obligations, if personal or sensitive data is involved
- Security standards: reference OWASP or ISO 27001 if applicable
- Accessibility: browser, mobile, bandwidth requirements
- Scalability: expected growth in users or data volume

If you do not know the answer to a specific technical question, state: "Vendors should advise on [topic] and justify their recommendation."

---

**Section 5: Deliverables and milestones** *(structured table)*

List what the vendor must produce. Be specific — outputs, not activities.

| Deliverable | Description | Target date |
|---|---|---|
| Inception report | Detailed technical specification, revised timeline, confirmed approach | [Month X] |
| Prototype / proof of concept | Working version of core functionality for user testing | [Month X] |
| User acceptance testing | Testing period with designated staff; issue log and fixes | [Month X] |
| Final tool delivery | Fully functional, documented, and deployed tool | [Month X] |
| Training | User guide and training session for staff | [Month X] |
| Source code and documentation | Full code repository transfer and technical documentation | On delivery |

State that payment will be linked to milestone acceptance, not to time elapsed.

---

**Section 6: Intellectual property** *(short paragraph)*

State clearly:
- All outputs, code, data models, and documentation produced under this contract are assigned to [Client organisation].
- Vendors must disclose any pre-existing IP (e.g. frameworks, libraries) embedded in the deliverables and grant the client a perpetual, royalty-free licence to use these.
- [If applicable: Vendors agree not to deploy a substantially similar tool for [category of competing organisations] for [X] years following contract end.]

---

**Section 7: Data protection** *(if personal data is involved)*

State that:
- The vendor will act as a data processor under GDPR Article 28.
- A Data Processing Agreement (DPA) will be required as part of the contract.
- The vendor must maintain appropriate technical and organisational security measures.
- Any sub-processors must be disclosed and approved.
- Data must be returned or deleted at contract end.

If no personal data is involved, state this explicitly so vendors do not over-engineer privacy measures.

---

**Section 8: Budget and pricing**

State the indicative budget range. Ask vendors to submit a detailed cost breakdown by:
- Development phases
- Team roles and day rates
- Ongoing costs (hosting, licences, maintenance, support) — these must be stated separately from development costs

State the currency and whether VAT is included or excluded.

---

**Section 9: Vendor eligibility and evaluation criteria**

State any minimum requirements vendors must meet to be eligible (registration, insurance, track record).

State how proposals will be evaluated. If using a weighted scorecard, list the criteria and weights. Example:

| Criterion | Weight |
|---|---|
| Technical approach and methodology | 35% |
| Relevant experience and team qualifications | 25% |
| Value for money (cost breakdown and justification) | 25% |
| Timeline and risk management | 15% |

---

**Section 10: Proposal requirements**

Tell vendors exactly what to submit. Example:

Proposals must include:
1. Understanding of the brief and proposed approach
2. Technical methodology and architecture overview
3. Team composition with CVs for named individuals
4. Portfolio: two examples of comparable prior work
5. Detailed budget with day rates and cost breakdown
6. Proposed timeline with milestones
7. Confirmation of insurance coverage
8. Any assumptions or clarification questions

State the submission format (PDF, email, portal), the deadline, and the contact point.

---

**Section 11: Process and timeline**

| Stage | Date |
|---|---|
| RFP issue date | [Date] |
| Deadline for clarification questions | [Date] |
| Responses to clarification questions issued | [Date] |
| Proposal submission deadline | [Date] |
| Shortlisting / presentations (if applicable) | [Date] |
| Contract award notification | [Date] |
| Anticipated contract start | [Date] |

---

**Annex A: Glossary** *(if the RFP uses technical terms)*

Define any acronyms or technical concepts that a non-specialist vendor might not know. For IPPF EN work, this typically includes: SRHR, MAs, donor-programme names, GDPR, OAuth, Azure Entra ID. If a specific Member Association is named in the RFP, include its full name and country.

---

## Step 3: Quality check before finalising

Before presenting the draft to the user, run this internal check:

- [ ] Problem statement describes a problem, not a pre-selected solution
- [ ] Functional requirements use user-action language ("users must be able to...")
- [ ] Must have / should have / nice to have are distinguished
- [ ] Technical requirements state constraints, not vendor choices (where avoidable)
- [ ] Budget range is included — no budget = unbiddable RFP
- [ ] Ongoing costs are addressed
- [ ] IP ownership is explicit
- [ ] GDPR obligations are included if personal data is involved
- [ ] Payment is linked to milestones, not time
- [ ] Evaluation criteria are stated
- [ ] Proposal submission requirements are specific and complete
- [ ] No section is blank or contains "TBD" without flagging it to the user

Flag any gaps to the user with a specific question: "Section X is currently incomplete because you were unsure about [topic]. Can you tell me [specific question]?"

---

## Step 4: Offer to connect to the next stage

After the RFP is finalised, offer:

> "Once proposals are submitted, I can help you review and compare them using the tech-proposal-review skill. Would you like me to set up a scoring matrix based on the evaluation criteria in this RFP?"

---

## Tone and audience guidance

The user is a programme professional, not a procurement or IT specialist. All questions must be answerable in plain language. When translating their answers into RFP language, preserve their intent — do not impose technical choices they have not made.

The RFP itself must be readable by two audiences simultaneously: a programme person at the client organisation (who needs to recognise their own requirements) and a technical vendor (who needs enough precision to price and plan).

Write in active voice. Use specific verbs. No filler.

---

## Reference: IPPF EN procurement context

These patterns are specific to IPPF EN procurements and must be applied when relevant.

- **Funding source**: If the work is funded through a donor programme, name the funding source in the RFP background section. Contracts without this reference create grant compliance risk.
- **Azure infrastructure**: IPPF EN tools are typically hosted on IPPF's own cloud infrastructure. If this applies, state it as a technical requirement and flag that the vendor will need to coordinate with IPPF IT during deployment.
- **MA as contracting entity**: If an IPPF EN Member Association is the contracting entity rather than the IPPF EN Secretariat, the RFP must reflect the MA as the issuing organisation — including its full legal name, country of registration, and registration number. IP ownership, governing law, and dispute resolution clauses in the resulting contract must reflect the MA's jurisdiction, not Belgium. Ask the user to confirm which entity is contracting before drafting the cover page.
- **GDPR**: IPPF EN operates under Belgian law and EU GDPR. All tools handling personal data require a DPA. Even tools that handle only organisational data (e.g. MA contact lists) may trigger GDPR depending on the nature of the data.
- **Do-no-harm**: Tools used in a sensitive SRHR advocacy context handle sensitive information about activists, beneficiaries, and other people who could be put at risk. The RFP must include a do-no-harm provision: the vendor must not disclose, sell, or use this data for any purpose other than the contracted work, and must not deploy the tool for parties whose interests conflict with IPPF EN's mandate.
- **Multi-country access**: IPPF EN tools often serve MAs in 40+ countries across Europe and Central Asia. State expected user locations and any specific accessibility requirements (language, bandwidth, device type) so vendors can design accordingly.
- **Replicability**: If the tool is intended to be replicable by other MAs or deployable across the network, state this as a design requirement — not as an afterthought. It affects architecture decisions significantly.
