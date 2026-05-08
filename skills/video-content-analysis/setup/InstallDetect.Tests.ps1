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
        Mock -ModuleName InstallDetect Invoke-Expression { '' } -ParameterFilter { $Command -like '*py -3.11 --version*' }
        Test-RealPythonInstalled | Should -Be $false
    }
    It 'Returns true when py launcher reports Python 3.11+' {
        Mock -ModuleName InstallDetect Get-Command { $null } -ParameterFilter { $Name -eq 'python' }
        Mock -ModuleName InstallDetect Invoke-Expression { 'Python 3.11.7' } -ParameterFilter { $Command -like '*py -3.11 --version*' }
        Test-RealPythonInstalled | Should -Be $true
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
