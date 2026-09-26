import { useEffect, useRef, useState } from 'react'
import type { PostureEvent } from '../types'

interface Props { posture: PostureEvent | null }

const SETTINGS_KEY = 'ergovision.reminders.v3'

function desktopAlertsEnabled(): boolean {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY)
    if (!raw) return true
    return JSON.parse(raw)?.desktopNotifications !== false
  } catch {
    return true
  }
}

export default function CorrectionOverlay({ posture }: Props) {
  const state = posture?.intervention.state ?? 'NORMAL'
  const [pulse, setPulse] = useState(0)
  const latestRef = useRef(posture)
  latestRef.current = posture

  useEffect(() => {
    if (state !== 'ALERTING' && state !== 'VERIFYING') return

    const remind = () => {
      setPulse((value) => value + 1)
      const current = latestRef.current
      if (
        desktopAlertsEnabled() &&
        'Notification' in window &&
        Notification.permission === 'granted'
      ) {
        const body = current?.tracking.reliable
          ? current?.feedback?.[0] ?? 'Return to your calibrated upright posture.'
          : 'ErgoVision cannot verify correction until your head and shoulders are visible.'
        new Notification('ErgoVision · correction required', {
          body,
          tag: 'ergovision-correction',
          silent: false,
        })
      }
    }

    remind()
    const id = window.setInterval(remind, 3000)
    return () => window.clearInterval(id)
  }, [state])

  if (!posture || !['ALERTING', 'VERIFYING', 'CORRECTED'].includes(state)) return null

  const corrected = state === 'CORRECTED'
  const verifying = state === 'VERIFYING'
  const canVerify = posture.tracking.reliable
  const before = Math.round(posture.intervention.risk_before * 100)
  const after = Math.round(posture.intervention.risk_after * 100)

  return (
    <div className="correction-backdrop" role="alertdialog" aria-live="assertive">
      <div className={`correction-overlay ${corrected ? 'corrected' : ''} pulse-${pulse % 2}`}>
        {corrected ? (
          <>
            <div className="correction-icon">✓</div>
            <h2>Correction verified</h2>
            <div className="risk-drop"><strong>{before}%</strong><span>→</span><strong>{after}%</strong></div>
            <p>Risk reduced {posture.intervention.improvement_percent.toFixed(0)}% in {posture.intervention.correction_seconds.toFixed(1)} seconds.</p>
          </>
        ) : (
          <>
            <div className="correction-icon">!</div>
            <h2>Posture correction required</h2>
            <p className="correction-primary">{posture.feedback?.[0] ?? 'Return to your calibrated upright posture.'}</p>
            {!canVerify ? (
              <div className="verification warning">Tracking lost — correction cannot be verified. Keep your head and shoulders visible.</div>
            ) : verifying ? (
              <div className="verification">Hold the corrected posture… {posture.intervention.verification_seconds.toFixed(1)} / {posture.intervention.recovery_required_seconds.toFixed(0)} s</div>
            ) : (
              <div className="verification">Waiting for correction · current risk {Math.round(posture.combined_risk * 100)}%</div>
            )}
            <div className="no-dismiss">This alert closes automatically after a verified correction.</div>
          </>
        )}
      </div>
    </div>
  )
}
