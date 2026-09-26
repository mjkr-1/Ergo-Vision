import { useEffect, useMemo, useRef, useState } from 'react'

interface ReminderSettings {
  movementBreaks: boolean
  desktopNotifications: boolean
  breakMinutes: number
}

const STORAGE_KEY = 'ergovision.reminders.v3'
const DEFAULTS: ReminderSettings = {
  movementBreaks: false,
  desktopNotifications: true,
  breakMinutes: 5,
}

function loadSettings(): ReminderSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? { ...DEFAULTS, ...JSON.parse(raw) } : DEFAULTS
  } catch {
    return DEFAULTS
  }
}

export default function ReminderPanel() {
  const [settings, setSettings] = useState<ReminderSettings>(loadSettings)
  const [permission, setPermission] = useState<NotificationPermission | 'unsupported'>(() => 'Notification' in window ? Notification.permission : 'unsupported')
  const [nextBreakSeconds, setNextBreakSeconds] = useState(settings.breakMinutes * 60)
  const settingsRef = useRef(settings)
  const lastBreakAt = useRef(Date.now())

  useEffect(() => {
    settingsRef.current = settings
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  }, [settings])

  useEffect(() => {
    const timer = window.setInterval(() => {
      const current = settingsRef.current
      const now = Date.now()
      const breakMs = Math.max(1, current.breakMinutes) * 60_000
      const untilBreak = Math.max(0, breakMs - (now - lastBreakAt.current))
      setNextBreakSeconds(Math.ceil(untilBreak / 1000))
      if (!current.movementBreaks || untilBreak > 0) return

      if ('Notification' in window && Notification.permission === 'granted' && current.desktopNotifications) {
        new Notification('ErgoVision · movement break', {
          body: 'Stand up, move around, and reset your posture for a minute or two.',
          tag: 'ergovision-break',
        })
      }
      lastBreakAt.current = now
    }, 1000)
    return () => window.clearInterval(timer)
  }, [])

  const requestNotifications = async () => {
    if (!('Notification' in window)) return
    const result = await Notification.requestPermission()
    setPermission(result)
  }

  const countdown = useMemo(() => {
    const minutes = Math.floor(nextBreakSeconds / 60)
    const seconds = nextBreakSeconds % 60
    return `${minutes}:${String(seconds).padStart(2, '0')}`
  }, [nextBreakSeconds])

  return (
    <div className="card reminder-card">
      <div className="card-title">Smart Alerts</div>
      <p className="reminder-copy">Posture correction overlays are automatic and cannot be manually dismissed. While correction is required, ErgoVision reinforces the alert every 3 seconds until a reliable correction is verified.</p>

      <label className="checkbox-row">
        <input type="checkbox" checked={settings.desktopNotifications} onChange={(event) => setSettings((current) => ({ ...current, desktopNotifications: event.target.checked }))} />
        <span>Mirror correction alerts to desktop notifications</span>
      </label>

      {'Notification' in window && permission !== 'granted' && settings.desktopNotifications && (
        <button className="button primary notification-button" onClick={requestNotifications}>
          {permission === 'denied' ? 'Desktop notifications blocked' : 'Enable desktop notifications'}
        </button>
      )}

      <div className="setting-grid one-row">
        <label>
          <span>Movement break</span>
          <select value={settings.breakMinutes} onChange={(event) => {
            const breakMinutes = Number(event.target.value)
            lastBreakAt.current = Date.now()
            setSettings((current) => ({ ...current, breakMinutes }))
          }}>
            <option value={1}>Every 1 min</option>
            <option value={2}>Every 2 min</option>
            <option value={5}>Every 5 min</option>
            <option value={7}>Every 7 min</option>
            <option value={10}>Every 10 min</option>
            <option value={15}>Every 15 min</option>
          </select>
        </label>
      </div>

      <div className="reminder-status">
        <span>Movement reminder</span>
        <strong>{settings.movementBreaks ? countdown : 'Paused'}</strong>
      </div>
      <button className="button" onClick={() => {
        lastBreakAt.current = Date.now()
        setSettings((current) => ({ ...current, movementBreaks: !current.movementBreaks }))
      }}>
        {settings.movementBreaks ? 'Pause movement reminders' : 'Enable movement reminders'}
      </button>
    </div>
  )
}
