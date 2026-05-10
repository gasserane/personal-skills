# Power BI Build Skill — Changelog

## 1.0.0 — 2026-05-10

- Initial release.
- Pre-flight checks: pbi-cli installed, Power BI Desktop running, .pbip active, brand layer importable.
- Imports brand layer from `${WORK_FOLDER_ROOT}/ane_package/reporting/powerbi_dashboard/`.
- Theme + 11 DAX measures + 3 page templates (indicator dashboard, equity disaggregation, methodology card).
- Tier 1 working brief output by default.
- Page-ID sanitisation at the CLI boundary.
- See `docs/superpowers/specs/2026-05-10-power-bi-dashboard-capability-design.md` in the anework-package repo for the design.
