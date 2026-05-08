# Changelog

All notable changes to the video-content-analysis skill.

Format: Keep a Changelog (https://keepachangelog.com/en/1.1.0/).
Versioning: Semantic Versioning (https://semver.org/).

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
