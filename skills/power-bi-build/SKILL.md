---
name: power-bi-build
description: Build IPPF-branded Power BI artefacts from analytical input. Use when Ane asks to build, scaffold, or update a Power BI dashboard, semantic model, DAX measures, or .pbip project. Applies IPPF Visual Identity 2025 brand, MEL-standard DAX measures, and three standard page recipes (indicator dashboard, equity disaggregation, methodology card). Requires the pbi CLI (pbi-cli-tool, command name `pbi`) installed and Power BI Desktop running with a .pbip open.
version: 1.0.1
trigger_keywords:
  - power bi
  - powerbi
  - dashboard
  - .pbip
  - .pbix
  - DAX
---

# /power-bi-build

Build IPPF-branded Power BI artefacts. v1 scope: writes DAX measures into the semantic model via the `pbi` CLI; writes the IPPF theme JSON into the `.pbip` folder directly; saves page recipes (indicator dashboard, equity, methodology) as JSON staging artefacts the user applies manually in Power BI Desktop. Full page-and-visual automation is v2.

## Tooling reality

The `pbi` CLI (package `pbi-cli-tool`, command name `pbi`) wraps a Power BI MCP server for **semantic model** operations only:

- ✅ `pbi measure create` — add DAX measures.
- ✅ `pbi table`, `pbi column`, `pbi relationship` — model structure.
- ✅ `pbi dax` — execute and validate DAX.
- ❌ No `pbi theme` command. Theme JSON is written directly to the `.pbip` folder.
- ❌ No `pbi page` or `pbi visual` command. Pages and visuals are created manually in Power BI Desktop using the staging recipe JSONs as a guide.

When the upstream tool adds report-layer commands, this skill will absorb them. v1 ships with the scope above.

## Pre-flight

Run these checks in order. Stop with the indicated message on first failure.

1. **`pbi` installed.**
   - Run: `pipx list | grep pbi-cli-tool`.
   - If empty: stop. Show: "pbi CLI is not installed. Run: `pipx install pbi-cli-tool && pipx ensurepath && pbi skills install`. Open a fresh shell so PATH updates pick up."

2. **Power BI Desktop running with an active project, connection named.**
   - Run `pbi connect` (bare) once to read the port from the "Auto-detected Power BI Desktop on localhost:<port>" line. Disconnect: `pbi disconnect`.
   - Re-connect with an explicit name matching the MCP server's internal label: `pbi connect -d localhost:<port> -n PBIDesktop-<pbip-basename>-<port>`. The model-derived name is required — pbi-cli's default save-name `localhost-<port>` is rejected by the MCP server's measure/table operations with `"Connection 'localhost-<port>' not found"`.
   - If `pbi connect` reports no active project: stop. Show: "Open Power BI Desktop and load a `.pbip` project, then re-run."
   - If the Analysis Services port shifts mid-session (Power BI Desktop sometimes restarts the engine on file reopen, Model-view switch, etc.), re-run this step with the new port.

3. **Active project is `.pbip` (text-format), not legacy `.pbix` binary.**
   - The `pbi connect` output includes the project path. If it ends in `.pbix`: stop. Show: "Save your project as `.pbip` first — File → Save as → set Save as type to Power BI Project. The skill operates on the text-based PBIP format only."

4. **Brand layer importable.**
   - Verify `${WORK_FOLDER_ROOT}/ane_package/reporting/powerbi_dashboard/__init__.py` exists.
   - If missing: stop. Show: "Brand layer not found at `${WORK_FOLDER_ROOT}/ane_package/reporting/powerbi_dashboard/`. Verify OneDrive sync."

## Resolve intent

From the prompt and the most recent analytical artefact in this session, resolve:

- **Indicators** — keys from `MEL_DAX_LIBRARY`. If ambiguous, ask Ane: "Which indicators? Available: {sorted(MEL_DAX_LIBRARY.keys())}".
- **Audience tier** — Tier 1 working brief by default; Tier 2 publication only if the prompt names it.
- **Page set** — default `(indicator_dashboard, equity_disaggregation, methodology_card)` per indicator.
- **Source line** — derive from prior artefact; if absent, ask once.
- **Staging directory** — default `${PWD}/powerbi-build-output/`. Holds theme.json, measures.json, and page recipes for the run.

## Build (Python — produces all artefacts in memory)

```python
import json
from pathlib import Path
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

staging = Path("powerbi-build-output")
staging.mkdir(exist_ok=True)
(staging / "theme.json").write_text(json.dumps(theme, indent=2))
(staging / "measures.json").write_text(json.dumps(measures, indent=2))
for i, page in enumerate(pages):
    (staging / f"page_{page['page_id']}.json").write_text(json.dumps(page, indent=2))
```

## Apply

### 1. DAX measures via `pbi measure create`

For each measure, infer the table from the DAX expression's `[bracketed]` references (heuristic: first `Table[Column]` reference in the expression, or `_Measures` if the expression only references other measures).

```bash
pbi measure create <measure-key> \
    --table <inferred-table> \
    --expression "<dax-expression>"
```

The measure name is positional (NOT a `--name` flag). Verified against `pbi-cli-tool 0.5.6`.

Surface any error verbatim. Never retry — `pbi` failures usually mean the table or column referenced does not exist in the model. `pbi-cli` rolls back the transaction on any "table not found"; the measure does NOT land with a red icon (contrary to older Power BI behaviour). Either pre-seed a stub table or correct the DAX before retry.

### 1a. Save discipline — mandatory after EACH `pbi` model write

Tell Ane to switch to Power BI Desktop and press **Ctrl+S** immediately after each `pbi table` / `pbi measure` / `pbi column` / `pbi relationship` write. External `pbi` writes are held in the Analysis Services engine's memory only; the `.pbip` on disk is updated by Power BI Desktop on File → Save. If the engine restarts before save (port shift, file reopen, sometimes Model-view switch), the writes are lost.

### 2. Theme JSON — direct write into the `.pbip` folder

The `.pbip` is a text-format project. The theme JSON goes into the report folder as a custom theme. Path layout (Power BI Desktop 2.140+):

```
<project>.pbip
<project>.Report/
    StaticResources/
        SharedResources/
            BaseThemes/
                ippf-visual-identity-2025.json   ← write theme here
        RegisteredResources/
            ippf-visual-identity-2025.json       ← also write here
    definition/
        report.json                              ← register the theme (see below)
```

Write the theme JSON to both paths. Then update `report.json` to register it (Power BI Desktop reads the theme name from `report.json` metadata; without registration the theme appears in the Themes gallery but does not auto-apply).

If the user has not enabled the PBIP report-format preview in Power BI Desktop (File → Options → Preview features → Power BI Project (.pbip) source control), the theme path may differ. Surface a clear message if `<project>.Report/` does not exist.

**Cache-bust on retry.** Power BI Desktop caches a registered theme by filename across failed imports — re-importing the same filename re-shows old validation errors even after the file is fixed. On any retry after a validation failure, write the new theme JSON under a versioned name (`ippf-visual-identity-2025-v2.json`, `-v3`, etc.) so Power BI parses it as new.

### 3. Page recipes — staging only in v1

Save each page recipe to the staging directory as JSON. Do NOT attempt to write PBIR page files into the `.pbip` folder in v1 (PBIR format is still in preview and the schema is unstable).

Tell Ane in the chat output exactly which file holds which page recipe and which visuals to create manually:

```
Pages saved to staging — apply manually in Power BI Desktop:

powerbi-build-output/page_cyp_total-dashboard.json
  → New page "cyp_total Dashboard"
  → Card visual: measure [cyp_total], position (40, 40, 280, 120)
  → Line chart: x=Date[Month], y=[cyp_total], position (360, 40, 880, 320)
  → Bar chart: x=Geography[country], y=[cyp_total], position (40, 380, 1200, 280)

(repeat for each page)
```

v2 will automate page creation once the upstream pbi-cli adds report-layer support, or once we wire a direct PBIR writer.

## Output (Tier 1 working brief)

```
Power BI build complete (v1 scope: measures + theme + page recipes).

Measures applied to semantic model: {N} ({list of keys}).
Theme written to: {project}.Report/StaticResources/SharedResources/BaseThemes/ippf-visual-identity-2025.json

Page recipes staged at powerbi-build-output/:
  - page_<id>.json — {N} visuals each. Apply manually per the recipe.

Source: {derived source line}.
```

## Common errors

| Error | Likely cause | Fix |
|---|---|---|
| `pbi: command not found` after install | PATH not updated yet | `pipx ensurepath`; open a fresh shell. |
| `pbi connect` reports no session | Power BI Desktop not running, or no `.pbip` open | Open Power BI Desktop and load a `.pbip`. |
| `pbi measure create` fails: "table not found" | DAX measure references a table absent from the model | Verify the data model matches measure assumptions; add the table or adjust the DAX. |
| Indicator not in `MEL_DAX_LIBRARY` | Adding a new indicator | Add to `dax_library.py` with its wiki entry; PR to anework-package. |
| Theme not applied in Power BI Desktop | PBIP preview feature disabled, or theme not registered in `report.json` | Enable PBIP preview (File → Options → Preview features); check `report.json` carries the theme name. |
| Page recipe says visualType the user can't find | Power BI Desktop UI naming differs from recipe `type` | Use the visual gallery: card = "Card"; lineChart = "Line chart"; barChart / stackedBarChart = "Stacked bar chart"; slicer = "Slicer"; table = "Table"; textbox = "Text box". |
| `pbi measure create` fails: `Connection 'localhost-<port>' not found` | pbi-cli's auto-saved name and the MCP server's internal name differ | Re-connect with `-n PBIDesktop-<pbip-basename>-<port>` — see Pre-flight step 2. |
| `pbi` model writes vanish between commands | AS engine restarted before File → Save | Press Ctrl+S in Power BI Desktop after every `pbi` write. See Apply step 1a. |
| Theme import fails with `oneOf` validation error referencing the same key after a fix | Power BI Desktop cached the previous failed parse by filename | Rewrite the theme JSON under a `-v2` (or `-v3`) filename and re-browse. See Apply step 2. |
| `pbi table refresh` fails with `Invalid operation: Refresh` | pbi-cli 0.5.6 sends `Refresh` op-name; MCP server only accepts `REFRESHWITHXMLA` / `REFRESHWITHAPI` | Upstream pbi-cli bug. Workaround: trigger refresh manually in Power BI Desktop (Home → Refresh). |
| `pbi measure get` or `pbi table export-tmdl` fails with `References is required` | pbi-cli 0.5.6 doesn't pass the References parameter to the MCP server | Upstream pbi-cli bug. Use `pbi measure list --table <name>` to confirm a measure exists; use Power BI Desktop's Tabular Editor view for TMDL inspection. |
