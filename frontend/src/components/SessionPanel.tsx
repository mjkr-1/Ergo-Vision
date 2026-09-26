import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { SessionStats } from '../types'
import { archiveSession } from '../utils/history'
import { formatDuration, formatPercent } from '../utils/format'

type SessionAction = 'start' | 'stop' | 'reset'

export default function SessionPanel() {
  const [stats, setStats] = useState<SessionStats | null>(null)
  const [busy, setBusy] = useState<SessionAction | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let disposed = false
    const load = async () => {
      try {
        const next = await api.sessionStats()
        if (!disposed) { setStats(next); setError('') }
      } catch {
        if (!disposed) setError('Session service unavailable')
      }
    }
    load()
    const id = setInterval(load, 2000)
    return () => { disposed = true; clearInterval(id) }
  }, [])

  const runAction = async (action: SessionAction) => {
    setBusy(action)
    setError('')
    try {
      if (action === 'reset' && stats) archiveSession(stats)
      const next = action === 'start' ? await api.sessionStart() : action === 'stop' ? await api.sessionStop() : await api.sessionReset()
      setStats(next)
    } catch {
      setError('Could not update the session')
    } finally {
      setBusy(null)
    }
  }

  if (!stats) return <div className="card"><div className="card-title">Session Intelligence</div><p className="muted">{error || 'Waiting…'}</p></div>

  return (
    <div className="card">
      <div className="card-title-row">
        <div className="card-title">Session Intelligence</div>
        <span className={`session-state ${stats.active ? 'active' : 'paused'}`}>{stats.active ? 'MONITORING' : 'PAUSED'}</span>
      </div>
      <table className="metrics-table">
        <tbody>
          <tr><td>Monitoring Time</td><td>{formatDuration(stats.session_duration_seconds)}</td></tr>
          <tr><td>Good Posture</td><td>{formatPercent(stats.good_percentage)}</td></tr>
          <tr><td>Exposure Dose</td><td>{stats.exposure_dose.toFixed(1)} · {stats.exposure_level}</td></tr>
          <tr><td>Postural Drift</td><td>{`${stats.postural_drift >= 0 ? '+' : ''}${Math.round(stats.postural_drift * 100)}%`}</td></tr>
          <tr><td>Blink Rate</td><td>{stats.blink_rate_per_min ? `${stats.blink_rate_per_min.toFixed(1)}/min` : '—'}</td></tr>
          <tr><td>Verified Corrections</td><td>{stats.successful_corrections} / {stats.intervention_count}</td></tr>
          <tr><td>Correction Rate</td><td>{stats.correction_rate_percent.toFixed(0)}%</td></tr>
          <tr><td>Last Risk Reduction</td><td>{stats.last_improvement_percent.toFixed(0)}%</td></tr>
          <tr><td>Longest Poor Period</td><td>{formatDuration(stats.longest_poor_posture_seconds)}</td></tr>
        </tbody>
      </table>

      <div className="session-actions">
        <button className="button primary" disabled={stats.active || busy !== null} onClick={() => runAction('start')}>Resume</button>
        <button className="button" disabled={!stats.active || busy !== null} onClick={() => runAction('stop')}>Pause</button>
        <button className="button danger" disabled={busy !== null} onClick={() => runAction('reset')}>Finish & Reset</button>
      </div>
      <p className="session-note">Finish & Reset archives the current summary locally and starts a fresh exposure/blink/intervention session.</p>
      {error && <p className="inline-error">{error}</p>}
    </div>
  )
}
