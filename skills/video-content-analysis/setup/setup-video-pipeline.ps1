#Requires -Version 7.0
<#
.SYNOPSIS
    Installer for the video-content-analysis skill toolchain.

.DESCRIPTION
    Idempotent. Installs ffmpeg, Python 3.11, dedicated venv, faster-whisper,
    pyannote.audio, captures HuggingFace token, optionally downloads Whisper
    large-v3 model, runs smoke test.

.PARAMETER SkipDiarization
    Skip pyannote.audio install and HuggingFace token capture.
    Diarization will be unavailable until installer re-run with diarization enabled.

.PARAMETER DeferModelDownload
    Skip the upfront Whisper large-v3 model download. First transcription run
    will download it instead (~3 GB, 5-10 min on typical broadband).

.EXAMPLE
    ./setup-video-pipeline.ps1
    Full install with prompts.

.EXAMPLE
    ./setup-video-pipeline.ps1 -SkipDiarization -DeferModelDownload
    Minimal install, skip diarization and defer model.
#>
[CmdletBinding()]
param(
    [switch]$SkipDiarization,
    [switch]$DeferModelDownload
)

$ErrorActionPreference = 'Stop'
$script:LogFile = Join-Path $PSScriptRoot 'install.log'
$script:VenvPath = Join-Path $PSScriptRoot '..' 'venv'

Import-Module (Join-Path $PSScriptRoot 'InstallDetect.psm1') -Force

function Write-Step {
    param([string]$Message, [ValidateSet('INFO','OK','SKIP','WARN','FAIL')][string]$Level='INFO')
    $stamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'
    $line = "[$stamp][$Level] $Message"
    Write-Host $line
    Add-Content -Path $script:LogFile -Value $line
}

function Confirm-DiskSpace {
    param([int]$RequiredGB = 6)
    $drive = (Get-Item $PSScriptRoot).PSDrive
    $freeGB = [math]::Round($drive.Free / 1GB, 1)
    if ($freeGB -lt $RequiredGB) {
        Write-Step "Insufficient disk space: ${freeGB}GB free, ${RequiredGB}GB required" 'FAIL'
        $reply = Read-Host "Continue anyway? [y/N]"
        if ($reply -notmatch '^[Yy]') { exit 1 }
    } else {
        Write-Step "Disk space check: ${freeGB}GB free (${RequiredGB}GB required)" 'OK'
    }
}

function Install-FFmpeg {
    if (Test-FFmpegInstalled) {
        Write-Step "ffmpeg already installed at $((Get-Command ffmpeg).Source)" 'SKIP'
        return
    }
    Write-Step "Installing ffmpeg via winget (Gyan.FFmpeg)..." 'INFO'
    & winget install Gyan.FFmpeg --scope user --accept-source-agreements --accept-package-agreements --silent | Out-Null
    $wingetExit = $LASTEXITCODE
    # winget exit codes treated as success:
    #   0           = installed
    #   -1978335189 = already installed (APPINSTALLER_CLI_ERROR_PACKAGE_ALREADY_INSTALLED, 0x8A15002B)
    if ($wingetExit -ne 0 -and $wingetExit -ne -1978335189) {
        Write-Step "ffmpeg install via winget failed (exit $wingetExit)" 'FAIL'
        throw "ffmpeg install failed."
    }
    # Refresh PATH for the current session
    $env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
    $ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if (-not $ffmpegCmd) {
        Write-Step "ffmpeg installed but not on PATH after refresh. Open a new PowerShell session and re-run this installer to continue." 'WARN'
    } else {
        Write-Step "ffmpeg installed at $($ffmpegCmd.Source)" 'OK'
    }
}

function Install-Python311 {
    if (Test-RealPythonInstalled -MinimumVersion '3.11') {
        Write-Step "Python 3.11+ already installed (real Python, not Store stub)" 'SKIP'
        return
    }

    # Python Install Manager (PIM) via py launcher 3.13+ installs runtimes to
    # user scope without admin elevation. winget Python.Python.3.11 requires
    # admin for the runtime install on most setups, which is unreachable on
    # IPPF-managed devices where the user has no admin rights.
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if (-not $pyLauncher) {
        Write-Step "Python launcher 'py' not found. Install it from https://python.org (per-user installer, no admin needed) before re-running this installer." 'FAIL'
        throw "py launcher missing - required for Python Install Manager."
    }

    Write-Step "Installing Python 3.11 via Python Install Manager (py install 3.11) - no admin required..." 'INFO'
    $pimOutput = & py install 3.11 --yes 2>&1
    $pimExit = $LASTEXITCODE
    foreach ($line in $pimOutput) {
        if ($line) { Write-Step "  py install: $line" 'INFO' }
    }
    if ($pimExit -ne 0) {
        Write-Step "py install 3.11 failed (exit $pimExit)" 'FAIL'
        throw "Python 3.11 install via PIM failed."
    }

    # Refresh PATH (PIM adds shortcut directories to user PATH on first install)
    $env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
    if (-not (Test-RealPythonInstalled -MinimumVersion '3.11')) {
        Write-Step "Python 3.11 installed via PIM but not detected after PATH refresh. Open a new PowerShell session and re-run this installer to continue." 'WARN'
        throw "Python 3.11 install verification failed."
    }
    $pyVersionOutput = & py -3.11 --version 2>&1
    Write-Step "Python 3.11 installed: $pyVersionOutput" 'OK'
}

function New-SkillVenv {
    if (Test-VenvExists -VenvPath $script:VenvPath) {
        Write-Step "Skill venv already exists at $script:VenvPath" 'SKIP'
        return
    }
    Write-Step "Creating skill venv at $script:VenvPath..." 'INFO'
    & py -3.11 -m venv $script:VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Step "venv creation failed (exit $LASTEXITCODE)" 'FAIL'
        throw "venv creation failed."
    }
    if (-not (Test-VenvExists -VenvPath $script:VenvPath)) {
        Write-Step "venv created but pyvenv.cfg missing. Investigate." 'FAIL'
        throw "venv post-creation check failed."
    }
    Write-Step "Venv created. Python: $(& "$script:VenvPath/Scripts/python.exe" --version)" 'OK'
}

function Install-PipDependencies {
    param([switch]$SkipDiarization)

    $venvPython = Join-Path $script:VenvPath 'Scripts' 'python.exe'
    if (-not (Test-Path $venvPython)) {
        Write-Step "venv Python not found at $venvPython" 'FAIL'
        throw "venv missing."
    }

    Write-Step "Upgrading pip in venv..." 'INFO'
    & $venvPython -m pip install --upgrade pip --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Step "pip upgrade failed (exit $LASTEXITCODE)" 'FAIL'
        throw "pip upgrade failed."
    }

    $reqFile = Join-Path $PSScriptRoot 'requirements.txt'
    if ($SkipDiarization) {
        Write-Step "Installing faster-whisper only (diarization skipped)..." 'INFO'
        & $venvPython -m pip install "faster-whisper>=1.0.0,<2.0.0" "soundfile>=0.12.0,<1.0.0"
    } else {
        Write-Step "Installing faster-whisper + pyannote.audio from requirements.txt..." 'INFO'
        & $venvPython -m pip install -r $reqFile
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Step "pip install failed (exit $LASTEXITCODE)" 'FAIL'
        throw "pip install failed."
    }

    # Verify imports
    Write-Step "Verifying imports..." 'INFO'
    $verifyScript = if ($SkipDiarization) {
        'import faster_whisper; print("faster_whisper:", faster_whisper.__version__)'
    } else {
        'import faster_whisper, pyannote.audio; print("faster_whisper:", faster_whisper.__version__); print("pyannote.audio:", pyannote.audio.__version__)'
    }
    & $venvPython -c $verifyScript
    if ($LASTEXITCODE -ne 0) {
        Write-Step "Import verification failed" 'FAIL'
        throw "Imports failed after pip install."
    }
    Write-Step "Pip dependencies installed and verified" 'OK'
}

function Set-HuggingFaceToken {
    [CmdletBinding()]
    param([switch]$Skip)

    # Use hyphens only; cmdkey rejects ':' in target names. /generic: is the
    # correct form for app-token credentials (vs. /add: which is for NTLM).
    $credentialName = 'IPPF-MEL-Video-HuggingFace'

    if ($Skip) {
        Write-Step "Diarization skipped; HuggingFace token not requested" 'SKIP'
        return
    }

    # Check if a token already exists
    $existing = & cmdkey /list:$credentialName 2>&1
    if ($LASTEXITCODE -eq 0 -and $existing -match [regex]::Escape($credentialName)) {
        Write-Step "HuggingFace token already stored under $credentialName" 'SKIP'
        return
    }

    Write-Host ""
    Write-Host "HuggingFace token required for pyannote speaker-diarization-3.1 model."
    Write-Host "Get a token at https://huggingface.co/settings/tokens (free account, 'read' scope sufficient)."
    Write-Host "You also need to accept the gated-model terms at https://huggingface.co/pyannote/speaker-diarization-3.1"
    Write-Host ""
    $token = Read-Host -Prompt "Paste HuggingFace token (or 'n' to skip)" -AsSecureString
    $tokenPlain = [System.Net.NetworkCredential]::new('', $token).Password

    if ($tokenPlain -eq 'n' -or [string]::IsNullOrWhiteSpace($tokenPlain)) {
        Write-Step "HuggingFace token entry skipped. Diarization will not work until installer re-run with token." 'WARN'
        return
    }

    & cmdkey /generic:$credentialName /user:hf /pass:$tokenPlain | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Step "Credential Manager storage failed (exit $LASTEXITCODE)" 'FAIL'
        throw "Token storage failed."
    }
    Write-Step "HuggingFace token stored in Windows Credential Manager under $credentialName" 'OK'
}

function Get-WhisperModel {
    param([switch]$Defer)

    if ($Defer) {
        Write-Step "Whisper large-v3 model download deferred. First analyze-video run will download (~3GB)." 'SKIP'
        return
    }

    Write-Host ""
    Write-Host "Whisper large-v3 model is ~3GB. Best Romanian/Bulgarian/Polish/Arabic accuracy but a one-time download."
    $reply = Read-Host "Download now (recommended) or defer to first use? [now/defer]"
    if ($reply -eq 'defer') {
        Write-Step "Whisper large-v3 download deferred." 'SKIP'
        return
    }

    Write-Step "Downloading Whisper large-v3 model (this takes 5-10 minutes)..." 'INFO'
    $venvPython = Join-Path $script:VenvPath 'Scripts' 'python.exe'
    $script = @'
from faster_whisper import WhisperModel
print("Downloading large-v3...")
model = WhisperModel("large-v3", device="cpu", compute_type="int8")
print("Model loaded successfully.")
'@
    & $venvPython -c $script
    if ($LASTEXITCODE -ne 0) {
        Write-Step "Whisper model download failed" 'FAIL'
        throw "Model download failed."
    }
    Write-Step "Whisper large-v3 model ready" 'OK'
}

function Invoke-SmokeTest {
    Write-Step "Running post-install smoke test..." 'INFO'
    $venvPython = Join-Path $script:VenvPath 'Scripts' 'python.exe'
    $smokeScript = Join-Path $PSScriptRoot 'smoke-test.py'
    $fixturePath = Join-Path $PSScriptRoot 'test-fixtures' 'silence-5sec.wav'

    if (-not (Test-Path $fixturePath)) {
        Write-Step "Test fixture missing. Generating..." 'INFO'
        & (Join-Path $PSScriptRoot 'Generate-TestFixture.ps1')
    }

    & $venvPython $smokeScript --audio $fixturePath --model tiny
    if ($LASTEXITCODE -ne 0) {
        Write-Step "Smoke test failed (exit $LASTEXITCODE)" 'FAIL'
        throw "Smoke test failed."
    }
    Write-Step "Smoke test passed. Skill toolchain ready." 'OK'
}

function Write-Summary {
    Write-Host ""
    Write-Host "==================================================================="
    Write-Host "  video-content-analysis Stage 1 install complete."
    Write-Host "==================================================================="
    Write-Host "  Components:"
    if (Test-FFmpegInstalled) { Write-Host "    [OK]   ffmpeg ($((Get-Command ffmpeg).Source))" }
    if (Test-RealPythonInstalled -MinimumVersion '3.11') { Write-Host "    [OK]   Python 3.11 ($(py -3.11 --version))" }
    if (Test-VenvExists -VenvPath $script:VenvPath) { Write-Host "    [OK]   venv ($script:VenvPath)" }
    Write-Host "  Log: $script:LogFile"
    Write-Host "  Re-run safely; the installer is idempotent."
    Write-Host ""
}

function Main {
    Write-Step "Starting video-content-analysis installer (PowerShell $($PSVersionTable.PSVersion))" 'INFO'
    Write-Step "Log file: $script:LogFile" 'INFO'

    # Pre-flight
    if (-not (Test-WingetAvailable)) {
        Write-Step "winget not found. Install via Microsoft Store: https://aka.ms/getwinget" 'FAIL'
        exit 1
    }
    Write-Step "winget detected" 'OK'

    Confirm-DiskSpace -RequiredGB 6

    # Stage 1.4: ffmpeg
    Install-FFmpeg

    # Stage 1.5: Python 3.11
    Install-Python311

    # Stage 1.6: venv
    New-SkillVenv

    # Stage 1.7: pip dependencies
    Install-PipDependencies -SkipDiarization:$SkipDiarization

    # Stage 1.8: HuggingFace token
    Set-HuggingFaceToken -Skip:$SkipDiarization

    # Stage 1.9: test fixture (auto-generated if missing)
    # Handled inline by Invoke-SmokeTest

    # Stage 1.10-1.11: model preload + smoke test
    Get-WhisperModel -Defer:$DeferModelDownload
    Invoke-SmokeTest

    # Stage 1.12: summary
    Write-Summary
}

Main
