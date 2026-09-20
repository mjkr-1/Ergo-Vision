$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Runner = Join-Path $Root "scripts\run_windows.ps1"
$PowerShell = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"

if (-not (Test-Path $Runner)) {
    throw "Could not find ErgoVision runner: $Runner"
}

$Shell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath("Desktop")
$StartMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"

foreach ($ShortcutPath in @(
    (Join-Path $Desktop "ErgoVision.lnk"),
    (Join-Path $StartMenu "ErgoVision.lnk")
)) {
    $Shortcut = $Shell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $PowerShell
    $Shortcut.Arguments = "-NoLogo -NoProfile -ExecutionPolicy Bypass -File `"$Runner`""
    $Shortcut.WorkingDirectory = $Root
    $Shortcut.Description = "ErgoVision local posture monitor"
    $Shortcut.Save()
    Write-Host "Created: $ShortcutPath"
}

Write-Host "Windows shortcuts installed." -ForegroundColor Green
