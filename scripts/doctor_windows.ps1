$ErrorActionPreference = "Continue"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$Models = Join-Path $Root "backend\app\models"
$Failed = $false

function Pass($Message) { Write-Host "OK   $Message" -ForegroundColor Green }
function Warn($Message) { Write-Host "WARN $Message" -ForegroundColor Yellow }
function Fail($Message) { Write-Host "FAIL $Message" -ForegroundColor Red; $script:Failed = $true }

Write-Host "ErgoVision Windows doctor"
Write-Host ""

if (Get-Command python -ErrorAction SilentlyContinue) {
    Pass "python: $(python --version 2>&1)"
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    Pass "Python launcher is installed."
}
else {
    Fail "Python is not installed."
}

if (Get-Command node -ErrorAction SilentlyContinue) { Pass "node: $(node --version)" }
else { Warn "Node.js is not installed. This is OK for a release bundle with a prebuilt frontend." }

if (Test-Path $VenvPython) {
    Pass "virtual environment exists"
    & $VenvPython -c "import cv2, fastapi, mediapipe, numpy, uvicorn"
    if ($LASTEXITCODE -eq 0) { Pass "Python runtime imports succeeded" }
    else { Fail "Python runtime imports failed; rerun setup_windows.ps1" }
}
else {
    Fail "virtual environment is missing"
}

if (Test-Path (Join-Path $Root "frontend\dist\index.html")) { Pass "frontend production build exists" }
else { Fail "frontend production build is missing" }

foreach ($Name in @("face_landmarker.task", "pose_landmarker_lite.task")) {
    $Path = Join-Path $Models $Name
    if (Test-Path $Path -and (Get-Item $Path).Length -gt 0) { Pass "$Name is present" }
    else { Fail "$Name is missing or empty" }
}

$Port = if ($env:PORT) { [int]$env:PORT } else { 8000 }
$Listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
if ($Listener) { Warn "port $Port is already in use" }
else { Pass "port $Port is available" }

Write-Host ""
if ($Failed) {
    Write-Host "One or more checks failed. See docs\WINDOWS.md." -ForegroundColor Red
    exit 1
}
Write-Host "Environment looks ready." -ForegroundColor Green
