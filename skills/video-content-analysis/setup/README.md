# video-content-analysis — installer

One-command installer for the toolchain the video-content-analysis skill needs.

## What it installs

| Component | Source | Disk |
|---|---|---|
| ffmpeg | winget (Gyan.FFmpeg) | ~150 MB |
| Python 3.11 | Python Install Manager (`py install 3.11 --yes`, no admin) | ~150 MB |
| Dedicated venv | py -3.11 -m venv | — |
| faster-whisper + pyannote.audio | pip | ~650 MB |
| Whisper large-v3 model (optional) | HuggingFace | ~3 GB |
| pyannote speaker-diarization-3.1 | HuggingFace (gated) | ~500 MB |

Total: ~4.5 GB after first-run model downloads.

## Run

```powershell
cd "C:/Users/AGasser/OneDrive/GitHub/personal-skills/skills/video-content-analysis/setup/"
./setup-video-pipeline.ps1
```

The installer is idempotent. Safe to re-run; it skips components already installed.

## Options

| Flag | Effect |
|---|---|
| `-SkipDiarization` | Skip pyannote.audio install + HuggingFace token capture. Diarization will not work until re-run without this flag. |
| `-DeferModelDownload` | Skip the upfront 3 GB Whisper large-v3 download. First analyze-video run downloads it instead. |

## Pre-requisites

- Windows 10/11 with PowerShell 7+
- `py` launcher (3.13+) on PATH. If absent, install per-user via the Python.org Windows installer (no admin needed; choose "Install Python launcher").
- winget (install via Microsoft Store if missing: https://aka.ms/getwinget)
- ~6 GB free disk space
- HuggingFace account (free, only needed for diarization). Create at https://huggingface.co
- Token at https://huggingface.co/settings/tokens
- Accept gated model terms at https://huggingface.co/pyannote/speaker-diarization-3.1

**No admin rights required.** ffmpeg installs via winget `--scope user`. Python 3.11 installs via the Python Install Manager (PIM) into user scope. All other components install into the user-scoped venv or user profile.

## What "ready" looks like

The installer ends with a summary box like:

```
===================================================================
  video-content-analysis Stage 1 install complete.
===================================================================
  Components:
    [OK]   ffmpeg (C:\...\ffmpeg.exe)
    [OK]   Python 3.11 (Python 3.11.x)
    [OK]   venv (C:\...\venv)
  Log: C:\...\install.log
  Re-run safely; the installer is idempotent.
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `winget not found` | winget not installed | Install from Microsoft Store: https://aka.ms/getwinget |
| `py launcher missing` (Stage 1.5 FAIL) | py launcher not installed or pre-3.13 | Install per-user from python.org; reopen PowerShell; re-run installer |
| `py -3.11` not found after install | PATH not refreshed after PIM install | Open a new PowerShell session, re-run installer (idempotency makes this safe) |
| `pip install` hangs | Network / proxy | Check `pip --version`; retry on a different network |
| `pyannote.audio` import fails with `AudioMetaData` AttributeError | torchaudio >=2.7 installed | Verify requirements.txt pins torch+torchaudio<2.7; re-run installer |
| Smoke test fails with `ImportError` | Wrong venv | Delete `<skill>/venv/`, re-run installer |
| HuggingFace token rejected | Invalid token or terms not accepted | Verify token + accept gated model terms; re-run |

## Uninstall

```powershell
# Remove venv (frees ~650 MB plus models if downloaded)
Remove-Item -Recurse -Force "C:/Users/AGasser/OneDrive/GitHub/personal-skills/skills/video-content-analysis/venv/"

# Remove HuggingFace token from Credential Manager
cmdkey /delete:IPPF-MEL-Video-HuggingFace

# Optionally remove ffmpeg via winget
winget uninstall Gyan.FFmpeg

# Optionally remove Python 3.11 via PIM
py uninstall 3.11
```
