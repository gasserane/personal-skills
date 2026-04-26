# Changelog — gasserane/personal-skills

All notable changes to the Ann / Vi / Li / Researcher skill set are documented here.

## [2026-04-26] — Agent system audit improvements

**Skills affected:** ann, vi, li, researcher
**System-level additions:** `mel_wiki/wiki/domain-standards.md`, `CHANGELOG.md`

### Ann
- **Vi failure path**: added explicit halt-and-present protocol when Vi fails both return cycles in PHASE 5
- **SIMPLE task insight capture**: added lightweight wiki flag step in PHASE 6 for SIMPLE tasks that do not generate an Evidence Brief
- **Cost estimate model**: replaced vague "rough range" with defined token-range bands
- **Domain standards reference**: added link to `mel_wiki/wiki/domain-standards.md` as primary source; inline block retained as quick reference

### Vi
- **Progress signal clarification**: marked as informational; execution continues immediately without waiting for response
- **Post-escalation compile logic**: escalated subtasks are explicitly excluded from the coverage check and placed in the ESCALATION annex
- **Contradiction resolution**: added protocol for when specialists contradict on material points (flag, state precedence, mark for verification)
- **Standing instructions**: added optional block allowing Ann to pass Ane's validated preferences to Vi's specialist design
- **Domain standards reference**: added link to `mel_wiki/wiki/domain-standards.md`

### Li
- **CATALOG table schema**: defined explicit column headers (`Title | Author(s) | Year | Language | Doc_type | Key_topics | Quality | Readable`)
- **First-run setup**: added artifact-log.md creation check in INGEST-FROM-RESEARCHER Step 2
- **LINT trigger**: clarified as "on request or automatically as part of CURATE (weekly)" — removes ambiguous standalone "weekly" claim

### Researcher
- **Tool unavailability fallback**: added protocol for Consensus / PubMed / knowledge MCP failure — log and continue, do not block
- **Roster advisory language**: clarified that specialist roster in Artifact A is advisory; Vi owns final design
- **Evidence Brief length cap**: Artifact A limited to 2,500 words; prioritisation order defined
- **Intra-evidence conflict resolution**: added explicit conflict flagging protocol for contradictory Tier 1 sources
- **Domain standards reference**: added link to `mel_wiki/wiki/domain-standards.md`

### System-level
- Created `mel_wiki/wiki/domain-standards.md` — single source of truth for current authoritative framework versions; replaces four identical embedded blocks
- Created `CHANGELOG.md` — documents all skill changes for future reference
