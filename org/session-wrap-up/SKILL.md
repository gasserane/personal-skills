---
name: session-wrap-up
description: Close a working session cleanly, in a Claude chat or in Claude Code. Use when the user types /session-wrap-up, or says "wrap up", "close this session", "end of session", "I want to start fresh" or "continue tomorrow". Produces one handoff note - what is decided, what is still open and who does it, and what the next session must settle - written so it can be pasted into a new chat or session and work starts exactly where this one stopped. In a chat this replaces the Claude Code /clear command - wrap up, open a new chat, paste the note.
---

# Session Wrap-Up

## What this skill is for

A new chat remembers nothing, so people stay in long, slow conversations to avoid losing the thread. This skill writes one handoff note that carries the thread into a fresh chat or session.

A good handoff is thinking, not form-filling. Its value comes from three things a template cannot do for you: getting every decision down with its reason, giving each open action an owner and a date, and spotting what the next session must settle before it starts. Spend your effort there.

Never send, publish, delete, commit or push anything as part of a wrap-up.

## Step 1 - Read the whole conversation

Collect, without writing anything yet:

- **Decided.** Each decision, with the reason the user gave. A decision without its reason gets argued again in the next chat.
- **Produced.** Each finished output, and where it now lives (a file name, an artifact, a draft in this chat). If you do not know where something was saved, say so.
- **Open.** Each piece of work not finished, who does it, what it waits on, and any date. Include anything the user said they would do, and anything you said you would check and did not.
- **Unsettled.** Questions the work raises that nobody has answered yet: a rule nobody checked, a word two readers could understand differently, a risk to the people the work is for. These often never came up in the chat. Finding them is the most useful thing you do here.

Only record what the conversation shows. If you are not sure something was finished, treat it as open.

**In Claude Code only:** if the folder is a git repository, run `git status --short` and `git log --oneline @{u}..`. Add files not committed, or commits not pushed, to the open actions only if they belong to the work of this session. Leave out changes to other work. Do not commit or push.

## Step 2 - Write the handoff

Use today's date from the session. Never guess it.

Write the handoff as a normal, easy-to-read document: short headings, numbered lists and plain tables. Do not put it in a code block. The reader should see in a few seconds what is decided, what is open and who does it.

Use this order and leave out any part that is empty:

1. **Title:** "Handoff: [name of the work], [date]".
2. **Two opening sentences:** what is now fixed, and what is still open or blocked.
3. **Decided.** A numbered list. Each decision with its reason, because a decision without its reason gets argued again. Include the finished content itself where the next session needs it: the agenda as a table, the exact wording of questions, the figures.
4. **Produced.** Each output and where it lives. If the user edited it by hand, say: change that file, do not rebuild it.
5. **Open actions.** A table with the columns: #, Action, Who, Waits on, When. Write "urgent" when it is due within two weeks.
6. **To settle before continuing.** Up to four questions, most important first. Each says why it matters and what changes depending on the answer.
7. **Next step.** One concrete action, and what to attach or paste to start it.

Rules:

- **It must stand alone.** The next chat sees nothing of this one. Spell out names, figures, wording and decisions in full. Never write "as discussed".
- **Keep it tight.** Say each fact once. Do not repeat the decisions in the open actions.
- **No sensitive personal data.** Never copy names, contact details, ages or health information of clients, service users, survivors or any private person into the handoff. Write "the case discussed" and point to where the details are kept. The same applies to passwords and access codes. If you left something out for this reason, say so in one sentence inside the note, so the next chat does not add it back.
- **Mark your own additions.** If a question or action did not come up in the conversation, add "(new)" after it.

## Step 3 - Close

End with one line telling the user what to do, and nothing after it except the optional offer below:

- In a chat: "Open a new chat, attach [any files it needs], and paste the note above." The copy button under this reply copies the whole note.
- In Claude Code: "Type /clear, then paste the note above." Offer to save the note as a Markdown file in the project folder first; ask for the file name and never overwrite an existing file without asking.

If the session produced real work, you may add one line: "If you want, I can also write a four-line learning note from this session." Do not wait for an answer.

If nothing is open, say "Nothing open. Safe to close." and skip the handoff, unless the user asked for one.

## Writing style

Plain English for readers whose first language may not be English. Short sentences, common words, no idioms. Spell out an abbreviation the first time you use it. Do not talk about this skill or how it works in the output.

## If available

- **The setup has its own wrap-up command or skill** (for example a project `/wrap-up`): if the user called this skill by name, do the wrap-up here and do not discuss the other one. Otherwise, mention it in one line as an option.
- **Project instruction files** (such as `CLAUDE.md`) that say where handoff notes go or how to name them: follow them when saving.
- **A memory feature** that already stores session notes: do not repeat its content. Point to it instead.
