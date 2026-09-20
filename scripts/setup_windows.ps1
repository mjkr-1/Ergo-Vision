$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Venv = Join-Path $Root ".venv"
$Models = Join-Path $Root "backend\app\models"
$FrontendDist = Join-Path $Root "frontend\dist\index.html"

function Invoke-SystemPython {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 @Arguments
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python @Arguments
    }
    else {
        throw "Python was not found. Install Python 3.11 or 3.12 from python.org, then run this installer again."
    }

    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed."
    }
}

Write-Host "ErgoVision Windows setup" -ForegroundColor Cyan
Write-Host ""

$VersionText = if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
} else {
    throw "Python was not found. Install Python 3.11 or 3.12 from python.org."
}

$Parts = $VersionText.Trim().Split(".")
$Major = [int]$Parts[0]
$Minor = [int]$Parts[1]
if ($Major -ne 3 -or $Minor -lt 11 -or $Minor -gt 12) {
    throw "ErgoVision currently supports Python 3.11-3.12. Detected Python $VersionText."
}

if (-not (Test-Path $Venv)) {
    Write-Host "Creating Python virtual environment..."
    Invoke-SystemPython -m venv $Venv
}

$VenvPython = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment creation failed: $VenvPython was not created."
}

Write-Host "Installing Python dependencies..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }

& $VenvPython -m pip install -r (Join-Path $Root "backend\requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Python dependency installation failed." }

if (-not (Test-Path $FrontendDist)) {
    Write-Host "Frontend build not bundled; building it locally..."
    if (-not (Get-Command node -ErrorAction SilentlyContinue) -or -not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "This source checkout does not contain a production frontend build. Install Node.js 18+ and npm, then run setup again. GitHub release ZIPs include the built frontend and do not require Node.js."
    }

    Push-Location (Join-Path $Root "frontend")
    try {
        npm ci
        if ($LASTEXITCODE -ne 0) { throw "npm ci failed." }
        npm run build
        if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Host "Using bundled frontend production build."
}

New-Item -ItemType Directory -Force -Path $Models | Out-Null

Write-Host "Provisioning MediaPipe models..."
Push-Location (Join-Path $Root "backend")
try {
    & $VenvPython -m app.vision.models
    $ModelsOk = $LASTEXITCODE -eq 0
}
finally {
    Pop-Location
}

$FaceModel = Join-Path $Models "face_landmarker.task"
$PoseModel = Join-Path $Models "pose_landmarker_lite.task"

if (-not $ModelsOk -or -not (Test-Path $FaceModel) -or -not (Test-Path $PoseModel)) {
    Write-Host "Python model download did not complete; retrying with PowerShell..."
    Invoke-WebRequest `
        -Uri "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task" `
        -OutFile $FaceModel
    Invoke-WebRequest `
        -Uri "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task" `
        -OutFile $PoseModel
}

foreach ($Model in @($FaceModel, $PoseModel)) {
    if (-not (Test-Path $Model) -or (Get-Item $Model).Length -le 0) {
        throw "MediaPipe model is missing or empty: $Model"
    }
}

$StateDir = Join-Path $env:USERPROFILE ".ergovision"
New-Item -ItemType Directory -Force -Path $StateDir | Out-Null

Write-Host ""
Write-Host "ErgoVision setup is complete." -ForegroundColor Green
Write-Host "Diagnostics: powershell -ExecutionPolicy Bypass -File `"$Root\scripts\doctor_windows.ps1`""
Write-Host "Start:       powershell -ExecutionPolicy Bypass -File `"$Root\scripts\run_windows.ps1`""
