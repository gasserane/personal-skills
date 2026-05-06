# Trigger eval set — grade-system

20 realistic queries (9 should-trigger, 10 should-not-trigger) for description optimization.

## How to run

The optimization loop must run from a terminal **outside** an active Claude Code session. Inside Claude Code, recursive `claude -p` subprocess calls fail with `WinError 10038` on Windows.

From a fresh PowerShell or Git Bash terminal:

```powershell
$env:PYTHONIOENCODING = "utf-8"
cd "C:\Users\AGasser\.claude\plugins\cache\claude-plugins-official\skill-creator\unknown\skills\skill-creator"
python -m scripts.run_loop `
  --eval-set "C:\Users\AGasser\OneDrive\GitHub\personal-skills\skills\grade-system\evals\trigger-eval.json" `
  --skill-path "C:\Users\AGasser\OneDrive\GitHub\personal-skills\skills\grade-system" `
  --model claude-opus-4-7 `
  --max-iterations 3 `
  --verbose
```

Output: HTML report opens in browser. JSON contains `best_description` selected by held-out test score.

## When to re-run

- After the skill has been used in production for 2–4 weeks and you've noticed under-triggering on phrasings you'd expect to work
- When you add new triggering keywords / contexts to the description
- After major changes to the skill's scope (e.g., adding more dimensions to the grading framework)

## Pairing with system-audit

`system-audit/evals/trigger-eval.json` is the parallel eval set for the sister skill. Both can be optimized in the same terminal session.

## Notes on the eval set

The should-not-trigger queries deliberately include near-misses where someone is grading content (proposals, indicators, ToCs) rather than the system itself. This is the most common confusion vector for `/grade-system` — the word "grade" is shared with content-grading tasks. The negative cases test whether the description correctly disambiguates "grade the system" from "grade my draft".
