# Power BI Build Skill — Changelog

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
