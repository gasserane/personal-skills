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

.PARAMETER NonInteractive
    Suppress all Read-Host prompts. HuggingFace token entry is skipped
    (equivalent to passing 's'); model download is deferred; disk-space
    warning is auto-continued. Enables unattended CI runs.

.EXAMPLE
    ./setup-video-pipeline.ps1
    Full install with prompts.

.EXAMPLE
    ./setup-video-pipeline.ps1 -SkipDiarization -DeferModelDownload
    Minimal install, skip diarization and defer model.

.EXAMPLE
    ./setup-video-pipeline.ps1 -DeferModelDownload -NonInteractive
    Unattended install; no prompts. Suitable for CI.
#>
[CmdletBinding()]
param(
    [switch]$SkipDiarization,
    [switch]$DeferModelDownload,
    [switch]$NonInteractive
)

$ErrorActionPreference = 'Stop'
$script:Constants = Import-PowerShellDataFile (Join-Path $PSScriptRoot 'constants.psd1')
$script:LogFile = Join-Path $PSScriptRoot 'install.log'
$script:VenvPath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\venv'))

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
        Write-Step "Insufficient disk space: ${freeGB}GB free, ${RequiredGB}GB required" 'WARN'
        if ($NonInteractive) {
            Write-Step "NonInteractive mode: continuing despite low disk space." 'WARN'
        } else {
            $reply = Read-Host "Continue anyway? [y/N]"
            if ($reply -notmatch '^[Yy]') { exit 1 }
        }
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
    $output = & winget install Gyan.FFmpeg --scope user --accept-source-agreements --accept-package-agreements --silent 2>&1
    $wingetExit = $LASTEXITCODE
    Write-Verbose ($output -join "`n")
    # winget exit codes treated as success:
    #   0           = installed
    #   -1978335189 = already installed (APPINSTALLER_CLI_ERROR_PACKAGE_ALREADY_INSTALLED, 0x8A15002B)
    if ($wingetExit -ne 0 -and $wingetExit -ne -1978335189) {
        Write-Step "ffmpeg install via winget failed (exit $wingetExit)" 'FAIL'
        throw "ffmpeg install failed."
    }
    # Refresh PATH for the current session
    $env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
    # PATH may be stale even after refreshenv. Force a fresh process so subsequent
    # Get-Command finds the new binary. If still missing, abort with instruction.
    if (-not (Test-FFmpegInstalled)) {
        Write-Step "ffmpeg installed but not on PATH after refresh. Open a new PowerShell session and re-run." 'FAIL'
        exit 1
    }
    $ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
    Write-Step "ffmpeg installed at $($ffmpegCmd.Source)" 'OK'
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
    # PATH may be stale even after refreshenv. Force a fresh process so subsequent
    # Get-Command finds the new binary. If still missing, abort with instruction.
    if (-not (Test-RealPythonInstalled -MinimumVersion '3.11')) {
        Write-Step "Python 3.11 installed but not detected after PATH refresh. Open a new PowerShell session and re-run." 'FAIL'
        exit 1
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
    $output = & py -3.11 -m venv $script:VenvPath 2>&1
    $exit = $LASTEXITCODE
    Write-Verbose ($output -join "`n")
    if ($exit -ne 0) {
        Write-Step "venv creation failed (exit $exit)" 'FAIL'
        throw "venv creation failed."
    }
    if (-not (Test-VenvExists -VenvPath $script:VenvPath)) {
        Write-Step "venv created but pyvenv.cfg missing. Investigate." 'FAIL'
        throw "venv post-creation check failed."
    }
    Write-Step "Venv created. Python: $(& "$script:VenvPath/Scripts/python.exe" --version)" 'OK'
}

function Test-PipDependenciesInstalled {
    param(
        [Parameter(Mandatory)] [string] $VenvPath,
        [Parameter(Mandatory)] [string] $RequirementsFile
    )
    $venvPython = Join-Path $VenvPath 'Scripts/python.exe'
    if (-not (Test-Path $venvPython)) { return $false }
    $required = Get-Content $RequirementsFile | Where-Object { $_ -and -not $_.StartsWith('#') }
    foreach ($line in $required) {
        $name = ($line -split '[<>=!]')[0].Trim()
        if (-not $name) { continue }
        $output = & $venvPython -m pip show $name 2>&1
        if ($LASTEXITCODE -ne 0) { return $false }
    }
    return $true
}

function Install-PipDependencies {
    param([switch]$SkipDiarization)

    $venvPython = Join-Path $script:VenvPath 'Scripts' 'python.exe'
    if (-not (Test-Path $venvPython)) {
        Write-Step "venv Python not found at $venvPython" 'FAIL'
        throw "venv missing."
    }

    $reqFile = Join-Path $PSScriptRoot 'requirements.txt'

    if ($SkipDiarization) {
        # Minimal install: faster-whisper + soundfile only.
        # Idempotency check mirrors what we actually install — not the full requirements.txt.
        $needed = @('faster-whisper', 'soundfile')
        $allPresent = $true
        foreach ($pkg in $needed) {
            $null = & $venvPython -m pip show $pkg 2>&1
            if ($LASTEXITCODE -ne 0) { $allPresent = $false; break }
        }
        if ($allPresent) {
            Write-Step "[SKIP] pip dependencies already satisfied (minimal install)" 'SKIP'
            return
        }

        Write-Step "Installing pip dependencies (faster-whisper + soundfile, diarization skipped)..." 'INFO'
        $output = & $venvPython -m pip install --upgrade pip --quiet 2>&1
        $exit = $LASTEXITCODE
        Write-Verbose ($output -join "`n")
        if ($exit -ne 0) {
            Write-Step "pip upgrade failed (exit $exit)" 'FAIL'
            throw "pip upgrade failed."
        }

        Write-Step "Installing faster-whisper only (diarization skipped)..." 'INFO'
        $output = & $venvPython -m pip install "faster-whisper>=1.0.0,<2.0.0" "soundfile>=0.12.0,<1.0.0" 2>&1
        $exit = $LASTEXITCODE
        Write-Verbose ($output -join "`n")
        if ($exit -ne 0) {
            Write-Step "pip install failed (exit $exit)" 'FAIL'
            throw "pip install failed."
        }

        # Verify imports
        Write-Step "Verifying imports..." 'INFO'
        $output = & $venvPython -c 'import faster_whisper; print("faster_whisper:", faster_whisper.__version__)' 2>&1
        $exit = $LASTEXITCODE
        Write-Verbose ($output -join "`n")
        if ($exit -ne 0) {
            Write-Step "Import verification failed" 'FAIL'
            throw "Imports failed after pip install."
        }
    } else {
        if (Test-PipDependenciesInstalled -VenvPath $script:VenvPath -RequirementsFile $reqFile) {
            Write-Step "[SKIP] pip dependencies already satisfied" 'SKIP'
            return
        }

        Write-Step "Installing pip dependencies (upgrading pip + full requirements.txt)..." 'INFO'
        $output = & $venvPython -m pip install --upgrade pip --quiet 2>&1
        $exit = $LASTEXITCODE
        Write-Verbose ($output -join "`n")
        if ($exit -ne 0) {
            Write-Step "pip upgrade failed (exit $exit)" 'FAIL'
            throw "pip upgrade failed."
        }

        Write-Step "Installing faster-whisper + pyannote.audio from requirements.txt..." 'INFO'
        $output = & $venvPython -m pip install -r $reqFile 2>&1
        $exit = $LASTEXITCODE
        Write-Verbose ($output -join "`n")
        if ($exit -ne 0) {
            Write-Step "pip install failed (exit $exit)" 'FAIL'
            throw "pip install failed."
        }

        # Verify imports
        Write-Step "Verifying imports..." 'INFO'
        $output = & $venvPython -c 'import faster_whisper, pyannote.audio; print("faster_whisper:", faster_whisper.__version__); print("pyannote.audio:", pyannote.audio.__version__)' 2>&1
        $exit = $LASTEXITCODE
        Write-Verbose ($output -join "`n")
        if ($exit -ne 0) {
            Write-Step "Import verification failed" 'FAIL'
            throw "Imports failed after pip install."
        }
    }

    Write-Step "Pip dependencies installed and verified" 'OK'
}

function Set-HuggingFaceToken {
    [CmdletBinding()]
    param([switch]$Skip)

    # Use hyphens only; cmdkey rejects ':' in target names. /generic: is the
    # correct form for app-token credentials (vs. /add: which is for NTLM).
    $credentialName = $script:Constants.HuggingFaceCredentialTarget

    if ($Skip) {
        Write-Step "Diarization skipped; HuggingFace token not requested" 'SKIP'
        return
    }

    # Check if a token already exists. cmdkey /list:<name> always returns exit 0
    # AND always echoes the credential name in the "Currently stored credentials for X:"
    # header — even when the body says "* NONE *". Match the "Target:" line instead;
    # that line only appears when an actual credential exists.
    $existing = & cmdkey /list:$credentialName 2>&1
    $existingText = ($existing -join "`n")
    if ($existingText -match "Target:\s*$([regex]::Escape($credentialName))") {
        Write-Step "HuggingFace token already stored under $credentialName" 'SKIP'
        return
    }

    if ($NonInteractive) {
        Write-Step "NonInteractive mode: HuggingFace token entry skipped. Diarization will not work until installer re-run with token." 'WARN'
        return
    }

    Write-Host ""
    Write-Host "HuggingFace token required for pyannote speaker-diarization-3.1 model."
    Write-Host "Get a token at https://huggingface.co/settings/tokens (free account, 'read' scope sufficient)."
    Write-Host "You also need to accept the gated-model terms at https://huggingface.co/pyannote/speaker-diarization-3.1"
    Write-Host ""
    $token = Read-Host -Prompt "Paste HuggingFace token (or 's'/'skip'/'n'/'no' to skip)" -AsSecureString
    $tokenPlain = [System.Net.NetworkCredential]::new('', $token).Password

    $skipResponses = @('s', 'skip', 'n', 'no', '')
    if ($tokenPlain.Trim().ToLower() -in $skipResponses) {
        Write-Step "HuggingFace token entry skipped. Diarization will not work until installer re-run with token." 'WARN'
        return
    }

    $output = & cmdkey /generic:$credentialName /user:hf /pass:$tokenPlain 2>&1
    $exit = $LASTEXITCODE
    Write-Verbose ($output -join "`n")
    if ($exit -ne 0) {
        Write-Step "Credential Manager storage failed (exit $exit)" 'FAIL'
        throw "Token storage failed."
    }
    Write-Step "HuggingFace token stored in Windows Credential Manager under $credentialName" 'OK'

    # Stage 6: confirm gated-terms acceptance up-front so the first diarization
    # run does not download 500 MB and then fail with HTTP 403.
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($token)
    try {
        $plain = [Runtime.InteropServices.Marshal]::PtrToStringUni($bstr)
        $accepted = Confirm-PyannoteGatedTerms -Token $plain
        if (-not $accepted) {
            Write-Step "Diarization will not work until gated terms are accepted." 'WARN'
        }
    } finally {
        if ($bstr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
        Remove-Variable plain -ErrorAction SilentlyContinue
    }
}

function Confirm-PyannoteGatedTerms {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$Token,
        [int]$TimeoutSeconds = 10
    )

    Write-Step "Probing pyannote gated-terms acceptance..." 'INFO'
    $modelUrl = "https://huggingface.co/api/models/pyannote/speaker-diarization-3.1"
    $headers = @{ Authorization = "Bearer $Token" }
    try {
        $resp = Invoke-WebRequest -Uri $modelUrl -Headers $headers -UseBasicParsing `
            -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            Write-Step "Gated-terms acceptance confirmed; pyannote model accessible" 'OK'
            return $true
        }
        Write-Step "Unexpected status $($resp.StatusCode) probing gated terms" 'WARN'
        return $false
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        if ($code -eq 403) {
            Write-Step "Gated-terms NOT accepted (HTTP 403). Visit https://huggingface.co/pyannote/speaker-diarization-3.1, click 'Agree and access repository', then re-run this installer." 'FAIL'
            return $false
        }
        if ($code -eq 401) {
            Write-Step "Token rejected (HTTP 401). Token may be wrong scope or expired." 'FAIL'
            return $false
        }
        Write-Step "Probe error: $($_.Exception.Message)" 'WARN'
        return $false
    }
}

function Get-WhisperModel {
    param([switch]$Defer)

    if ($Defer) {
        Write-Step "Whisper large-v3 model download deferred. First analyze-video run will download (~3GB)." 'SKIP'
        return
    }

    if ($NonInteractive) {
        Write-Step "NonInteractive mode: Whisper large-v3 model download deferred." 'SKIP'
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
    $pyScript = @'
from faster_whisper import WhisperModel
print("Downloading large-v3...")
model = WhisperModel("large-v3", device="cpu", compute_type="int8")
print("Model loaded successfully.")
'@
    $output = & $venvPython -c $pyScript 2>&1
    $exit = $LASTEXITCODE
    Write-Verbose ($output -join "`n")
    if ($exit -ne 0) {
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

    $output = & $venvPython $smokeScript --audio $fixturePath --model tiny 2>&1
    $smokeExit = $LASTEXITCODE
    Write-Verbose ($output -join "`n")
    if ($smokeExit -ne 0) {
        # Surface a targeted hint based on the exit code from smoke-test.py
        $hint = switch ($smokeExit) {
            1 { "Smoke test failed (unclassified error). Review output above or run smoke-test.py manually for the full traceback." }
            2 { "Test fixture WAV missing — re-run installer or run Generate-TestFixture.ps1 manually." }
            3 { "faster_whisper import failed — check pip install in venv; run: pip show faster-whisper" }
            4 { "Whisper model load failed — venv may be corrupt; delete venv/ and re-run installer." }
            5 { "Transcription failed — audio fixture may be corrupt; delete test-fixtures/silence-5sec.wav and re-run." }
            default { "Smoke test failed with unexpected exit code $smokeExit." }
        }
        Write-Step "Smoke test failed (exit $smokeExit): $hint" 'FAIL'
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
