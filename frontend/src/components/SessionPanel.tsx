import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { SessionStats } from '../types'
import { formatDuration, formatPercent } from '../utils/format'

export default function SessionPanel() {
  const [stats, setStats] = useState<SessionStats | null>(null)

  useEffect(() => {
    let disposed = false
    const load = async () => {
      try {
        const s = await api.sessionStats()
        if (!disposed) setStats(s)
      } catch {
        // backend not ready yet; retry in a moment
      }
    }
    load()
    const id = setInterval(load, 3000)
    return () => {
      disposed = true
      clearInterval(id)
    }
  }, [])

  if (!stats) {
    return <div className="card"><div className="card-title">Session</div><p className="muted">Waiting…</p></div>
  }

  return (
    <div className="card">
      <div className="card-title">Session</div>
      <table className="metrics-table">
        <tbody>
          <tr><td>Monitoring Time</td><td>{formatDuration(stats.session_duration_seconds)}</td></tr>
          <tr><td>Good Posture</td><td>{formatPercent(stats.good_percentage)}</td></tr>
          <tr><td>Warning</td><td>{formatPercent(stats.warning_percentage)}</td></tr>
          <tr><td>Poor Posture</td><td>{formatPercent(stats.bad_percentage)}</td></tr>
          <tr><td>Average Score</td><td>{stats.average_score.toFixed(1)}</td></tr>
          <tr><td>Warnings</td><td>{stats.warning_count}</td></tr>
          <tr><td>Longest Poor Period</td><td>{formatDuration(stats.longest_poor_posture_seconds)}</td></tr>
        </tbody>
      </table>
    </div>
  )
}