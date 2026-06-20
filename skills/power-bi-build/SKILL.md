---
name: power-bi-build
description: Build IPPF-branded Power BI artefacts from analytical input. Use when Ane asks to build, scaffold, or update a Power BI dashboard, semantic model, DAX measures, or .pbip project. Applies IPPF Visual Identity 2025 brand, MEL-standard DAX measures, and three standard page recipes (indicator dashboard, equity disaggregation, methodology card). Requires the pbi CLI (pbi-cli-tool, command name `pbi`) installed and Power BI Desktop running with a .pbip open.
version: 1.1.0
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

**Two routes.** The v1 flow below (`pbi` CLI for measures + theme + staged page recipes) suits an existing model the user keeps building by hand. When the source is an **Excel workbook** and the user wants a **complete, working dashboard handed over** (data loaded, measures, theme, and report pages all built), use the **full `.pbip` authoring route** in the dedicated section below instead. That route was validated end-to-end (CERV Portfolio Dashboard, 2026-06-20).

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

## Full `.pbip` authoring from Excel (full-handover route)

Use when the source is an Excel workbook and the user wants a complete working dashboard, not staged recipes. Author the entire `.pbip` from a **Python generator** (one re-runnable script), because the `pbi` CLI cannot import Excel data (DataSourceOperationsTool is skipped in PowerBI compat mode) and has no report page/visual API. Reference build: `${WORK_FOLDER_ROOT}/scripts/gen_cerv_dashboard_pbip.py`.

**Apply `mel_wiki/wiki/concepts/edit-preservation-protocol.md` when the target `.pbip` already exists.** Author into a NEW project folder if the user has the target open (avoids the file lock); they close-without-saving and reopen.

**Procedure:**
1. **Mirror the schema.** Read an existing empty `.pbip`'s skeleton and copy its exact versions (compatibilityLevel 1600; report.json 3.3.0; visual 2.9.0; page 2.1.0; pbism 4.2). Require the PBIP + PBIR preview features enabled in Desktop.
2. **Inspect the Excel** with openpyxl: sheet names, exact header strings (no stripping — trailing spaces break column refs), header row position, and value types per column. Reconcile expected aggregates against any existing in-workbook dashboard tabs.
3. **Author the SemanticModel TMDL** (TAB-indented): `database.tmdl`, `model.tmdl` (with `ref table X` lines + `relationship` blocks), `cultures/`, and `tables/*.tmdl` (columns + measures + an M `partition`). The M block is indented deeper than `source =`.
4. **Author the report PBIR**: `definition.pbir` (relative `byPath` to the SemanticModel — this link survives folder moves), `report.json` (register the IPPF custom theme + base theme), `pages/<id>/page.json`, and `pages/<id>/visuals/<id>/visual.json`.
5. **Reconcile measures** against source aggregates, then have the user open + Refresh. After load, verify via the CLI: `pbi connect`, then `pbi dax execute "EVALUATE <Table>"` and read `RowCount=` (the CLI does NOT print cell values; use a table EVALUATE and read the row count).

**Power Query M gotchas (each cost a refresh-error cycle — apply pre-emptively):**
- `Excel.Workbook(File.Contents(path), null, true)` **drops leading fully-blank rows**, so a fixed `Table.Skip(n)` misaligns the header. Locate it dynamically: `HeaderRow = List.PositionOf(Sheet[Column1], "<key header>")`, then `Table.Skip(Sheet, HeaderRow)`, then `Table.PromoteHeaders(.., [PromoteAllScalars=true])`.
- It is `List.PositionOf` (list + value), NOT `Table.PositionOf` (table + record) — the latter throws "cannot convert List to Table".
- **Only hard-type columns the dashboard needs** (amounts → `type number`, counts → `Int64.Type`). Typing computed / "(auto)" columns throws per-cell "N errors" when they return non-numeric ("" / "Pending") for not-yet-filled rows. Leave those untyped.
- Multi-row / merged-header sheets: skip PromoteHeaders; use positional `Table.Range` + `Table.SelectColumns({"Column1",...})` + rename.
- M file paths are literal (no backslash escaping). Put the source path once in a shared expression or inline consistently.

**PBIR visual JSON (authored blind, all rendered correctly):** minimal `visual.query.queryState.<role>.projections[{field:{Measure|Column:{Expression:{SourceRef:{Entity}},Property}}, queryRef:"Entity.Prop", nativeQueryRef:"Prop"}]`. Roles: `card`→`Values`; `clusteredColumnChart`/`clusteredBarChart`→`Category`+`Y` (omit `Category` for a multi-measure chart); `tableEx`→`Values` (list). Omit title objects — let the IPPF theme and auto-titles style everything. Extras: slicer multi-select + Select-all = `objects.selection[{properties:{singleSelect:{Literal false}, selectAllCheckboxEnabled:{Literal true}}}]`; nav bar = visualType `pageNavigator`; logo = visualType `image` with `ResourcePackageItem(RegisteredResources)` + copy the PNG into `StaticResources/RegisteredResources/` + register in report.json; header band = textbox with `visualContainerObjects.background`.

**Layout that reads well (1280×720):** compact full-width slicer strip (slicers render as dropdowns), KPI cards row, then large charts spanning the full width — avoid a part-width slicer row that wastes the band to its right. Set page `displayOption` to `FitToWidth` so it fills the monitor and scrolls vertically.

## Distribution & licensing (advise the user)

- `.pbip` is a **dev/source-control format** — it opens **empty until refreshed**, wrong for novices.
- For novice viewers, hand out a **`.pbix`** (File → Save As → `.pbix` embeds the data, opens populated, needs no licence). Only Power BI Desktop can write a `.pbix`; no CLI/script can, and embedding data needs a live refresh first.
- **Power BI Service** publishing lets free-tier colleagues view ONLY if the workspace is on **Premium (P SKU) or Fabric F64+ capacity**; otherwise every viewer also needs **Pro/PPU**. Never use "Publish to web" for sensitive (SRHR / finance / sub-grantee) data — it is public.
- The page-navigator and buttons navigate on **single-click in Reading view / published**, **Ctrl+click in Editing view** (inherent Power BI behaviour, not a bug).
- An Excel source referenced by absolute local/OneDrive path **breaks if moved to SharePoint**. Repoint via the SharePoint connector for cloud scheduled refresh; refresh re-reads the source each time.

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
| Refresh: "The column '<key>' of the table wasn't found" (promote-header tables) | `Excel.Workbook` dropped a leading blank row, so a fixed `Table.Skip` misaligned the header | Find the header dynamically: `Table.Skip(Sheet, List.PositionOf(Sheet[Column1], "<key>"))`. See full-authoring route. |
| Refresh: "We cannot convert a value of type List to type Table" | Used `Table.PositionOf` on a column | Use `List.PositionOf(list, value)`, not `Table.PositionOf(table, record)`. |
| Refresh: "N rows loaded. M errors" on one table | A typed computed/"(auto)" column returns non-numeric for not-yet-filled rows | Drop the type conversion on that column; type only columns the dashboard needs. |
| Report opens but every visual is blank after refresh | Import model loaded 0 rows (M failed) — not a binding bug | Connect with `pbi`, run `pbi dax execute "EVALUATE <Table>"`, read `RowCount=`; fix the M, not the visuals. |
| Recipient opens the `.pbip` to an empty report | `.pbip` stores no data; opens empty until refresh | Distribute a `.pbix` (embeds data) or publish to Service. See Distribution & licensing. |
