import { useEffect, useMemo, useRef, useState } from 'react'
import type { PostureEvent } from '../types'

interface Props {
  posture: PostureEvent | null
}

interface Point {
  score: number
  time: number
}

export default function TrendChart({ posture }: Props) {
  const [points, setPoints] = useState<Point[]>([])
  const lastSample = useRef(0)

  useEffect(() => {
    if (!posture?.person_detected) return
    const now = Date.now()
    if (now - lastSample.current < 1000) return
    lastSample.current = now
    setPoints((current) => [...current, { score: posture.score, time: now }].slice(-120))
  }, [posture])

  const polyline = useMemo(() => {
    if (points.length < 2) return ''
    return points
      .map((point, index) => {
        const x = (index / Math.max(points.length - 1, 1)) * 100
        const y = 100 - point.score
        return `${x},${y}`
      })
      .join(' ')
  }, [points])

  const average = points.length
    ? Math.round(points.reduce((sum, point) => sum + point.score, 0) / points.length)
    : 0

  return (
    <div className="card trend-card">
      <div className="card-title-row">
        <div className="card-title">Posture Trend</div>
        <span className="trend-average">2 min avg {points.length ? average : '—'}</span>
      </div>
      {points.length < 2 ? (
        <p className="muted">Trend appears after a few seconds of monitoring.</p>
      ) : (
        <div className="trend-wrap" aria-label="Posture score trend">
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="trend-svg">
            <line x1="0" y1="30" x2="100" y2="30" className="trend-guide good-guide" />
            <line x1="0" y1="60" x2="100" y2="60" className="trend-guide warning-guide" />
            <polyline points={polyline} className="trend-line" fill="none" />
          </svg>
          <div className="trend-labels"><span>100</span><span>0</span></div>
        </div>
      )}
    </div>
  )
}
