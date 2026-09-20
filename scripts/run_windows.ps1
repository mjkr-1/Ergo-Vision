param(
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Backend = Join-Path $Root "backend"
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$StateDir = Join-Path $env:USERPROFILE ".ergovision"
$PidFile = Join-Path $StateDir "windows.pid"
$OutLog = Join-Path $StateDir "ergovision-windows.out.log"
$ErrLog = Join-Path $StateDir "ergovision-windows.err.log"

if (-not (Test-Path $Python)) {
    throw "ErgoVision is not set up yet. Run scripts\setup_windows.ps1 first."
}

New-Item -ItemType Directory -Force -Path $StateDir | Out-Null

$EnvFile = Join-Path $Root ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        $Line = $_.Trim()
        if ($Line -and -not $Line.StartsWith("#") -and $Line.Contains("=")) {
            $Pair = $Line.Split("=", 2)
            [Environment]::SetEnvironmentVariable($Pair[0].Trim(), $Pair[1].Trim(), "Process")
        }
    }
}

$Port = if ($env:PORT) { [int]$env:PORT } else { 8000 }
$Url = "http://127.0.0.1:$Port"
$Health = "$Url/health"

function Test-ErgoVision {
    try {
        $Response = Invoke-WebRequest -Uri $Health -UseBasicParsing -TimeoutSec 2
        return $Response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

if (Test-ErgoVision) {
    if (-not $NoBrowser) { Start-Process $Url }
    Write-Host "ErgoVision is already running at $Url"
    exit 0
}

$Existing = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
if ($Existing) {
    throw "Port $Port is already in use by another process. Set PORT in .env or stop the other service."
}

Write-Host "Starting ErgoVision..."
$Process = Start-Process `
    -FilePath $Python `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$Port") `
    -WorkingDirectory $Backend `
    -PassThru `
    -WindowStyle Hidden `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog

Set-Content -Path $PidFile -Value $Process.Id -Encoding ascii

$Ready = $false
for ($i = 0; $i -lt 120; $i++) {
    if ($Process.HasExited) { break }
    if (Test-ErgoVision) {
        $Ready = $true
        break
    }
    Start-Sleep -Milliseconds 500
}

if (-not $Ready) {
    if (-not $Process.HasExited) {
        Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
    }
    Remove-Item $PidFile -ErrorAction SilentlyContinue
    Write-Host "ErgoVision failed to start. Check:" -ForegroundColor Red
    Write-Host "  $ErrLog"
    throw "Backend startup failed."
}

Write-Host "ErgoVision is ready at $Url" -ForegroundColor Green
if (-not $NoBrowser) { Start-Process $Url }
