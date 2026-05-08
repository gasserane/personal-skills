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

    # Stage 1.5+: subsequent install steps
    Write-Step "Stage 1.4 complete (ffmpeg). Subsequent steps not yet wired." 'INFO'
}

Main
