# Diagnosis: indicator-designer blind compare, 2026-10-09

## Verdict and key

The owner preferred B. Per `key.json`, A is the draft (new text, working copy) and B is the before (old text, `be3d137`). The old version won.

B's lead comes mainly from two things: B verified its sources on the web and A did not, and B gathered its limits into one section. New lines 61 and 97 plausibly explain the first; no line explains the second. With one run per arm and one rater, every "noise" call is provisional.

## What B did better

**1. Clear and to the point.**
- Evidence: B opens with a bold verdict and its reason, then the verification plan. A opens with a disclaimer ("every source below is marked unchecked") before the title. A also leaks skill mechanics into reader text ("the 20% flag in the standard", "the skill's built-in method"). B leaks once.
- Cause: both versions say "put the answer first" (old via CLAUDE.md, new inline). No line explains the ordering.
- Type: noise for ordering. Plain-chat relevant: yes.

**2. Citations well listed.**
- Evidence: B lists three sources with titles, years and working links to UN, Washington Group and WHO pages, then a separate list of what it could not verify. A lists five sources, none linked, all "URL unverified". One has no title ("WHO (2008) reproductive health indicators"). One is padding ("used as context... not as an indicator source"). A states it did not search ("rung 0"). B searched ("rung 2").
- Cause: text-explained. New line 61 makes search conditional ("If you can search the web... If you cannot..."), which gives the model an exit. New line 97 pre-writes "no superseding edition found as of 2026-10". A copied that phrase almost word for word without checking. The new mandatory list (lines 56-58, 97-100) adds WHO (2008) and ICPD+30, which A cited as filler. In the old text, the unconfirmable "WHO/UNFPA 2023" item pushed B to search: a bad citation produced good behaviour by accident.
- Type: text-explained. Plain-chat relevant: yes.

**3. Limitations clearly explained.**
- Evidence: B has one numbered section, "What this set cannot tell you" (no mid-project outcome data, no proof of cause, groups not tracked, small subgroups, consent). A covers similar ground across a summary bullet, an equity note and a gaps list.
- Cause: neither version asks for a reader-facing limits section. Both "Limitations" sections describe the skill, not the indicator set.
- Type: noise (no line explains it). Plain-chat relevant: yes.

**4. Implementation plan with roles.**
- Evidence: on paper A is not weaker; its mechanism section lists roles. B wins on placement: each indicator carries its own who, how and when ("The clinic manager compares... one randomly chosen week each quarter"), plus a use line and a cost flag.
- Cause: text-explained ambiguity present in both versions. Step 5 asks for the mechanism "for each indicator". The output structure asks for "one paragraph on who does what". B followed Step 5; A followed the output structure.
- Type: text-explained (contradiction), outcome noise. Plain-chat relevant: yes.

**5. AI use declared at the end.**
- Evidence: B ends with "AI disclosure: this draft was produced with Claude" and a human-check line. A has none.
- Cause: neither version mentions AI disclosure. B's line comes from the owner's CLAUDE.md publication rule.
- Type: noise between arms. Environment-only: in plain chat, neither version would produce it.

## What A did better

- **No fake source.** A never names "WHO/UNFPA 2023". B names it in its source list (flagged as unverified and not used), so the non-existent title still reaches a donor-facing draft. B also never cites WHO (2010), the canonical reference. The correction in the new text works and should stay.
- **A routine signal on choice.** A's indicator 4 ("received the method they asked for", with mismatch reasons) gives six-monthly data on the "method they choose" half of the outcome. B has no choice signal between surveys.
- **Sharper definitions and gaps.** A defines "modern method", notes the SDG 3.7.1 adaptation, separates minors (15-17), and flags targets and the session schedule as decisions before submission.

## The CLAUDE.md hypothesis

**Partly confirmed, mostly refuted.** A still shows CLAUDE.md marks throughout: a verification-plan line, "Skip to", a five-bullet summary, an "Evidence base" block, the data-gap format and a rung line. The inline rules did not displace CLAUDE.md.

What A lost is narrower: web verification and AI disclosure, two CLAUDE.md rules outside voice. The new pointer scopes CLAUDE.md to "the default writing rules" (line 128), which fits a dilution, but the old pointer ("house style") was just as narrow. The loss of verification is better explained by lines 61 and 97 than by the pointer. The loss of AI disclosure has no textual cause and may be run-to-run variation.

## Proposed changes for revision 3

1. **Make verification the default** (gap 2). Replace line 61's conditional with: "Search the web for every source you cite and link to the issuing body's page. Only if no search tool is available, mark each one ⚠️ URL unverified." Remove "no superseding edition found as of 2026-10" from line 97 so the model checks instead of copying.
2. **Cite only what an indicator rests on** (gap 2). Add: "List a source only if an indicator is taken or adapted from it. Give author, year, full title and link." Keep the WHO (2010) correction. Instruct that a non-existent title is never named in the output.
3. **Add a reader-facing limits section** (gap 3). Add to the output structure: "What this set cannot tell you: a numbered list covering gaps in timing, cause (no comparison group), groups not tracked, subgroup size, and consent or safety."
4. **Resolve the mechanism contradiction** (gap 4). Change the output structure to: per indicator, one line on who collects it, with what tool, the quality check (role and frequency) and how the team uses it. Then a short table: role, task, how often.
5. **Add an AI-use line** (gap 5). Add: "If the output will go to a donor or outside the organisation, end with one line stating that AI drafted it and a named person must check sources and figures." This makes the behaviour independent of CLAUDE.md.
6. **Open with the answer; keep the skill out of the text** (gap 1). Add: "The first line is the recommended set and why. Put any verification note after it. Do not mention this skill, its rules or its thresholds in the output."

## Test-validity note

This compare cannot show plain-chat behaviour. Both arms ran with CLAUDE.md supplying rules neither skill contains: AI disclosure, verification rungs, the evidence-base format, the "Skip to" line. One run per arm cannot separate text effect from variation. The colleague "pass" says nothing about either version, because claude.ai fired mel-discipline.

A valid colleague test needs:
1. Only this skill enabled in claude.ai, or a prompt opening "Use the indicator-designer skill".
2. Proof the skill fired, recorded per run.
3. Web search on or off, recorded per run, because it drives the citation result.
4. Both versions blind, at least two runs each.
5. A cheap first pass: a Claude Code arm with user and project settings excluded.
