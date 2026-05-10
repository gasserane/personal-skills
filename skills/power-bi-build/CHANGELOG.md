# Power BI Build Skill — Changelog

## 1.0.1 — 2026-05-10

Smoke-test driven fixes from the manual smoke run against `pbi-cli-tool 0.5.6` + Power BI Desktop on 2026-05-10. All findings logged in `mel_wiki/wiki/concepts/power-bi-dashboard-smoke.md` smoke-log row.

- **Apply → 1: `pbi measure create` syntax corrected.** The measure name is positional (`pbi measure create NAME --table T --expression "..."`), NOT a `--name` flag. v1.0.0 documented the wrong shape.
- **Apply → 1: clarified rollback behaviour.** When the referenced table is missing, `pbi-cli` rolls back the transaction; the measure does NOT land with a red icon. Pre-seed a stub table for empty-`.pbip` demos.
- **Apply → 1a (new): save discipline rule.** External `pbi` writes live in AS engine memory until Power BI Desktop's File → Save. If the engine restarts before save (port shift, file reopen, Model-view switch), the writes are lost. Rule: press Ctrl+S after every `pbi` write.
- **Pre-flight → 2: connection naming workaround.** `pbi connect` saves connections as `localhost-<port>`; the MCP server's measure/table operations expect `PBIDesktop-<pbip-basename>-<port>`. Use `pbi connect -n PBIDesktop-...` explicitly.
- **Apply → 2: theme cache-bust note.** Power BI Desktop caches a registered theme by filename across failed imports — re-importing the same filename re-shows old validation errors. Rename to `-v2`/`-v3` to bust.
- **Common errors table:** added 5 new rows for the above + 2 upstream `pbi-cli-tool 0.5.6` bugs (`pbi table refresh`, `pbi measure get` / `pbi table export-tmdl`).

Companion fix in `anework-package`: `theme.py` `gridlineColor` emitted as bare string; Power BI requires `{"solid": {"color": "#XXX"}}` wrapper. Already committed there.

## 1.0.0 — 2026-05-10

- Initial release. v1 scope is constrained by the actual capabilities of `pbi-cli-tool 1.0.6` (binary name `pbi`):
  - DAX measures applied via `pbi measure create`.
  - IPPF theme JSON written directly to `<project>.Report/StaticResources/...`.
  - Page recipes saved to `powerbi-build-output/` as JSON; user creates pages and visuals manually in Power BI Desktop following the recipe.
- Pre-flight checks: pbi installed, Power BI Desktop running, .pbip active, brand layer importable.
- Imports brand layer from `${WORK_FOLDER_ROOT}/ane_package/reporting/powerbi_dashboard/`.
- Theme + 11 DAX measures + 3 page recipes (indicator dashboard, equity disaggregation, methodology card).
- Tier 1 working brief output by default.
- Page-ID sanitisation at the CLI boundary.
- Notes on factual corrections from the live install: command name is `pbi` (not `pbi-cli`); `pbi skills install` produces 5 skills, not 12.
- See `docs/superpowers/specs/2026-05-10-power-bi-dashboard-capability-design.md` in the anework-package repo for the original design. The pbi-cli command-name claims and skill-count in that spec are superseded by this CHANGELOG.
