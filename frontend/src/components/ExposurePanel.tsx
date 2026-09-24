import type { PostureEvent } from '../types'

interface Props { posture: PostureEvent | null }

function pct(value: number) {
  const sign = value > 0 ? '+' : ''
  return `${sign}${Math.round(value * 100)}%`
}

export default function ExposurePanel({ posture }: Props) {
  const exposure = posture?.exposure
  if (!exposure) {
    return <div className="card insight-card"><div className="card-title">Ergonomic Exposure</div><p className="muted">Waiting for exposure data…</p></div>
  }

  return (
    <div className="card insight-card">
      <div className="card-title-row">
        <div className="card-title">Ergonomic Exposure</div>
        <span className={`dose-pill dose-${exposure.dose_level.toLowerCase()}`}>{exposure.dose_level}</span>
      </div>
      <div className="hero-metric">
        <strong>{exposure.cumulative_dose.toFixed(1)}</strong>
        <span>risk-seconds</span>
      </div>
      <div className="insight-grid-small">
        <div><span>Current risk</span><strong>{Math.round(exposure.instantaneous_risk * 100)}%</strong></div>
        <div><span>Continuous poor</span><strong>{exposure.continuous_poor_seconds.toFixed(0)} s</strong></div>
        <div><span>Postural drift</span><strong className={exposure.postural_drift > 0.08 ? 'risk-text' : ''}>{pct(exposure.postural_drift)}</strong></div>
        <div><span>Confidence weighted</span><strong>{Math.round(exposure.confidence_weighted_risk * 100)}%</strong></div>
      </div>
      <p className="panel-note">Exposure accumulates with duration and tracking confidence, then slowly recovers during lower-risk posture.</p>
    </div>
  )
}
