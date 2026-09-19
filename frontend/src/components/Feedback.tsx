import type { PostureEvent } from '../types'

interface Props {
  posture: PostureEvent | null
}

export default function Feedback({ posture }: Props) {
  const messages = posture?.feedback ?? []

  return (
    <div className="card">
      <div className="card-title">Feedback</div>
      {messages.length === 0 ? (
        <p className="muted">Waiting for feedback…</p>
      ) : (
        <ul className="feedback-list">
          {messages.map((msg, i) => (
            <li key={i} className={msg.startsWith('Your posture looks good') ? 'good' : 'alert'}>
              {msg.startsWith('Your posture looks good') ? '✓ ' : '• '}
              {msg}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}