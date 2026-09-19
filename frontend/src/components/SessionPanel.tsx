import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { SessionStats } from '../types'
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
        const s = await api.sessionStats()
        if (!disposed) {
          setStats(s)
          setError('')
        }
      } catch {
        if (!disposed) setError('Session service unavailable')
      }
    }
    load()
    const id = setInterval(load, 2000)
    return () => {
      disposed = true
      clearInterval(id)
    }
  }, [])

  const runAction = async (action: SessionAction) => {
    setBusy(action)
    setError('')
    try {
      const next =
        action === 'start'
          ? await api.sessionStart()
          : action === 'stop'
            ? await api.sessionStop()
            : await api.sessionReset()
      setStats(next)
    } catch {
      setError('Could not update the session')
    } finally {
      setBusy(null)
    }
  }

  if (!stats) {
    return (
      <div className="card">
        <div className="card-title">Session</div>
        <p className="muted">{error || 'Waiting…'}</p>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-title-row">
        <div className="card-title">Session</div>
        <span className={`session-state ${stats.active ? 'active' : 'paused'}`}>
          {stats.active ? 'MONITORING' : 'PAUSED'}
        </span>
      </div>

      <table className="metrics-table">
        <tbody>
          <tr><td>Monitoring Time</td><td>{formatDuration(stats.session_duration_seconds)}</td></tr>
          <tr><td>Good Posture</td><td>{formatPercent(stats.good_percentage)}</td></tr>
          <tr><td>Warning</td><td>{formatPercent(stats.warning_percentage)}</td></tr>
          <tr><td>Poor Posture</td><td>{formatPercent(stats.bad_percentage)}</td></tr>
          <tr><td>Away</td><td>{formatPercent(stats.no_person_percentage)}</td></tr>
          <tr><td>Average Score</td><td>{stats.average_score.toFixed(1)}</td></tr>
          <tr><td>Warnings</td><td>{stats.warning_count}</td></tr>
          <tr><td>Longest Poor Period</td><td>{formatDuration(stats.longest_poor_posture_seconds)}</td></tr>
        </tbody>
      </table>

      <div className="session-actions">
        <button
          className="button primary"
          disabled={stats.active || busy !== null}
          onClick={() => runAction('start')}
        >
          Resume
        </button>
        <button
          className="button"
          disabled={!stats.active || busy !== null}
          onClick={() => runAction('stop')}
        >
          Pause
        </button>
        <button
          className="button danger"
          disabled={busy !== null}
          onClick={() => runAction('reset')}
        >
          Reset
        </button>
      </div>
      {error && <p className="inline-error">{error}</p>}
    </div>
  )
}
