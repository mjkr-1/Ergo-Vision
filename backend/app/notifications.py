from __future__ import annotations

import platform
import subprocess


def send_desktop_notification(title: str, body: str) -> None:
    """Send a native macOS notification without blocking posture processing."""
    if platform.system() != "Darwin":
        return

    safe_title = title.replace("\\", "\\\\").replace('"', '\\"')
    safe_body = body.replace("\\", "\\\\").replace('"', '\\"')
    script = (
        f'display notification "{safe_body}" '
        f'with title "{safe_title}" sound name "Glass"'
    )

    try:
        subprocess.Popen(
            ["osascript", "-e", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        # Notifications are optional and must never stop posture monitoring.
        pass
