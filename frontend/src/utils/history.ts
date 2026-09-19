import type { SessionHistoryEntry, SessionStats } from '../types'

const KEY = 'ergovision-session-history-v1'
const EVENT = 'ergovision-history-updated'

export function loadSessionHistory(): SessionHistoryEntry[] {
  try {
    const raw = window.localStorage.getItem(KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function archiveSession(stats: SessionStats): void {
  if (stats.session_duration_seconds < 10) return
  const entry: SessionHistoryEntry = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    ended_at: new Date().toISOString(),
    duration_seconds: stats.session_duration_seconds,
    average_score: stats.average_score,
    good_percentage: stats.good_percentage,
    warning_percentage: stats.warning_percentage,
    bad_percentage: stats.bad_percentage,
  }
  const next = [entry, ...loadSessionHistory()].slice(0, 30)
  window.localStorage.setItem(KEY, JSON.stringify(next))
  window.dispatchEvent(new Event(EVENT))
}

export function clearSessionHistory(): void {
  window.localStorage.removeItem(KEY)
  window.dispatchEvent(new Event(EVENT))
}

export function onHistoryUpdated(listener: () => void): () => void {
  window.addEventListener(EVENT, listener)
  return () => window.removeEventListener(EVENT, listener)
}
