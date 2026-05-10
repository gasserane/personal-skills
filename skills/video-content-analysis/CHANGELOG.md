# Changelog

All notable changes to the video-content-analysis skill.

Format: Keep a Changelog (https://keepachangelog.com/en/1.1.0/).
Versioning: Semantic Versioning (https://semver.org/).

## [0.6.0-stage6] — 2026-05-10

### Added
- Calibration anchors page at `mel_wiki/wiki/calibration/video-content-analysis.md` — seven operational quality anchors per spec Section 8 mechanism 3.
- `ane_package/video/retrospective.py` — `should_run_retrospective`, `read_telemetry`, `compute_anchor_performance`, `identify_recurring_failures`, `write_retrospective`, `update_state`.
- `prompt_save_fixture` in `ane_package/video/feedback.py` — tier-gated regression-fixture save offer per spec Section 8 mechanism 5.
- Tier 2 fixture pipeline runner `tests/video/test_fixture_pipeline.py` invoked via `python tests/run_tests.py --fixtures`.
- Two committed fixture scaffolds: `synthetic-romanian-fgd-30s/` and `sbcc-public-15s/` (source.mp4 user-supplied per fixture README).
- `## Reading a video-content-analysis manifest` section added to four specialist files: `qualitative-coding-specialist.md`, `intersectionality-analyst.md`, `sbcc-campaign-mel-specialist.md`, `gender-transformative-assessor.md`.
- Installer probe step `Confirm-PyannoteGatedTerms` — verifies pyannote gated-terms acceptance via HuggingFace API before first diarization run.
- Six new static harness checks: `video.calibration_anchors_published`, `video.specialist_manifest_sections`, `video.retrospective_module_present`, `video.fixture_pipeline_runner_present`, `video.first_fixture_dir_present`, `video.second_fixture_dir_present`.
- `--retrospective` flag in skill (`/analyze-video --retrospective`) reads telemetry, writes recommendation document; never auto-applies.
- `--fixtures` flag in `tests/run_tests.py` dispatches to Tier 2 fixture runner.
- `jsonschema>=4.21` added to `setup/requirements.txt`.
- `source.hash` field on manifest (16-hex SHA-256 of source content) for fixture-save keying and telemetry.
- `network_egress` field added to telemetry allowlist.
- Auto-saved fixtures land at `tests/video/fixtures/auto/` (gitignored).

### Changed
- `check_video_manifest_schema_present` now uses `jsonschema.Draft202012Validator.check_schema` (full schema validation, not shape-only). Smoke test exercises the harness function end-to-end.
- SKILL.md frontmatter `version: 0.6.0-stage6` (was `0.5.0-stage5`).
- `update_state` semantics: when both `retrospective_ran` and `increment` are passed, reset happens BEFORE increment so a coincident successful run starts the new cycle at count=1 (not 0).
- `compute_anchor_performance` Anchor 5 now references `audio_quality_flags[]` (matches schema reality); confidence-based extension explicitly gated on Stage 4.5 alignment.
- `compute_anchor_performance` Anchor 3 prefers `network_egress` field, falls back to engine-as-proxy, treats engine=None on sensitive rows as DATA_GAP rather than silent PASS.

### Fixed
- `_read_hf_token_from_credential_manager` distinguishes "credential missing" (CredRead exit 2 → silent None) from genuine PowerShell errors (anything else → log to stderr).
- `_patch_torch_load_compat` docstring expanded to mention the omitted-`weights_only` case (in addition to explicit None).
- Installer's gated-terms probe uses single BSTR allocation with proper zero-free in `finally`.
- Tier 2 fixture runner defers heavy imports past existence checks — clean "source not present" message on missing source.mp4 even when venv lacks pyannote/soundfile.
- `expected_manifest.json` files no longer assert on `source.duration_seconds` / `source.format_name` (brittle source-echo).

### Closes
- Stage 5 deferred items: real `jsonschema` validation; calibration anchors page; retrospective protocol; test fixture growth from real failures; specialist `.md` updates × 4; installer gated-terms acceptance check; two non-blocking diarization items.

### Out-of-scope (deferred to v2 / future stages)
- Live populating `source.mp4` and `transcript.gold.json` for both Tier 2 fixtures (user-contribution step).
- Wiring a `scene_change` knob through `analyze_video` so the SBCC fixture can exercise scene-change frame extraction (currently interval-only).
- Wiring a runner CLI flag `--m365-caption` through the Tier 2 fixture runner.
- Refactor of duplicate `check_video_first_fixture_dir_present` and `check_video_second_fixture_dir_present` into a single list-driven check.
- Re-probing gated-terms on installer re-runs when token already stored (currently bypassed by idempotent skip-path).
- Telemetry per-segment `confidence` field (gated on Stage 4.5 alignment work).
- Pushing `tests/video/fixtures/auto/` redaction to a fixtures.py module.

## [0.1.0-stage1] - 2026-05-08

### Added
- Skill directory scaffolding under personal-skills/skills/video-content-analysis/.
- One-command Windows installer (setup/setup-video-pipeline.ps1) covering:
    - ffmpeg via winget
    - Python 3.11 via winget (Windows Store stub-aware)
    - Dedicated venv at skills/video-content-analysis/venv/
    - faster-whisper and pyannote.audio
    - HuggingFace token capture into Windows Credential Manager
    - Whisper large-v3 model download (opt-in upfront vs defer)
    - Post-install smoke test
- Pester-tested install-state detection module (setup/InstallDetect.psm1).
- README for installer use.

### Verified
- End-to-end install completed on dev machine 2026-05-08.
- Smoke test passes (faster-whisper tiny model loads, transcribes 5-second silence WAV in ~6s).
- Idempotency confirmed: re-run skips all install steps and only runs smoke test.
- Pester tests pass (11/11 for InstallDetect.psm1 covering version-comparison fast/fallback paths).
- pytest passes (2/2 for smoke-test.py).
- Baseline state captured in setup/baseline-install-2026-05-08.txt.
- No admin rights required (PIM for Python; winget --scope user for ffmpeg).

### Hot-fixes during stage
- 1.4.5 — Fixed Test-RealPythonInstalled to verify version meets MinimumVersion (was returning true on any non-Store Python regardless of version). Added winget exit code -1978335189 ("already installed") to success whitelist. Replaced Invoke-Expression with call operator + Invoke-PyLauncher helper for testability.
- 1.5 — Pivoted Python 3.11 install from winget to Python Install Manager (py install 3.11 --yes) to support no-admin IPPF-managed devices.
- 1.7 — Pinned torch+torchaudio<2.7 because pyannote.audio 3.4.0 expects torchaudio.AudioMetaData (removed in 2.7).

### Calibration anchors affected
- None. Stage 1 produces no telemetry; calibration anchors begin populating in Stage 4.

## [0.2.0-stage2] - 2026-05-09

### Added
- `ane_package/video/` Python primitives (in anework-package repo):
    - `probe_video` — ffprobe wrapper returning structured `VideoProbe`.
    - `extract_audio` — ffmpeg wrapper, 16 kHz mono PCM WAV by default.
    - `extract_frames` — ffmpeg I-frame + scene-change + fixed-interval frame extraction (filter expression `eq(pict_type,I)+gt(scene,X)`; see Stage 2.7 deviation note in plan).
    - `transcribe` — faster-whisper wrapper returning structured `TranscriptionResult` with word-level timestamps.
- `tests/video/fixtures/synthetic-30s.mp4` — 30 s synthetic colour-bars + 440 Hz sine wave fixture; deterministic, free of participant content.
- `tests/smoke_video_primitives.py` — end-to-end smoke test covering all four primitives.
- Three static checks in `tests/run_tests.py` (work-folder) guarding package layout, fixture presence, smoke-script presence.
- `setup/constants.psd1` + `setup/constants.py` (this repo) — single source of truth for the HuggingFace credential target name (`IPPF-MEL-Video-HuggingFace`) and Whisper default model (`large-v3`).

### Changed
- Stage 1 carry-over polish — chore commits `efb3ad6` (initial 14 fixes) and `2b4fcbe` (follow-up):
    - I1-I4: variable rename in `Get-WhisperModel`, path canonicalisation for `$script:VenvPath`, native-exe stdout capture before `$LASTEXITCODE` test, `Test-PipDependenciesInstalled` predicate for clean idempotent re-run.
    - M1-M9: numpy<2.0 pin, cmdkey behaviour note, fail-fast on PATH staleness, broader skip-affirmative parsing, smoke-test exit-code semantics, `-NonInteractive` flag, `__pycache__` gitignore, `Generate-TestFixture` clarification, `Get-Command py` mock fix.
- HuggingFace credential name centralised in `setup/constants.psd1` + `setup/constants.py` (commit `95a9b7c`). One literal in PS1 before, zero after; README points at the canonical file.

### Calibration anchors affected
- None populated yet. Anchors begin populating in Stage 4 (telemetry).

### Deferred to later stages
- Manifest schema + assembler + `summary.md` generator → Stage 3.
- Diarization + privacy/consent enforcement + telemetry → Stage 4.
- M365 Stream adapter + skill (`/analyze-video`) + subagent (`video-content-analyst`) → Stage 5.
- Calibration anchors page + retrospective protocol + remaining test fixtures + specialist `.md` updates → Stage 6.
- `extract_frames` real-video frame-cap (current I-frame union may emit hundreds of frames on long FGD recordings; Stage 5 callers should pass higher `scene_threshold` or use interval strategy exclusively).

## [0.3.0-stage3] - 2026-05-09

### Added
- `ane_package/video/manifest.py` — `build_manifest(probe, audio, frames, transcription, output_dir, *, skill_version)` writes manifest.json matching the full Section 7 schema. Privacy / consent / diarization / audio_quality_flags / data_gaps / downstream_routing_hints fields populated as placeholders for Stages 4-5 to fill in.
- `ane_package/video/summary.py` — `generate_summary(manifest, output_path)` writes Tier 1 BLUF summary.md. Plain markdown; Stage 5 wraps via word_export for the IPPF brand template.
- `ane_package/video/schemas/manifest_v1.schema.json` — JSON Schema (Draft 2020-12) describing the full Section 7 manifest shape.
- `tests/manual/integration_real_video.py` — long-running manual script exercising the full pipeline on a real video.
- 3 new static checks in `tests/run_tests.py` (105/105 total).

### Changed
- `extract_frames` defaults flipped from `scene_change=True` to `scene_change=False`. Reasoning: 64.5-min IPPF launch recording produced 848 frames with the Stage 2 default; the I-frame clause in the Stage 2.7 deviation matches every encoder keyframe regardless of `scene_threshold`. Interval-only is the safer default for real Teams / webinar content. Callers wanting scene detection pass `scene_change=True` explicitly.
- `extract_frames` adds `max_frames: int | None = None` parameter with uniform downsampling. Pruned PNGs are deleted from disk.

### Deferred to later stages
- `jsonschema` package + real schema validation -> Stage 6 (requires installer change).
- Privacy enforcement, consent metadata population, diarization -> Stage 4.
- M365 Stream adapter, skill orchestrator, subagent -> Stage 5.
- IPPF brand-template wrapping of summary.md (Word/PDF) -> Stage 5 via word_export.
- Calibration anchors page, retrospective protocol -> Stage 6.

### Known carry-overs
- `ane_package/video/__init__.py` still does NOT re-export the four function symbols (`extract_audio`, `extract_frames`, `probe_video`, `transcribe`). Stage 5 wires these back when the skill orchestrator lands. Type re-exports include the new `VideoManifest` and `VideoSummary` dataclasses.

## [0.4.0-stage4] - 2026-05-09

### Added
- `ane_package/video/privacy.py` — `validate_privacy(tier, engine, *, diarization_used)` enforces "no silent escalation" per spec Section 6 hard guarantee #1. `write_network_log(path, tier, engine, egress)` writes the audit trail per guarantee #2.
- `ane_package/video/consent.py` — `validate_consent` blocks `consent_unclear` runs; `is_publication_cleared` gates Tier 2 quote use.
- `ane_package/video/diarization.py` — `diarize(audio_path, *, hf_token, num_speakers)` wraps `pyannote.audio.Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")`. HF token retrieved from Windows Credential Manager via inline PowerShell `CredRead` shim.
- `ane_package/video/alignment.py` — `align_speakers(transcription, diarization)` returns a new `TranscriptionResult` with `segment.speaker` populated by majority temporal overlap.
- `ane_package/video/quality.py` — `detect_audio_quality_flags(audio_path)` detects `low_volume` (-20 dBFS / 5s windows), `clipping` (>= 0.99 amplitude), `long_silence` (-50 dBFS / 10s windows).
- `ane_package/video/telemetry.py` — `record_run(event)` appends JSONL operational metrics. Allowlist-enforced — participant-content keys raise `TelemetryError`.
- `PrivacyTier`, `PrivacySettings`, `ConsentStatus`, `ConsentMetadata`, `SpeakerTurn`, `DiarizationResult`, `AudioQualityFlag` types in `ane_package/video/types.py`. `TranscriptSegment` extended with optional `speaker: str | None = None`.

### Changed
- `build_manifest` accepts new optional kwargs: `privacy`, `consent`, `diarization`, `audio_quality_flags`. Backward-compatible: omitting them keeps the Stage 3 placeholder values.
- When `consent.status == "consent_unclear"` is passed explicitly, `build_manifest` appends a `Data gap: consent_unclear ...` line per CLAUDE.md data-gap protocol.

### Compatibility patches (Stage 4.5 diarization)
- Three upstream incompatibilities surfaced and were patched inside `diarization.py`:
  1. PowerShell 7 `Add-Type -UsingNamespace` "duplicate using directive" error → switched to `Add-Type -TypeDefinition` with inline `using` directives.
  2. `huggingface_hub` 1.14.0 dropped `use_auth_token` parameter → `_patch_hf_hub_compat()` remaps `use_auth_token` -> `token` for pyannote callers.
  3. `torch` 2.6 changed `weights_only=None` default to True → `_patch_torch_load_compat()` normalises `None` to `False` (pyannote checkpoints are trusted local files).
- Each patch is idempotent and scoped to the diarization import path. Stage 6 should remove these once upstream libraries align.

### Deferred to later stages
- M365 Stream/Teams adapter (engine=`m365-stream` is recognised by `validate_privacy` but the actual fetch is Stage 5).
- Interactive consent capture prompt → Stage 5 (skill orchestrator).
- `record_run` calls inside the pipeline → Stage 5 (orchestrator wires telemetry calls per stage).
- Calibration anchors page + retrospective protocol → Stage 6.
- Real `jsonschema` validation of manifest → Stage 6.
- `ane_package/video/__init__.py` function-symbol re-exports → Stage 5.
- Robust `keyring`-based HF token retrieval → Stage 6 alongside the installer dependency upgrade.

### Known carry-overs
- `__init__.py` re-exports types only (17 symbols after Stage 4).
- Two non-blocking minor items from the Stage 4.5 review: (a) `_read_hf_token_from_credential_manager` could log PowerShell stderr when CredRead fails for non-missing reasons; (b) `_patch_torch_load_compat` docstring should clarify the patch also fires when `weights_only` is omitted.
- The diarization smoke test downloads ~500 MB on first run if the user has not already accepted the `pyannote/speaker-diarization-3.1` gated terms.

## [0.5.0-stage5] - 2026-05-09

### Added
- `ane_package/video/orchestrator.py` — `analyze_video(input_path, *, privacy_tier, consent, language, diarize, brand_summary, output_dir, m365_caption_path, telemetry_path)`. End-to-end pipeline. Validates privacy + consent before any primitive runs. Wraps every stage in `time.perf_counter`. Calls `record_run` once at the end with operational keys only. Returns `AnalysisResult`.
- `ane_package/video/m365_stream.py` — `parse_vtt(vtt_path) -> TranscriptionResult` for the M365 Stream/Teams caption path. `fetch_caption_via_graph(file_id, *, access_token, out_path)` for the direct-HTTP path used by Vi-spawned subagents and manual integration. Skill (Claude Code) prefers the connected Microsoft 365 MCP server. UTF-8 BOM stripped automatically.
- `ane_package/video/routing.py` — `populate_routing_hints(manifest)` returns a per-specialist `{ready, notes}` dict for the four manifest-consuming specialists named in spec Section 10.
- `ane_package/video/feedback.py` — `prompt_verdict(*, timeout_s=30, stream=None)` returns `(Verdict, str | None)`. Defaults to `Verdict.SKIP` on EOF, blank line, unrecognised letter. Banner reflects the actual EOF/blank-line skip behaviour.
- `ane_package/video/_brand_summary.py` — manifest -> `WordReport` mapper used when `brand_summary=True`. Routes through `ane_package.reporting.word_export.write_word_report` for IPPF Visual Identity 2025.
- `AnalysisResult`, `Verdict`, `RoutingHint` types in `ane_package/video/types.py`.
- `~/.claude/skills/video-content-analysis/SKILL.md` — full Tier 1 skill content. Replaced the Stage 1 scaffolding placeholder. Version `0.5.0-stage5`.
- `~/.claude/agents/video-content-analyst.md` — Vi-spawnable subagent. Captured into `claude-config` via the `sync-from-local.sh` workflow.
- `agent-improvements/agent_registry.md` — `### video-content-analyst` entry registered for Vi's SELECT phase.
- Seven new static harness checks: `video.orchestrator_module_present`, `video.m365_stream_module_present`, `video.routing_module_present`, `video.feedback_module_present`, `video.skill_full`, `video.subagent_present`, `video.analyst_in_registry`.
- Brand-summary dependencies pinned in `setup/requirements.txt`: python-docx, lxml, xlsxwriter.

### Changed
- `ane_package/video/__init__.py` — exports the 12 function-style primitives + 20 types (32 symbols total). Submodule-direct imports remain valid.
- `tests/manual/integration_real_video.py` — switched from bare-primitive composition to a single `analyze_video(...)` call exercising the brand-summary path.

### Deferred to Stage 6
- Calibration anchors page at `mel_wiki/wiki/calibration/video-content-analysis.md`.
- Retrospective protocol `/analyze-video --retrospective`.
- Test fixtures `synthetic-romanian-fgd-30s/` and `sbcc-public-15s/` with expected_manifest.json + expected_summary.md.
- Specialist `.md` updates (qualitative-coding-specialist, intersectionality-analyst, sbcc-campaign-mel-specialist, gender-transformative-assessor) — the 8-12-line "Reading a video-content-analysis manifest" section.
- Real `jsonschema` validation.
- Gated-terms acceptance check in the installer.
- The two minor non-blocking diarization items.
- Real polling-based timeout for `prompt_verdict` if Ane wants TTY-side timeout behaviour.
- Real-video integration timing capture in `tests/manual/README.md` — Stage 5.10 ran the integration partially (network.log + audio.wav written; transcription not completed within the implementer-session timeout).

### Known carry-overs
- Skill calls `prompt_verdict` after the orchestrator returns; this means telemetry receives one operational line per run plus an optional verdict-update line. Stage 6 collapses these.
- Brand-summary path uses the existing `WordReport` dataclass with a single mapper; field choices are intentionally minimal in v1 and refactor freely as Ane reviews live output.
- Subagent's manifest schema validation is structural only (Stage 6 wires real `jsonschema`).
