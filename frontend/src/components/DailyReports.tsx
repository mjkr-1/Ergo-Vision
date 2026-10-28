import { useCallback, useEffect, useMemo, useState } from 'react'
import type { DailyReport } from '../types'
import { api } from '../services/api'
import { formatDuration } from '../utils/format'

export default function DailyReports() {
  const [reports, setReports] = useState<DailyReport[]>([])
  const [error, setError] = useState('')

  const refresh = useCallback(async () => {
    try {
      setReports(await api.dailyReports(14))
      setError('')
    } catch {
      setError('Daily reports are unavailable.')
    }
  }, [])

  useEffect(() => {
    refresh()
    const timer = window.setInterval(refresh, 30000)
    return () => window.clearInterval(timer)
  }, [refresh])

  const totals = useMemo(() => {
    const recordedDays = reports.filter((report) => report.has_data)
    const monitored = recordedDays.reduce((sum, report) => sum + report.monitored_seconds, 0)
    const good = recordedDays.reduce((sum, report) => sum + report.good_seconds, 0)
    const alerts = recordedDays.reduce((sum, report) => sum + report.posture_alert_count + report.movement_alert_count, 0)
    return {
      days: recordedDays.length,
      monitored,
      goodPercentage: monitored ? Math.round((good / monitored) * 100) : null,
      alerts,
    }
  }, [reports])

  const clearHistory = async () => {
    try {
      await api.clearReportHistory()
      await refresh()
    } catch {
      setError('Could not clear report history.')
    }
  }

  return (
    <section className="card daily-report-card">
      <div className="card-title-row">
        <div className="card-title">Daily Progress · 14 days</div>
        {reports.some((report) => report.has_data) && (
          <button className="text-button" onClick={clearHistory}>Clear reports</button>
        )}
      </div>

      {error && <p className="inline-error">{error}</p>}
      {!error && !reports.some((report) => report.has_data) ? (
        <p className="muted">Daily summaries will appear after a monitoring session is saved.</p>
      ) : (
        <>
          <div className="daily-report-summary">
            <div><strong>{formatDuration(totals.monitored)}</strong><span>Monitored</span></div>
            <div><strong>{totals.goodPercentage === null ? '—' : `${totals.goodPercentage}%`}</strong><span>Good posture</span></div>
            <div><strong>{totals.alerts}</strong><span>Alerts</span></div>
          </div>
          <p className="daily-report-note">Continuous monitored time.</p>
          <div className="daily-report-chart" role="img" aria-label="Good posture percentage by day over the last 14 days">
            {reports.map((report) => (
              <div className="daily-report-bar-column" key={report.date} title={report.has_data ? `${report.date}: ${report.good_percentage}% good posture` : `${report.date}: no data`}>
                <div className="daily-report-bar-track">
                  {report.has_data && (
                    <div className="daily-report-bar" style={{ height: `${Math.max(3, report.good_percentage ?? 0)}%` }} />
                  )}
                </div>
                <span>{new Date(`${report.date}T12:00:00`).toLocaleDateString(undefined, { day: 'numeric' })}</span>
              </div>
            ))}
          </div>
          <div className="daily-report-list">
            {reports.slice().reverse().map((report) => (
              <div className="daily-report-row" key={report.date}>
                <strong>{new Date(`${report.date}T12:00:00`).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}</strong>
                {report.has_data ? (
                  <span>{formatDuration(report.monitored_seconds)} · {report.good_percentage}% good · score {report.average_score} · {report.posture_alert_count + report.movement_alert_count} alerts</span>
                ) : <span className="muted">No data</span>}
              </div>
            ))}
          </div>
          <span className="sr-only">{totals.days} days with recorded monitoring</span>
        </>
      )}
    </section>
  )
}
