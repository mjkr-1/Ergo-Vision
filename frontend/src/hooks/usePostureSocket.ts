import { useEffect, useRef, useState } from 'react'
import type { PostureEvent } from '../types'

export function usePostureSocket() {
  const [posture, setPosture] = useState<PostureEvent | null>(null)
  const [connected, setConnected] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectDelay = useRef(1000)

  useEffect(() => {
    let disposed = false
    let reconnectTimer: number | null = null

    const cancelReconnect = () => {
      if (reconnectTimer !== null) {
        window.clearTimeout(reconnectTimer)
        reconnectTimer = null
      }
    }

    const connect = () => {
      if (disposed) return

      const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const socket = new WebSocket(`${proto}://${window.location.host}/ws/posture`)
      socketRef.current = socket

      socket.onopen = () => {
        if (disposed) {
          socket.close(1000, 'page inactive')
          return
        }
        reconnectDelay.current = 1000
        setConnected(true)
      }

      socket.onmessage = (event) => {
        if (disposed) return
        try {
          const data: PostureEvent = JSON.parse(event.data)
          setPosture(data)
        } catch {
          // ignore malformed message
        }
      }

      socket.onclose = () => {
        setConnected(false)
        if (!disposed) {
          reconnectTimer = window.setTimeout(connect, reconnectDelay.current)
          reconnectDelay.current = Math.min(reconnectDelay.current * 2, 5000)
        }
      }

      socket.onerror = () => socket.close()
    }

    const leavePage = () => {
      if (disposed) return
      disposed = true
      cancelReconnect()

      const socket = socketRef.current
      socketRef.current = null
      if (socket) {
        socket.onclose = null
        try {
          socket.close(1000, 'page closed')
        } catch {
          // Browser may already be tearing down the page.
        }
      }
    }

    const restorePage = (event: PageTransitionEvent) => {
      if (!event.persisted || !disposed) return
      disposed = false
      reconnectDelay.current = 1000
      connect()
    }

    window.addEventListener('pagehide', leavePage)
    window.addEventListener('beforeunload', leavePage)
    window.addEventListener('pageshow', restorePage)
    connect()

    return () => {
      leavePage()
      window.removeEventListener('pagehide', leavePage)
      window.removeEventListener('beforeunload', leavePage)
      window.removeEventListener('pageshow', restorePage)
    }
  }, [])

  return { posture, connected }
}
