import { useEffect, useRef, useState } from 'react'
import type { PostureEvent } from '../types'

export function usePostureSocket() {
  const [posture, setPosture] = useState<PostureEvent | null>(null)
  const [connected, setConnected] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectDelay = useRef(1000)

  useEffect(() => {
    let disposed = false

    const connect = () => {
      if (disposed) return
      const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const socket = new WebSocket(`${proto}://${window.location.host}/ws/posture`)

      socket.onopen = () => {
        reconnectDelay.current = 1000
        setConnected(true)
      }

      socket.onmessage = (event) => {
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
          setTimeout(connect, reconnectDelay.current)
          reconnectDelay.current = Math.min(reconnectDelay.current * 2, 5000)
        }
      }

      socket.onerror = () => socket.close()
      socketRef.current = socket
    }

    connect()

    return () => {
      disposed = true
      socketRef.current?.close()
    }
  }, [])

  return { posture, connected }
}