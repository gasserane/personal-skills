function Test-WingetAvailable {
    [CmdletBinding()]
    param()
    return [bool](Get-Command winget -ErrorAction SilentlyContinue)
}

function Test-FFmpegInstalled {
    [CmdletBinding()]
    param()
    return [bool](Get-Command ffmpeg -ErrorAction SilentlyContinue)
}

function Get-PythonVersion {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$PythonPath)
    try {
        $output = & $PythonPath --version 2>&1
        if ($output -match 'Python (\d+\.\d+(?:\.\d+)?)') {
            return [version]$Matches[1]
        }
    } catch {}
    return $null
}

function Invoke-PyLauncher {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$LauncherPath,
        [Parameter(Mandatory)][string]$Version
    )
    try {
        return (& $LauncherPath "-$Version" --version 2>&1)
    } catch {
        return $null
    }
}

function Test-RealPythonInstalled {
    [CmdletBinding()]
    param([string]$MinimumVersion = '3.11')

    $minVer = [version]$MinimumVersion

    # Fast-path: real (non-Store) python on PATH at sufficient version
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCmd -and $pyCmd.Source -notlike '*\WindowsApps\*') {
        $detectedVer = Get-PythonVersion -PythonPath $pyCmd.Source
        if ($detectedVer -and $detectedVer -ge $minVer) { return $true }
    }

    # Fallback: py launcher reports requested version at or above minimum
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        $launcherOutput = Invoke-PyLauncher -LauncherPath $pyLauncher.Source -Version $MinimumVersion
        if ($launcherOutput -match 'Python (\d+\.\d+(?:\.\d+)?)') {
            $launcherVer = [version]$Matches[1]
            if ($launcherVer -ge $minVer) { return $true }
        }
    }
    return $false
}

function Test-VenvExists {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$VenvPath)
    return (Test-Path (Join-Path $VenvPath 'pyvenv.cfg'))
}

Export-ModuleMember -Function Test-WingetAvailable, Test-FFmpegInstalled, Test-RealPythonInstalled, Test-VenvExists, Get-PythonVersion, Invoke-PyLauncher
