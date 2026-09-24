import { useEffect, useRef, useState } from 'react'

const FRAME_INTERVAL_MS = 125

export default function CameraFeed() {
  const [frameUrl, setFrameUrl] = useState(
    `/api/stream/frame?t=${Date.now()}`,
  )

  const [available, setAvailable] = useState(true)
  const timerRef = useRef<number | null>(null)

  useEffect(() => {
    const refreshFrame = () => {
      setFrameUrl(`/api/stream/frame?t=${Date.now()}`)
    }

    timerRef.current = window.setInterval(
      refreshFrame,
      FRAME_INTERVAL_MS,
    )

    return () => {
      if (timerRef.current !== null) {
        window.clearInterval(timerRef.current)
      }
    }
  }, [])

  return (
    <div className="card">
      <div className="card-title-row">
        <div className="card-title">Live Camera</div>

        <span
          className={`session-state ${
            available ? 'active' : 'paused'
          }`}
        >
          {available ? 'LIVE' : 'WAITING'}
        </span>
      </div>

      <div className="camera-wrap">
        <img
          src={frameUrl}
          alt="Live ErgoVision camera feed"
          className="camera-feed"
          onLoad={() => setAvailable(true)}
          onError={() => setAvailable(false)}
        />

        {!available && (
          <div className="camera-unavailable">
            Waiting for camera frames…
          </div>
        )}
      </div>
    </div>
  )
}
