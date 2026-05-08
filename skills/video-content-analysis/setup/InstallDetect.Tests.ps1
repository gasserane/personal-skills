BeforeAll {
    $ModulePath = Join-Path $PSScriptRoot 'InstallDetect.psm1'
    Import-Module $ModulePath -Force
}

Describe 'Test-WingetAvailable' {
    It 'Returns true when winget is on PATH' {
        Mock -ModuleName InstallDetect Get-Command { @{Source='C:\winget.exe'} } -ParameterFilter { $Name -eq 'winget' }
        Test-WingetAvailable | Should -Be $true
    }
    It 'Returns false when winget is missing' {
        Mock -ModuleName InstallDetect Get-Command { $null } -ParameterFilter { $Name -eq 'winget' }
        Test-WingetAvailable | Should -Be $false
    }
}

Describe 'Test-FFmpegInstalled' {
    It 'Returns true when ffmpeg is on PATH' {
        Mock -ModuleName InstallDetect Get-Command { @{Source='C:\ffmpeg\bin\ffmpeg.exe'} } -ParameterFilter { $Name -eq 'ffmpeg' }
        Test-FFmpegInstalled | Should -Be $true
    }
    It 'Returns false when ffmpeg is missing' {
        Mock -ModuleName InstallDetect Get-Command { $null } -ParameterFilter { $Name -eq 'ffmpeg' }
        Test-FFmpegInstalled | Should -Be $false
    }
}

Describe 'Test-RealPythonInstalled' {
    It 'Returns false when only the Windows Store stub is installed' {
        Mock -ModuleName InstallDetect Get-Command { @{Source='C:\Users\AGasser\AppData\Local\Microsoft\WindowsApps\python.exe'} } -ParameterFilter { $Name -eq 'python' }
        Mock -ModuleName InstallDetect Get-Command { $null } -ParameterFilter { $Name -eq 'py' }
        Test-RealPythonInstalled | Should -Be $false
    }
    It 'Returns true when py launcher reports Python 3.11+' {
        Mock -ModuleName InstallDetect Get-Command { $null } -ParameterFilter { $Name -eq 'python' }
        Mock -ModuleName InstallDetect Get-Command { @{Source='C:\Windows\py.exe'} } -ParameterFilter { $Name -eq 'py' }
        Mock -ModuleName InstallDetect Invoke-PyLauncher { 'Python 3.11.7' }
        Test-RealPythonInstalled | Should -Be $true
    }
}

Describe 'Test-RealPythonInstalled - version comparison' {
    It 'Returns false when non-Store Python is below MinimumVersion' {
        Mock -ModuleName InstallDetect Get-Command { @{Source='C:\Python310\python.exe'} } -ParameterFilter { $Name -eq 'python' }
        Mock -ModuleName InstallDetect Get-PythonVersion { [version]'3.10.5' } -ParameterFilter { $PythonPath -eq 'C:\Python310\python.exe' }
        Mock -ModuleName InstallDetect Get-Command { $null } -ParameterFilter { $Name -eq 'py' }
        Test-RealPythonInstalled -MinimumVersion '3.11' | Should -Be $false
    }
    It 'Returns true when non-Store Python is at or above MinimumVersion' {
        Mock -ModuleName InstallDetect Get-Command { @{Source='C:\Python311\python.exe'} } -ParameterFilter { $Name -eq 'python' }
        Mock -ModuleName InstallDetect Get-Command { $null } -ParameterFilter { $Name -eq 'py' }
        Mock -ModuleName InstallDetect Get-PythonVersion { [version]'3.11.7' } -ParameterFilter { $PythonPath -eq 'C:\Python311\python.exe' }
        Test-RealPythonInstalled -MinimumVersion '3.11' | Should -Be $true
    }
    It 'Falls back to py launcher and returns false when launcher reports lower version' {
        Mock -ModuleName InstallDetect Get-Command { $null } -ParameterFilter { $Name -eq 'python' }
        Mock -ModuleName InstallDetect Get-Command { @{Source='C:\Windows\py.exe'} } -ParameterFilter { $Name -eq 'py' }
        Mock -ModuleName InstallDetect Invoke-PyLauncher { 'Python 3.10.5' }
        Test-RealPythonInstalled -MinimumVersion '3.11' | Should -Be $false
    }
}

Describe 'Test-VenvExists' {
    BeforeEach { $script:tempVenv = Join-Path $env:TEMP "test-venv-$(Get-Random)" }
    AfterEach { if (Test-Path $script:tempVenv) { Remove-Item $script:tempVenv -Recurse -Force } }

    It 'Returns false when venv directory missing' {
        Test-VenvExists -VenvPath $script:tempVenv | Should -Be $false
    }
    It 'Returns true when venv has pyvenv.cfg' {
        New-Item -Path $script:tempVenv -ItemType Directory | Out-Null
        New-Item -Path (Join-Path $script:tempVenv 'pyvenv.cfg') -ItemType File | Out-Null
        Test-VenvExists -VenvPath $script:tempVenv | Should -Be $true
    }
}
