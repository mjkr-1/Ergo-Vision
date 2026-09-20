$ErrorActionPreference = "Stop"

$StateDir = Join-Path $env:USERPROFILE ".ergovision"
$PidFile = Join-Path $StateDir "windows.pid"

if (-not (Test-Path $PidFile)) {
    Write-Host "No managed ErgoVision Windows process was found."
    exit 0
}

$PidText = (Get-Content $PidFile -Raw).Trim()
$PidValue = 0
if (-not [int]::TryParse($PidText, [ref]$PidValue)) {
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    Write-Host "Removed a stale ErgoVision PID file."
    exit 0
}

$Process = Get-Process -Id $PidValue -ErrorAction SilentlyContinue
if ($Process) {
    Stop-Process -Id $PidValue -Force
    try { Wait-Process -Id $PidValue -Timeout 5 -ErrorAction SilentlyContinue } catch {}
    Write-Host "ErgoVision stopped and camera resources released."
}
else {
    Write-Host "ErgoVision was not running; removed stale PID information."
}

Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
