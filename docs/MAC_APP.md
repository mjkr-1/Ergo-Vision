# macOS App Launcher

ErgoVision remains a local FastAPI + React application, but the repository can install a lightweight macOS `.app` launcher so everyday use does not require opening Terminal.

## Install

```bash
bash scripts/install_mac_app.sh
```

The launcher is created at:

```text
~/Applications/ErgoVision.app
```

Open it from Finder or Spotlight. It starts the local backend, opens the dashboard in your default browser, and keeps the launcher process alive while ErgoVision is running.

Runtime logs are written to:

```text
~/.ergovision/ergovision.log
```

## Stop

Quitting the app should terminate its launcher and release the backend. You can always force a clean local shutdown with:

```bash
bash scripts/stop_mac.sh
```

## Uninstall

```bash
bash scripts/uninstall_mac_app.sh
```

This removes the `.app` launcher but leaves the source repository and local calibration data untouched.

## Camera permission

macOS may request camera permission when the launcher starts the Python vision process. ErgoVision processes frames locally and does not upload or save webcam footage.
