import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { CalibrationProfile, PostureEvent } from '../types'
interface Props { posture: PostureEvent | null }
export default function CalibrationPanel({ posture }: Props) {
  const [profile,setProfile]=useState<CalibrationProfile|null>(null); const [busy,setBusy]=useState(false); const [error,setError]=useState('')
  useEffect(()=>{api.calibration().then(setProfile).catch(()=>setError('Calibration service unavailable'))},[])
  const ready=posture?.tracking.quality==='EXCELLENT'&&posture.tracking.reliable
  const capture=async()=>{setBusy(true);setError('');try{setProfile(await api.captureCalibration())}catch(err){setError(err instanceof Error?err.message:'Could not calibrate')}finally{setBusy(false)}}
  const clear=async()=>{setBusy(true);setError('');try{setProfile(await api.clearCalibration())}catch{setError('Could not reset calibration')}finally{setBusy(false)}}
  return <div className="card calibration-card"><div className="card-title-row"><div className="card-title">Personal Calibration</div><span className={`session-state ${profile?.calibrated?'active':'paused'}`}>{profile?.calibrated?'CALIBRATED':'DEFAULT'}</span></div><p className="muted calibration-copy">Sit upright and hold still for 2–3 seconds. Calibration requires high-quality tracking of your head and shoulders.</p>{!ready&&<p className="calibration-meta">Get Camera Setup to EXCELLENT before calibrating.</p>}<div className="calibration-actions"><button className="button primary" disabled={busy||!ready} onClick={capture}>{busy?'Working…':'Calibrate upright posture'}</button>{profile?.calibrated&&<button className="button" disabled={busy} onClick={clear}>Reset</button>}</div>{profile?.calibrated&&profile.captured_at&&<p className="calibration-meta">Saved locally · {new Date(profile.captured_at).toLocaleString()}</p>}{error&&<p className="inline-error">{error}</p>}</div>
}
