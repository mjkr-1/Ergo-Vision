$ErrorActionPreference = "Stop"

$Source = (Resolve-Path $PSScriptRoot).Path
$Destination = Join-Path $env:LOCALAPPDATA "ErgoVision"

Write-Host "Installing ErgoVision for Windows" -ForegroundColor Cyan
Write-Host "Install location: $Destination"
Write-Host ""

if ($Source -ne $Destination) {
    if (Test-Path $Destination) {
        Remove-Item $Destination -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null

    Get-ChildItem -Force $Source | Where-Object {
        $_.Name -notin @(".git", ".venv", "node_modules")
    } | ForEach-Object {
        Copy-Item $_.FullName -Destination $Destination -Recurse -Force
    }
}

& (Join-Path $Destination "scripts\setup_windows.ps1")
& (Join-Path $Destination "scripts\install_windows_shortcut.ps1")

Write-Host ""
Write-Host "ErgoVision has been installed." -ForegroundColor Green
Write-Host "Starting it now..."
& (Join-Path $Destination "scripts\run_windows.ps1")
