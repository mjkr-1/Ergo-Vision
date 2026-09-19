import { useEffect, useState } from 'react'
import CalibrationPanel from './components/CalibrationPanel'
import CameraFeed from './components/CameraFeed'
import Feedback from './components/Feedback'
import Metrics from './components/Metrics'
import PostureScore from './components/PostureScore'
import ReminderPanel from './components/ReminderPanel'
import SessionHistory from './components/SessionHistory'
import SessionPanel from './components/SessionPanel'
import TrendChart from './components/TrendChart'
import { usePostureSocket } from './hooks/usePostureSocket'
import { api } from './services/api'
import type { AppConfig, HealthStatus } from './types'

export default function App() {
  const { posture, connected } = usePostureSocket()
  const [config, setConfig] = useState<AppConfig | null>(null)
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [backendReachable, setBackendReachable] = useState(true)

  useEffect(() => {
    let disposed = false
    const load = async () => {
      try {
        const [cfg, currentHealth] = await Promise.all([api.config(), api.health()])
        if (!disposed) {
          setConfig(cfg)
          setHealth(currentHealth)
          setBackendReachable(true)
        }
      } catch {
        if (!disposed) setBackendReachable(false)
      }
    }
    load()
    const id = setInterval(load, 5000)
    return () => {
      disposed = true
      clearInterval(id)
    }
  }, [])

  const setupProblem =
    health &&
    !health.demo_mode &&
    (!health.camera_available || !health.model_loaded)

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1 className="title">ErgoVision</h1>
          <p className="subtitle">Private, calibrated posture monitoring while you work</p>
        </div>
        <div className="header-badges">
          {health?.demo_mode && <span className="badge demo">DEMO</span>}
          {connected ? (
            <span className="badge live">LIVE</span>
          ) : (
            <span className="badge offline">OFFLINE</span>
          )}
        </div>
      </header>

      {!backendReachable && (
        <div className="system-banner error">
          The ErgoVision backend is not reachable. Start the local server and refresh this page.
        </div>
      )}

      {setupProblem && (
        <div className="system-banner warning">
          {!health.camera_available && <span>Camera unavailable. </span>}
          {!health.model_loaded && <span>MediaPipe models unavailable. </span>}
          Check Terminal camera permission and run the Mac setup script again.
        </div>
      )}

      <main className="grid">
        <section className="grid-main">
          <PostureScore posture={posture} connected={connected} />
          <CameraFeed />
          <TrendChart posture={posture} />
          <Feedback posture={posture} />
        </section>
        <aside className="grid-side">
          <CalibrationPanel />
          <Metrics posture={posture} config={config} />
          <SessionPanel />
          <ReminderPanel posture={posture} />
          <SessionHistory />
          <div className="card privacy-card">
            <div className="card-title">Privacy</div>
            <p>Video processing stays on this computer. Camera frames are not stored or uploaded. Calibration is stored locally on this Mac; session history stays in this browser.</p>
          </div>
        </aside>
      </main>

      <footer className="footer">
        <span>ErgoVision · privacy-first posture monitoring</span>
        <span className="muted">Ergonomic guidance only · not a medical device</span>
      </footer>
    </div>
  )
}
