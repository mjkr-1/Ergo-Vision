# Windows

## Supported environment

Recommended:

- Windows 10 or Windows 11, 64-bit
- Python 3.11 or 3.12
- integrated or USB webcam
- internet access during the first Python dependency installation

Node.js 18+ is only needed for a Git source checkout that does not already contain `frontend/dist`.

## Install a release

From the extracted `ErgoVision-Windows.zip`:

```powershell
powershell -ExecutionPolicy Bypass -File .\install-windows.ps1
```

The installer copies ErgoVision to:

```text
%LOCALAPPDATA%\ErgoVision
```

and creates Desktop and Start Menu shortcuts.

## Manual commands

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\doctor_windows.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\run_windows.ps1
```

Stop:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_windows.ps1
```

## Camera permission

Open **Settings → Privacy & security → Camera** and enable **Let desktop apps access your camera**.

ErgoVision releases the webcam after the final dashboard tab/window disconnects.

## Logs

Runtime state and logs are under:

```text
%USERPROFILE%\.ergovision\
```

including:

```text
ergovision-windows.out.log
ergovision-windows.err.log
windows.pid
```
