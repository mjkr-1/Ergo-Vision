import type { AppConfig, HealthStatus, PostureEvent, SessionStats } from '../types'

const BASE = '/api'

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Request failed: ${res.status}`)
  return res.json()
}

export const api = {
  health: () => getJson<HealthStatus>('/health'),
  currentPosture: () => getJson<PostureEvent>(`${BASE}/posture/current`),
  sessionStats: () => getJson<SessionStats>(`${BASE}/session/stats`),
  config: () => getJson<AppConfig>(`${BASE}/config`),
}

export const streamUrl = `${BASE}/stream`