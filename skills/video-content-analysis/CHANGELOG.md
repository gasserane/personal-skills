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
