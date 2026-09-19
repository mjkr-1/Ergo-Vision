import type { PostureEvent } from '../types'

interface Props {
  posture: PostureEvent | null
  connected: boolean
}

const STATUS_COLORS: Record<string, string> = {
  GOOD: '#2ecc71',
  WARNING: '#f39c12',
  BAD: '#e74c3c',
  NO_PERSON: '#95a5a6',
  UNKNOWN: '#95a5a6',
}

export default function PostureScore({ posture, connected }: Props) {
  const status = posture?.status ?? 'UNKNOWN'
  const score = posture?.score ?? 0
  const color = STATUS_COLORS[status] ?? '#95a5a6'

  return (
    <div className="card score-card">
      <div className="card-title">Current Posture</div>
      <div className="score-value" style={{ color }}>
        {score} / 100
      </div>
      <div className="score-status" style={{ background: color }}>
        {status}
      </div>
      {!connected && <div className="conn-badge">reconnecting…</div>}
    </div>
  )
}