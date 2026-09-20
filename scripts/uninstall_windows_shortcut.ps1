$Desktop = [Environment]::GetFolderPath("Desktop")
$StartMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"

foreach ($ShortcutPath in @(
    (Join-Path $Desktop "ErgoVision.lnk"),
    (Join-Path $StartMenu "ErgoVision.lnk")
)) {
    if (Test-Path $ShortcutPath) {
        Remove-Item $ShortcutPath -Force
        Write-Host "Removed: $ShortcutPath"
    }
}
