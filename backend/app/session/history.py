"""Local SQLite storage for anonymized completed and checkpointed sessions."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


class SessionHistory:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                """CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    ended_at TEXT NOT NULL,
                    local_date TEXT NOT NULL,
                    monitored_seconds REAL NOT NULL,
                    good_seconds REAL NOT NULL,
                    warning_seconds REAL NOT NULL,
                    bad_seconds REAL NOT NULL,
                    away_seconds REAL NOT NULL,
                    average_score REAL NOT NULL,
                    warning_count INTEGER NOT NULL,
                    bad_count INTEGER NOT NULL,
                    posture_alert_count INTEGER NOT NULL,
                    movement_alert_count INTEGER NOT NULL
                )"""
            )

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5.0)
        db.row_factory = sqlite3.Row
        return db

    def save_session(self, record: dict[str, Any]) -> None:
        started = datetime.fromisoformat(record["started_at"])
        local_date = started.astimezone().date().isoformat()
        values = (
            record["session_id"], record["started_at"], record["ended_at"], local_date,
            record["monitored_seconds"], record["good_seconds"], record["warning_seconds"],
            record["bad_seconds"], record["away_seconds"], record["average_score"],
            record["warning_count"], record["bad_count"], record["posture_alert_count"],
            record["movement_alert_count"],
        )
        with self._connect() as db:
            db.execute(
                """INSERT INTO sessions (
                       session_id, started_at, ended_at, local_date, monitored_seconds,
                       good_seconds, warning_seconds, bad_seconds, away_seconds, average_score,
                       warning_count, bad_count, posture_alert_count, movement_alert_count
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(session_id) DO UPDATE SET
                     ended_at=excluded.ended_at, local_date=excluded.local_date,
                     monitored_seconds=excluded.monitored_seconds, good_seconds=excluded.good_seconds,
                     warning_seconds=excluded.warning_seconds, bad_seconds=excluded.bad_seconds,
                     away_seconds=excluded.away_seconds, average_score=excluded.average_score,
                     warning_count=excluded.warning_count, bad_count=excluded.bad_count,
                     posture_alert_count=excluded.posture_alert_count,
                     movement_alert_count=excluded.movement_alert_count""",
                values,
            )

    def daily_reports(self, days: int = 14, today: date | None = None) -> list[dict[str, Any]]:
        days = max(1, min(int(days), 90))
        end = today or datetime.now().astimezone().date()
        start = end - timedelta(days=days - 1)
        with self._connect() as db:
            rows = db.execute(
                """SELECT local_date, COUNT(*) AS session_count,
                          SUM(monitored_seconds) AS monitored_seconds,
                          SUM(good_seconds) AS good_seconds,
                          SUM(warning_seconds) AS warning_seconds,
                          SUM(bad_seconds) AS bad_seconds, SUM(away_seconds) AS away_seconds,
                          SUM(average_score * monitored_seconds) AS weighted_score_sum,
                          SUM(warning_count) AS warning_count, SUM(bad_count) AS bad_count,
                          SUM(posture_alert_count) AS posture_alert_count,
                          SUM(movement_alert_count) AS movement_alert_count
                   FROM sessions WHERE local_date BETWEEN ? AND ? GROUP BY local_date""",
                (start.isoformat(), end.isoformat()),
            ).fetchall()

        by_date = {row["local_date"]: dict(row) for row in rows}
        reports = []
        for offset in range(days):
            day = (start + timedelta(days=offset)).isoformat()
            row = by_date.get(day)
            monitored = float(row["monitored_seconds"] or 0) if row else 0.0
            good = float(row["good_seconds"] or 0) if row else 0.0
            reports.append({
                "date": day,
                "has_data": bool(row and monitored > 0),
                "session_count": row["session_count"] if row else 0,
                "monitored_seconds": round(monitored, 1),
                "good_seconds": round(good, 1),
                "warning_seconds": round(float(row["warning_seconds"] or 0), 1) if row else 0.0,
                "bad_seconds": round(float(row["bad_seconds"] or 0), 1) if row else 0.0,
                "away_seconds": round(float(row["away_seconds"] or 0), 1) if row else 0.0,
                "good_percentage": round(good / monitored * 100, 1) if monitored else None,
                "average_score": round(row["weighted_score_sum"] / monitored, 1) if monitored else None,
                "warning_count": row["warning_count"] if row else 0,
                "bad_count": row["bad_count"] if row else 0,
                "posture_alert_count": row["posture_alert_count"] if row else 0,
                "movement_alert_count": row["movement_alert_count"] if row else 0,
            })
        return reports

    def delete_all(self) -> None:
        with self._connect() as db:
            db.execute("DELETE FROM sessions")
