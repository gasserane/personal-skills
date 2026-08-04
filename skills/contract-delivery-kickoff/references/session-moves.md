# Running the hour

How the session itself goes, and what each move is defending against. Read
this before the session, not during it.

The reference run throughout is the Abortion Dashboard Phase II session of
24 July 2026: 8 technical days and 7 coordination days against 17 contracted
components, three tranches, done by hand.

---

## Before the room

**Confirm signature status.** Not by assuming, and not from the offer document,
which almost never says. Ask. An unsigned contract means no expenditure can be
committed, so every day agreed in the session is provisional and has to be
labelled as such out loud. It also usually means the first contractual
deliverable has already slipped, which is a separate conversation you would
rather have now than in the wrap-up.

**Run `build` and read what it says about the contract's own proposal.** If the
tranches as priced already exceed the days bought, the session cannot fix that
by negotiating. It is a contract amendment, and it needs to be on the agenda as
one.

**Decide which items are protected before anyone sees the list.** A do-no-harm,
credibility or compliance defect is not a candidate to trade against a nicer
chart. If you have not named them in advance, they get traded in the room,
because in the room everything is negotiable and the clock is running.

---

## The running order, and why it is this order

### 1. Contract status and start date

Two minutes. What can be committed, and from when.

### 2. The day budget, across every tranche

**Before the item list. This is the single most important sequencing decision
in the session.**

A list of 17 plausible items read first does not inform the cap, it sets it.
Once a group has walked the list and agreed each item is reasonable, "what fits
in 8 days" gets answered against the list rather than against the contract, and
the answer is always "a bit more than 8". The workbook puts `01 Day budget`
ahead of `02 Triage` to make the wrong order require deliberate effort.

Fill `Days agreed` for every tranche, including the ones that start months from
now. Watch the `Remaining` cell: it shades red below zero.

### 3. Estimates against every tranche

Not just the one starting now. A tranche with no estimate reads as a tranche
with no cost, and the remainder of the budget reads as headroom when it is
already spoken for. The workbook writes `not priced` rather than a zero
precisely so this cannot be skimmed past.

A rough range beats no number. "Somewhere between two and four days" is
something you can plan against; silence is not.

### 4. The item-by-item walkthrough

**Ask for the estimate before saying what you want.** Naming the outcome first
anchors the number, and the anchored number is the one the budget then gets
built on. This is the cheapest discipline in the session and the easiest to
forget.

**Confirm each item is still open**, against the live product rather than from
memory. Items recorded weeks earlier are often already fixed, and on the
reference run several were.

**Split by lane as you go.** Three lanes:

| Lane | What it costs |
|---|---|
| Supplier, build | Development time, charged against the contracted days |
| Client, content | Near zero once the content is handed over |
| Joint | Client decides what correct looks like, supplier implements |

The content lane is where scope wins live. An item that looked like three days
of development is often a paragraph of final text plus twenty minutes. On the
reference run the split moved several items out of the paid lane entirely.

### 5. Decisions, written live

The `Decision` column is the output of the session. Not the notes afterwards,
not the follow-up email. Anything not written in the workbook while everyone is
present gets remembered differently by each person a fortnight later.

---

## What to watch for

**An item list that grows in the session is normal. A cap that grows with it is
the failure.** New items surface every time; that is why the triage sheet
carries blank `NEW-nn` rows. What must not happen is the ceiling moving to
accommodate them.

**"We can probably fit that in" is an estimate.** Write it down as one, with a
number. Unrecorded optimism is how a tranche ends up with no days left.

**A protected item being discussed as a trade-off** means move 4 did not happen
early enough. Say so, and put it back.

**Anything agreed against an unsigned contract is provisional.** Say it out
loud when it is agreed, not in the note. Otherwise somebody starts work on it.

---

## After the session

1. Fill the note template from the workbook rather than from memory, so the two
   cannot disagree.
2. Check three things: did the agreed days stay inside the cap once everything
   was entered; did any tranche end the session still unpriced; was anything
   committed against an unsigned contract.
3. Commit the workbook. The edit-preservation guard cannot see COM or openpyxl
   writes, so an emitted file left uncommitted looks hand-edited to the guard
   and is exposed to a OneDrive revert.
4. The workbook is now the live record. Edit it in place; never re-run `build`
   over it. The estimates and decisions in it exist nowhere else, which is why
   `build` refuses to overwrite without `--force`.
