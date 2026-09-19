import { useEffect, useState } from 'react'
import CameraFeed from './components/CameraFeed'
import Feedback from './components/Feedback'
import Metrics from './components/Metrics'
import PostureScore from './components/PostureScore'
import SessionPanel from './components/SessionPanel'
import { usePostureSocket } from './hooks/usePostureSocket'
import { api } from './services/api'
import type { AppConfig, HealthStatus } from './types'

export default function App() {
  const { posture, connected } = usePostureSocket()
  const [config, setConfig] = useState<AppConfig | null>(null)
  const [health, setHealth] = useState<HealthStatus | null>(null)

  useEffect(() => {
    let disposed = false
    const load = async () => {
      try {
        const [cfg, h] = await Promise.all([api.config(), api.health()])
        if (!disposed) {
          setConfig(cfg)
          setHealth(h)
        }
      } catch {
        // backend not ready
      }
    }
    load()
    const id = setInterval(load, 5000)
    return () => {
      disposed = true
      clearInterval(id)
    }
  }, [])

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1 className="title">ErgoVision</h1>
          <p className="subtitle">Your real-time ergonomics assistant</p>
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

      <main className="grid">
        <section className="grid-main">
          <PostureScore posture={posture} connected={connected} />
          <CameraFeed />
          <Feedback posture={posture} />
        </section>
        <aside className="grid-side">
          <Metrics posture={posture} config={config} />
          <SessionPanel />
        </aside>
      </main>

      <footer className="footer">
        <span>ErgoVision · privacy-first posture monitoring</span>
        <span className="muted">Not a medical device.</span>
      </footer>
    </div>
  )
}