# Dictated notes mode

Turn Ane's spoken per-topic debrief of a meeting into a confirmed, structured note. Process proven 2026-07-16 on a five-topic Lena 1-1.

## Flow

1. **Set up in one message.** Confirm the defaults as a block Ane can correct instead of answering one by one: meeting date (default today), counterpart, storage folder (default `Ane Plans` for 1-1s), personal record vs shareable. If a prep sheet exists for this meeting (`1-1 prep - Ane-<counterpart> - *.md`), load it: its topics become the expected topic list, and its listed actions get status-checked during the interview. Then invite "Topic 1: ...". If context about a topic already exists in the session or memory, say what you will be listening for; it primes a more complete dictation.

2. **Ane dictates one topic per message, free-form.** No structure expected from her. Conventions to request once: start with the topic name; say "we decided" vs "we discussed"; flag tentative items; say numbers, dates and names explicitly.

3. **Interview before drafting.** After each topic, ask at most 5 batched clarifying questions, and only questions that change the note:
   - Garbled or unknown names. Phonetic dictation mangles proper nouns badly (observed: "restaurants" for "Prashant", "SERV" for "CERV", "M8" for "MA"). Match against known contacts in memory and the project context; confirm anything not certain. Never guess a name or reconstruct a contact.
   - Decision or discussion? Anything ambiguous that would land under Decisions.
   - Owner and deadline for every action.
   - Ambiguous figures, dates, options ("which of the two options was chosen?").
   - Load-bearing gaps the topic implies but the dictation skipped.

   If an answer round skips a question, re-ask once, briefly. If it is skipped twice, file the item under Open/parked instead of nagging: an honest gap beats a stalled interview.

4. **Draft each topic immediately after its answers**, in the shared note structure subsections (Key takeaways / Decisions / Next steps / Open-parked). Ane corrects or confirms. Show amendments as changed lines only; never re-paste an unchanged section.

5. **One write at the end**, after all topics are confirmed: the `.md` then the branded `.docx`, per the shared rules in SKILL.md. Build the deadline-sorted action tables across all topics at this point, not incrementally.

6. **Close out.** Update the centralised tracker (`scripts/update_tracker.py`, see `references/action-tracker.md`). Offer to persist durable facts (confirmed decisions, changed budgets, new deadlines) to memory. In the final message, surface any action due today or tomorrow explicitly: a deadline that only lives inside the file gets missed.

## Why interview-first

Dictated summaries reliably carry five recoverable defect types: mangled names, unclear decision status, ownerless actions, missing deadlines, and tentative items sounding firm. Catching them in one question round while Ane's memory of the meeting is fresh costs a minute; catching them next week costs a rework session and sometimes a wrong email.
