import subprocess

from app.pipeline import PosturePipeline


def test_windows_notification_uses_powershell_toast(monkeypatch):
    calls = []
    monkeypatch.setattr("app.pipeline.platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "app.pipeline.subprocess.run",
        lambda *args, **kwargs: calls.append((args, kwargs)) or subprocess.CompletedProcess(args[0], 0, "", ""),
    )

    pipeline = PosturePipeline.__new__(PosturePipeline)
    pipeline._last_reminder = ""
    pipeline._notify_native("ErgoVision", "Sit upright")

    assert pipeline._last_reminder == "ErgoVision: Sit upright"
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[0][0] == "powershell"
    assert "ToastNotificationManager" in args[0][-1]
    assert "ErgoVision.Desktop" in args[0][-1]
    assert "<text>ErgoVision</text>" in args[0][-1]
    assert "<text>Sit upright</text>" in args[0][-1]
    assert kwargs["creationflags"] == getattr(subprocess, "CREATE_NO_WINDOW", 0)


def test_windows_notification_escapes_quotes(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "app.pipeline.subprocess.run",
        lambda *args, **kwargs: calls.append(args) or subprocess.CompletedProcess(args[0], 0, "", ""),
    )

    PosturePipeline._notify_windows("ErgoVision's alert", "Don't slouch")

    script = calls[0][0][-1]
    assert "ErgoVision''s alert" in script
    assert "Don''t slouch" in script


def test_macos_notification_keeps_osascript(monkeypatch):
    calls = []
    monkeypatch.setattr("app.pipeline.platform.system", lambda: "Darwin")
    monkeypatch.setattr("app.pipeline.subprocess.Popen", lambda *args, **kwargs: calls.append(args))

    pipeline = PosturePipeline.__new__(PosturePipeline)
    pipeline._last_reminder = ""
    pipeline._notify_native("ErgoVision", "Sit upright")

    assert calls[0][0][0] == "osascript"
