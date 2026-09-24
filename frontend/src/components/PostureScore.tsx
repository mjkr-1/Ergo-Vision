import type { PostureEvent } from '../types'

interface Props {
  posture: PostureEvent | null
  connected: boolean
}

function labelFor(posture: PostureEvent | null): string {
  if (!posture || posture.status === 'NO_PERSON') return 'WAITING'
  if (posture.status === 'LOW_CONFIDENCE') return 'REPOSITION'
  if (posture.ergovision_index >= 75) return 'STABLE'
  if (posture.ergovision_index >= 45) return 'CAUTION'
  return 'CORRECT NOW'
}

export default function PostureScore({ posture, connected }: Props) {
  const lowConfidence = posture?.status === 'LOW_CONFIDENCE'
  const index = posture?.ergovision_index ?? 0
  const risk = Math.round((posture?.combined_risk ?? 0) * 100)
  const label = labelFor(posture)

  return (
    <div className={`card score-card evi-card evi-${label.toLowerCase().replace(/\s+/g, '-')}`}>
      <div className="card-title">ErgoVision Index</div>
      <div className="evi-ring" aria-label={`ErgoVision index ${index} out of 100`}>
        <div className="evi-ring-value">{lowConfidence ? '—' : index}</div>
        <div className="evi-ring-unit">/ 100</div>
      </div>
      <div className="evi-status">{label}</div>
      <div className="evi-meta">
        {lowConfidence ? 'Tracking is not reliable enough to score.' : `Current combined risk ${risk}%`}
      </div>
      {!connected && <div className="conn-badge">Reconnecting…</div>}
    </div>
  )
}
