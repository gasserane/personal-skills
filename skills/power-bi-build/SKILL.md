---
name: power-bi-build
description: Build an IPPF-branded Power BI dashboard from analytical input. Use when Ane asks to build, scaffold, generate, or update a Power BI dashboard, report, or .pbip project. Applies IPPF Visual Identity 2025 brand, MEL-standard DAX measures, and three standard page templates (indicator dashboard, equity disaggregation, methodology card with evidence-base footer). Requires pbi-cli installed and Power BI Desktop running with a .pbip open.
version: 1.0.0
trigger_keywords:
  - power bi
  - powerbi
  - dashboard
  - .pbip
  - .pbix
  - DAX
---

# /power-bi-build

Build an IPPF-branded Power BI dashboard. Drives `pbi-cli` against the user's open `.pbip` project.

## Pre-flight

Run these checks in order. Stop with the indicated error message on first failure.

1. **`pbi-cli` installed.**
   - Run: `pipx list | grep pbi-cli-tool`.
   - If empty: stop. Show: "pbi-cli is not installed. Run: `pipx install pbi-cli-tool && pipx ensurepath && pbi-cli skills install && pbi connect`."

2. **Power BI Desktop running with an active project.**
   - Ask `pbi-cli` for the active project (`pbi connect` returns the active session).
   - If no active project: stop. Show: "Open Power BI Desktop and load a `.pbip` project, then re-run."

3. **Active project is `.pbip` (text-format), not legacy `.pbix` binary.**
   - If the active project is `.pbix`: stop. Show: "Save your project as `.pbip` first — File → Save as → Power BI Project. The skill operates on the text-based PBIP format only."

4. **Brand layer importable.**
   - Verify `${WORK_FOLDER_ROOT}/ane_package/reporting/powerbi_dashboard/__init__.py` exists.
   - If missing: stop. Show: "Brand layer not found at `${WORK_FOLDER_ROOT}/ane_package/reporting/powerbi_dashboard/`. Verify OneDrive sync or check the path constant in `~/.claude/CLAUDE.md`."

## Resolve intent

From the prompt and the most recent analytical artefact in this session, resolve:

- **Indicators** — keys from `MEL_DAX_LIBRARY`. If ambiguous, ask Ane: "Which indicators? Available: {sorted(MEL_DAX_LIBRARY.keys())}".
- **Audience tier** — Tier 1 working brief by default; Tier 2 publication only if the prompt names it.
- **Page set** — default `(indicator_dashboard, equity_disaggregation, methodology_card)` per indicator. Ane can override.
- **Source line** — derive from prior artefact; if absent, ask once.

## Build

```python
from ane_package.reporting.powerbi_dashboard import (
    MEL_DAX_LIBRARY,
    build_equity_disaggregation_page,
    build_indicator_dashboard_page,
    build_ippf_theme,
    build_methodology_card_page,
)

theme = build_ippf_theme()
measures = {k: MEL_DAX_LIBRARY[k] for k in selected_indicators}
pages = []
for indicator in selected_indicators:
    pages.append(build_indicator_dashboard_page(indicator, target, source))
    pages.append(build_equity_disaggregation_page(
        indicator, ("age", "gender", "geography", "wgss_disability"), source))
pages.append(build_methodology_card_page(method_note, evidence_base_sources, glossary_terms))
```

## Apply via pbi-cli

For each artefact, call the matching `pbi-cli` skill. Surface `pbi-cli`'s diagnostic verbatim on failure. Never retry — failed writes risk corrupting the `.pbip`.

1. `pbi-cli theme apply <theme.json>` — write theme.
2. For each measure: `pbi-cli measure add --table=<inferred-table> --name=<key> --expression=<dax>`.
3. For each page: `pbi-cli page create` then `pbi-cli visual add` per visual in the recipe.
4. Read back theme, measures, pages from disk; compare to written. On diff, surface the diff and stop.

**Page ID sanitisation.** Before passing `page_id` to `pbi-cli`, sanitise: `page_id.lower().replace(" ", "_")`. The brand layer's recipe uses `f"{indicator_name}-dashboard"`-style IDs which assume snake_case input; if a caller passed an indicator name with spaces, sanitise here at the CLI boundary rather than in the recipe layer.

## Output

Tier 1 working brief summary in chat:

```
Power BI build complete.
- Theme: IPPF Visual Identity 2025 applied (X visualStyles).
- Measures added: {N} ({list of keys}).
- Pages added: {N} ({list of page names}).
- Round-trip clean.
- Warnings: {list, or "none"}.

Source: {derived source line}.
```

For Tier 2 publication output, structure the response per the spec (inline citations, framework names visible).

## Common errors

| Error | Likely cause | Fix |
|---|---|---|
| `pbi-cli skills install` not run | First time using pbi-cli on this machine | Run `pbi-cli skills install` once. |
| File lock conflict | Visual being edited in Power BI Desktop | Close active visual edit; re-run. |
| Schema conflict on measure | Referenced table/column missing | Verify the data model matches measure assumptions; adjust DAX or data model. |
| Indicator not in MEL_DAX_LIBRARY | New indicator | Add to `dax_library.py` with its wiki entry; PR to anework-package. |
