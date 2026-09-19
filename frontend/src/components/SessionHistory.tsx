import { useEffect, useState } from 'react'
import type { SessionHistoryEntry } from '../types'
import { clearSessionHistory, loadSessionHistory, onHistoryUpdated } from '../utils/history'
import { formatDuration } from '../utils/format'

export default function SessionHistory() {
  const [history, setHistory] = useState<SessionHistoryEntry[]>(() => loadSessionHistory())

  useEffect(() => onHistoryUpdated(() => setHistory(loadSessionHistory())), [])

  return (
    <div className="card history-card">
      <div className="card-title-row">
        <div className="card-title">Recent Sessions</div>
        {history.length > 0 && (
          <button className="text-button" onClick={() => { clearSessionHistory(); setHistory([]) }}>Clear</button>
        )}
      </div>
      {history.length === 0 ? (
        <p className="muted">Finished sessions are saved only in this browser.</p>
      ) : (
        <div className="history-list">
          {history.slice(0, 5).map((entry) => (
            <div className="history-row" key={entry.id}>
              <div>
                <strong>{entry.average_score.toFixed(0)}/100</strong>
                <span>{new Date(entry.ended_at).toLocaleDateString()}</span>
              </div>
              <div className="history-right">
                <span>{formatDuration(entry.duration_seconds)}</span>
                <span>{entry.good_percentage.toFixed(0)}% good</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
