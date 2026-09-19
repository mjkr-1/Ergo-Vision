import { useEffect, useMemo, useRef, useState } from 'react'
import type { PostureEvent } from '../types'

interface Props {
  posture: PostureEvent | null
}

interface ReminderSettings {
  enabled: boolean
  desktopNotifications: boolean
  breakMinutes: number
  poorPostureSeconds: number
  cooldownMinutes: number
}

const STORAGE_KEY = 'ergovision.reminders.v1'

const DEFAULTS: ReminderSettings = {
  enabled: false,
  desktopNotifications: true,
  breakMinutes: 30,
  poorPostureSeconds: 20,
  cooldownMinutes: 5,
}

function loadSettings(): ReminderSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? { ...DEFAULTS, ...JSON.parse(raw) } : DEFAULTS
  } catch {
    return DEFAULTS
  }
}

export default function ReminderPanel({ posture }: Props) {
  const [settings, setSettings] = useState<ReminderSettings>(loadSettings)
  const [permission, setPermission] = useState<NotificationPermission | 'unsupported'>(() =>
    'Notification' in window ? Notification.permission : 'unsupported',
  )
  const [lastAlert, setLastAlert] = useState('')
  const [nextBreakSeconds, setNextBreakSeconds] = useState(settings.breakMinutes * 60)
  const settingsRef = useRef(settings)
  const postureRef = useRef(posture)
  const lastBreakAt = useRef(Date.now())
  const poorSince = useRef<number | null>(null)
  const lastPoorAlertAt = useRef(0)

  useEffect(() => {
    settingsRef.current = settings
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  }, [settings])

  useEffect(() => {
    postureRef.current = posture
  }, [posture])

  const notificationAvailable = permission !== 'unsupported'

  const notify = (title: string, body: string) => {
    setLastAlert(`${title}: ${body}`)
    const current = settingsRef.current
    if (
      current.desktopNotifications &&
      notificationAvailable &&
      Notification.permission === 'granted'
    ) {
      new Notification(title, { body, tag: title, silent: false })
    }
  }

  useEffect(() => {
    const timer = window.setInterval(() => {
      const current = settingsRef.current
      const now = Date.now()
      const breakMs = Math.max(1, current.breakMinutes) * 60_000
      const untilBreak = Math.max(0, breakMs - (now - lastBreakAt.current))
      setNextBreakSeconds(Math.ceil(untilBreak / 1000))

      if (!current.enabled) return

      if (untilBreak <= 0) {
        notify('Movement break', 'Stand up, move around, and reset your posture for a minute or two.')
        lastBreakAt.current = now
      }

      const currentPosture = postureRef.current
      const isPoor =
        Boolean(currentPosture?.person_detected) &&
        (currentPosture?.status === 'WARNING' || currentPosture?.status === 'BAD')

      if (!isPoor) {
        poorSince.current = null
        return
      }

      if (poorSince.current === null) poorSince.current = now
      const poorForMs = now - poorSince.current
      const cooldownMs = Math.max(1, current.cooldownMinutes) * 60_000

      if (
        poorForMs >= current.poorPostureSeconds * 1000 &&
        now - lastPoorAlertAt.current >= cooldownMs
      ) {
        const feedback = currentPosture?.feedback?.[0] ?? 'Adjust your sitting position and return to your calibrated posture.'
        notify('Posture check', feedback)
        lastPoorAlertAt.current = now
        poorSince.current = now
      }
    }, 1000)

    return () => window.clearInterval(timer)
  }, [notificationAvailable])

  const requestNotifications = async () => {
    if (!notificationAvailable) return
    const result = await Notification.requestPermission()
    setPermission(result)
  }

  const toggleEnabled = async () => {
    if (!settings.enabled && settings.desktopNotifications && permission === 'default') {
      await requestNotifications()
    }
    lastBreakAt.current = Date.now()
    poorSince.current = null
    setSettings((current) => ({ ...current, enabled: !current.enabled }))
  }

  const resetBreakTimer = () => {
    lastBreakAt.current = Date.now()
    setNextBreakSeconds(settings.breakMinutes * 60)
    setLastAlert('Break timer restarted.')
  }

  const countdown = useMemo(() => {
    const minutes = Math.floor(nextBreakSeconds / 60)
    const seconds = nextBreakSeconds % 60
    return `${minutes}:${String(seconds).padStart(2, '0')}`
  }, [nextBreakSeconds])

  return (
    <div className="card reminder-card">
      <div className="card-title-row">
        <div className="card-title">Smart Reminders</div>
        <span className={`session-state ${settings.enabled ? 'active' : 'paused'}`}>
          {settings.enabled ? 'ON' : 'OFF'}
        </span>
      </div>

      <p className="reminder-copy">
        Get a movement prompt on a timer and a posture alert only after poor posture persists.
      </p>

      <div className="setting-grid">
        <label>
          <span>Movement break</span>
          <select
            value={settings.breakMinutes}
            onChange={(event) => {
              const breakMinutes = Number(event.target.value)
              lastBreakAt.current = Date.now()
              setSettings((current) => ({ ...current, breakMinutes }))
            }}
          >
            <option value={20}>Every 20 min</option>
            <option value={30}>Every 30 min</option>
            <option value={45}>Every 45 min</option>
            <option value={60}>Every 60 min</option>
          </select>
        </label>

        <label>
          <span>Poor-posture delay</span>
          <select
            value={settings.poorPostureSeconds}
            onChange={(event) =>
              setSettings((current) => ({ ...current, poorPostureSeconds: Number(event.target.value) }))
            }
          >
            <option value={10}>10 sec</option>
            <option value={20}>20 sec</option>
            <option value={30}>30 sec</option>
            <option value={60}>60 sec</option>
          </select>
        </label>
      </div>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={settings.desktopNotifications}
          onChange={(event) =>
            setSettings((current) => ({ ...current, desktopNotifications: event.target.checked }))
          }
        />
        <span>Use macOS/browser desktop notifications</span>
      </label>

      <div className="reminder-status">
        <span>Next movement break</span>
        <strong>{settings.enabled ? countdown : 'Paused'}</strong>
      </div>

      <div className="reminder-actions">
        <button className="button primary" onClick={toggleEnabled}>
          {settings.enabled ? 'Pause reminders' : 'Enable reminders'}
        </button>
        <button className="button" onClick={resetBreakTimer} disabled={!settings.enabled}>
          Reset timer
        </button>
      </div>

      {notificationAvailable && permission !== 'granted' && settings.desktopNotifications && (
        <button className="text-button reminder-permission" onClick={requestNotifications}>
          {permission === 'denied' ? 'Notifications are blocked in the browser' : 'Allow desktop notifications'}
        </button>
      )}

      {lastAlert && <p className="reminder-last-alert">{lastAlert}</p>}
    </div>
  )
}
