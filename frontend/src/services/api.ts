import type { AppConfig, HealthStatus, PostureEvent, SessionStats } from '../types'

const BASE = '/api'

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  if (!res.ok) throw new Error(`Request failed: ${res.status}`)
  return res.json()
}

export const api = {
  health: () => requestJson<HealthStatus>('/health'),
  currentPosture: () => requestJson<PostureEvent>(`${BASE}/posture/current`),
  sessionStats: () => requestJson<SessionStats>(`${BASE}/session/stats`),
  sessionStart: () => requestJson<SessionStats>(`${BASE}/session/start`, { method: 'POST' }),
  sessionStop: () => requestJson<SessionStats>(`${BASE}/session/stop`, { method: 'POST' }),
  sessionReset: () => requestJson<SessionStats>(`${BASE}/session/reset`, { method: 'POST' }),
  config: () => requestJson<AppConfig>(`${BASE}/config`),
}

export const streamUrl = `${BASE}/stream`
