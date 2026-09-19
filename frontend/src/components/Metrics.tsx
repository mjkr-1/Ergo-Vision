import type { AppConfig, PostureEvent } from '../types'

interface Props {
  posture: PostureEvent | null
  config: AppConfig | null
}

const SHOULDER_LABEL = (score: number) => {
  if (score >= 0.95) return 'Good'
  if (score >= 0.75) return 'Slight Imbalance'
  return 'Poor'
}

const DISTANCE_LABEL = (forward: number, cfg: AppConfig | null) => {
  if (!cfg) return '—'
  if (forward >= cfg.forward_head_bad) return 'Too Close'
  if (forward >= cfg.forward_head_warning) return 'Close'
  return 'Normal'
}

export default function Metrics({ posture, config }: Props) {
  const m = posture?.measurements
  if (!m) return <div className="card"><div className="card-title">Ergonomic Metrics</div><p>Waiting for data…</p></div>

  return (
    <div className="card">
      <div className="card-title">Ergonomic Metrics</div>
      <table className="metrics-table">
        <tbody>
          <tr><td>Head Tilt</td><td>{m.head_tilt_degrees.toFixed(1)}°</td></tr>
          <tr><td>Shoulder Angle</td><td>{m.shoulder_alignment_degrees.toFixed(1)}°</td></tr>
          <tr><td>Shoulder Alignment</td><td>{SHOULDER_LABEL(m.shoulder_alignment_score)}</td></tr>
          <tr><td>Neck Offset</td><td>{(m.neck_offset > 0 ? '+' : '') + m.neck_offset.toFixed(2)}</td></tr>
          <tr><td>Screen Distance</td><td>{DISTANCE_LABEL(m.forward_head_indicator, config)}</td></tr>
          <tr><td>Gaze Angle</td><td>{m.gaze_vertical_degrees.toFixed(1)}°</td></tr>
        </tbody>
      </table>
    </div>
  )
}