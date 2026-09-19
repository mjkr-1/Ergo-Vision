import type {
  AppConfig,
  CalibrationProfile,
  HealthStatus,
  PostureEvent,
  SessionStats,
} from '../types'

const BASE = '/api'

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init)
  if (!response.ok) {
    let message = `Request failed: ${response.status}`
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') message = body.detail
    } catch {
      // keep the HTTP fallback message
    }
    throw new Error(message)
  }
  return response.json()
}

export const api = {
  health: () => requestJson<HealthStatus>('/health'),
  currentPosture: () => requestJson<PostureEvent>(`${BASE}/posture/current`),
  sessionStats: () => requestJson<SessionStats>(`${BASE}/session/stats`),
  sessionStart: () => requestJson<SessionStats>(`${BASE}/session/start`, { method: 'POST' }),
  sessionStop: () => requestJson<SessionStats>(`${BASE}/session/stop`, { method: 'POST' }),
  sessionReset: () => requestJson<SessionStats>(`${BASE}/session/reset`, { method: 'POST' }),
  calibration: () => requestJson<CalibrationProfile>(`${BASE}/calibration`),
  captureCalibration: () => requestJson<CalibrationProfile>(`${BASE}/calibration/capture`, { method: 'POST' }),
  clearCalibration: () => requestJson<CalibrationProfile>(`${BASE}/calibration`, { method: 'DELETE' }),
  config: () => requestJson<AppConfig>(`${BASE}/config`),
}

export const streamUrl = `${BASE}/stream`
