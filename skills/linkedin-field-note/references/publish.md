# Stage 5 — PUBLISH: LinkedIn via claude-in-chrome

## The gate, restated

Publish only artifacts Ane approved **in this session**. If the drafts were approved in an earlier session, show her the final text/file now and get a one-line go per artifact before touching LinkedIn. Anything she edits after approval needs re-approval. No exceptions, including "just fixing a typo".

## The calendar (agreed 2026-07-27; ledger's series rules may supersede)

| Slot | What |
|---|---|
| Tuesday 09:00-10:30 RST | Toolkit **document post** (PDF attached) |
| Wednesday or Thursday 08:30-10:00 RST | **Article**, then the **short post** pointing to it |

Post only when Ane can engage the first 60-90 minutes. If she cannot, propose the next matching slot instead of posting anyway.

## Scheduling mechanics

- **Posts** (short post, document post): LinkedIn's native scheduler supports them. If the agreed slot is in the future, schedule natively at the slot time and show Ane the scheduled-post confirmation.
- **Articles** cannot be scheduled natively: stage the article as a ready draft in the LinkedIn editor, confirm to Ane it is staged, and publish on her one-line go in the slot.
- **Order within the article slot:** publish the article first, then the short post, then immediately add the first comment with the article link (and any P.P.S.). The post must not go out before the article URL exists.

## Browser runbook

1. Load the claude-in-chrome core tools in one ToolSearch call; call `tabs_context_mcp` first; create a new tab (never reuse stale tab IDs).
2. Open linkedin.com; verify the session is Ane's account (her name/avatar in the nav) before any action. If not logged in, stop and hand over — never enter credentials.
3. **Short/document post:** Start a post → paste the approved text exactly (no silent edits) → attach the PDF (document post) or visual → set schedule if scheduling → screenshot → show Ane → on her go, click Post/Schedule.
4. **Article:** Write article → paste title and body → insert the header/cover image → save as draft → screenshot → on Ane's go, publish → copy the published URL.
5. **First comment:** paste the approved comment with the real article URL; post it.
6. The screenshot-before-submit step is mandatory for every artifact: what Ane confirms is what the button will send.
7. If a step fails 2-3 times (editor quirks, upload failures), stop and report; do not improvise workarounds that change the content. Formatting casualties of the LinkedIn editor (lost bold, list spacing) are shown to Ane before publishing, not silently accepted.

## After publishing

1. Update the ledger: status → published, dates, live URLs, which artifacts shipped.
2. Rename any `(DRAFT)` files to match their published status if Ane wants the folder tidy.
3. Remind Ane the engagement window is now (the calendar exists so she is available).
4. When she later reports reactions, they go in the ledger's "Reactions and learning" plus "Seeds" — that is Stage 1's raw material for the next note.
