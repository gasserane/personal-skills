#Requires -Version 7.0
<#
.SYNOPSIS
    Generates the silence-5sec.wav test fixture using ffmpeg.

.DESCRIPTION
    Re-runnable. Overwrites the fixture each time. Used by the smoke test.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$fixturePath = Join-Path $PSScriptRoot 'test-fixtures' 'silence-5sec.wav'

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Error "ffmpeg not on PATH. Run setup-video-pipeline.ps1 first."
    exit 1
}

& ffmpeg -y -f lavfi -i 'anullsrc=channel_layout=mono:sample_rate=16000' -t 5 $fixturePath 2>$null
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $fixturePath)) {
    Write-Error "Test fixture generation failed."
    exit 1
}

$size = (Get-Item $fixturePath).Length
Write-Output "Generated $fixturePath ($size bytes)"
