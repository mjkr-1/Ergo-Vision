import { useEffect, useMemo, useRef, useState } from 'react'
import type { PostureEvent } from '../types'

interface Props { posture: PostureEvent | null }
interface Point { index:number; time:number }

export default function TrendChart({ posture }: Props) {
  const [points, setPoints] = useState<Point[]>([])
  const lastSample = useRef(0)

  useEffect(() => {
    if (!posture?.person_detected || !posture.tracking.reliable || posture.status === 'LOW_CONFIDENCE') return
    const now = Date.now()
    if (now - lastSample.current < 1000) return
    lastSample.current = now
    setPoints((current) => [...current, { index: posture.ergovision_index, time: now }].slice(-120))
  }, [posture])

  const polyline = useMemo(
    () => points.length < 2 ? '' : points.map((point, index) => `${(index / Math.max(points.length - 1, 1)) * 100},${100 - point.index}`).join(' '),
    [points],
  )
  const average = points.length ? Math.round(points.reduce((sum, point) => sum + point.index, 0) / points.length) : 0

  return (
    <div className="card trend-card">
      <div className="card-title-row">
        <div className="card-title">Ergonomic Trend</div>
        <span className="trend-average">2 min avg {points.length ? average : '—'}</span>
      </div>
      {points.length < 2 ? (
        <p className="muted">Trend appears after a few seconds of reliable monitoring.</p>
      ) : (
        <div className="trend-wrap" aria-label="ErgoVision index trend">
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="trend-svg">
            <line x1="0" y1="25" x2="100" y2="25" className="trend-guide good-guide" />
            <line x1="0" y1="55" x2="100" y2="55" className="trend-guide warning-guide" />
            <polyline points={polyline} className="trend-line" fill="none" />
          </svg>
          <div className="trend-labels"><span>100</span><span>0</span></div>
        </div>
      )}
    </div>
  )
}
