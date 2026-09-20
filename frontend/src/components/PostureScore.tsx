import type { PostureEvent } from '../types'
interface Props { posture: PostureEvent | null; connected: boolean }
const COLORS: Record<string,string> = { GOOD:'#2ecc71', WARNING:'#f39c12', BAD:'#e74c3c', NO_PERSON:'#95a5a6', LOW_CONFIDENCE:'#95a5a6', UNKNOWN:'#95a5a6' }
export default function PostureScore({ posture, connected }: Props) {
  const status = posture?.status ?? 'UNKNOWN'; const score = posture?.score ?? 0; const color = COLORS[status] ?? '#95a5a6'; const low = status === 'LOW_CONFIDENCE'
  return <div className="card score-card"><div className="card-title">Current Posture</div><div className="score-value" style={{color}}>{low ? '—' : score} / 100</div><div className="score-status" style={{background:color}}>{low ? 'REPOSITION' : status}</div>{low && <div className="conn-badge">Tracking quality is too low for a reliable score</div>}{!connected && <div className="conn-badge">reconnecting…</div>}</div>
}
