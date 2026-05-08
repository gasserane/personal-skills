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

function Test-RealPythonInstalled {
    [CmdletBinding()]
    param([string]$MinimumVersion = '3.11')

    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCmd) {
        if ($pyCmd.Source -like '*\WindowsApps\*') {
            # Windows Store stub. Treat as not installed.
        } else {
            return $true
        }
    }
    $output = Invoke-Expression "py -$MinimumVersion --version 2>&1"
    return ($output -match "^Python $([regex]::Escape($MinimumVersion))")
}

function Test-VenvExists {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$VenvPath)
    return (Test-Path (Join-Path $VenvPath 'pyvenv.cfg'))
}

Export-ModuleMember -Function Test-WingetAvailable, Test-FFmpegInstalled, Test-RealPythonInstalled, Test-VenvExists
