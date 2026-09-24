import type { PostureEvent } from '../types'

interface Props { posture: PostureEvent | null }

export default function OcularPanel({ posture }: Props) {
  const ocular = posture?.ocular
  if (!ocular) {
    return <div className="card insight-card"><div className="card-title">Visual Ergonomics</div><p className="muted">Waiting for eye tracking…</p></div>
  }

  const blinkReady = ocular.calibrated && ocular.observation_seconds >= 10
  return (
    <div className="card insight-card">
      <div className="card-title-row">
        <div className="card-title">Visual Ergonomics</div>
        <span className={`tracking-badge ${ocular.available ? 'excellent' : 'poor'}`}>{ocular.available ? `${Math.round(ocular.confidence * 100)}%` : 'UNAVAILABLE'}</span>
      </div>
      <div className="insight-grid-small ocular-grid">
        <div><span>Eye Aspect Ratio</span><strong>{ocular.available ? ocular.ear.toFixed(3) : '—'}</strong></div>
        <div><span>Blink rate</span><strong>{blinkReady ? `${ocular.blink_rate_per_min.toFixed(1)}/min` : 'Warming up'}</strong></div>
        <div><span>Blinks observed</span><strong>{ocular.blink_count}</strong></div>
        <div><span>Visual load</span><strong>{Math.round(ocular.visual_load * 100)}%</strong></div>
        <div><span>Proximity drift</span><strong>{`${ocular.proximity_drift >= 0 ? '+' : ''}${Math.round(ocular.proximity_drift * 100)}%`}</strong></div>
        <div><span>Personal eye baseline</span><strong>{ocular.calibrated ? 'READY' : 'CALIBRATING'}</strong></div>
      </div>
      <p className="panel-note">Blink and proximity signals are ergonomic indicators only; they are not a diagnosis of eye disease or CVS.</p>
    </div>
  )
}
