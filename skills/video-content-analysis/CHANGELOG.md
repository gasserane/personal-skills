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

### Calibration anchors affected
- None. Stage 1 produces no telemetry; calibration anchors begin populating in Stage 4.
