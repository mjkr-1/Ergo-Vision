import { streamUrl } from '../services/api'

export default function CameraFeed() {
  return (
    <div className="card">
      <div className="card-title">Live Camera</div>
      <div className="camera-wrap">
        <img src={streamUrl} alt="Camera feed" className="camera-feed" />
      </div>
    </div>
  )
}