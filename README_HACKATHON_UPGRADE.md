# ErgoVision Hackathon v5 — drop-in upgrade bundle

This folder contains **complete replacement/new files**, using the current `main` branch structure of `mjkr-1/Ergo-Vision` as the base.

## What this upgrade adds

- confidence-weighted cumulative ergonomic exposure (risk-seconds)
- within-session postural drift
- personalized EAR baseline + blink state machine + rolling blink rate
- visual-load signal combining blink behaviour and calibrated proximity drift
- per-module confidence for head, shoulders, torso and eyes
- closed-loop posture intervention state machine
- persistent in-app correction overlay with **no dismiss button**
- repeated desktop correction reminder every **3 seconds** when permission is granted
- automatic alert dismissal only after **2 seconds of reliably verified GOOD posture**
- correction effectiveness: risk-before/risk-after, correction time, success rate
- upgraded session analytics and hackathon dashboard panels

## Copy into your repo

From the root of your local `Ergo-Vision` checkout, copy this bundle over the repository while preserving paths.

macOS/Linux:

```bash
cp -R /path/to/ergovision_hackathon_v5/backend/* backend/
cp -R /path/to/ergovision_hackathon_v5/frontend/* frontend/
```

Or manually replace/add the files shown in this bundle.

## Files added

```text
backend/app/ergonomics/exposure.py
backend/app/ergonomics/ocular.py
backend/app/ergonomics/intervention.py
backend/tests/test_exposure.py
backend/tests/test_ocular.py
backend/tests/test_intervention.py
frontend/src/components/ExposurePanel.tsx
frontend/src/components/OcularPanel.tsx
frontend/src/components/CorrectionOverlay.tsx
frontend/src/hackathon.css
```

## Files replaced

```text
backend/app/vision/landmarks.py
backend/app/vision/quality.py
backend/app/api/schemas.py
backend/app/api/routes.py
backend/app/pipeline.py
frontend/src/types/index.ts
frontend/src/App.tsx
frontend/src/components/PostureScore.tsx
frontend/src/components/TrendChart.tsx
frontend/src/components/Metrics.tsx
frontend/src/components/ReminderPanel.tsx
frontend/src/components/SessionPanel.tsx
```

## Validate before pushing

Run the repository's normal checks:

```bash
bash scripts/check.sh
```

Or separately:

```bash
cd backend
python -m pytest tests/ -v
```

```bash
cd frontend
npm run build
```

Then run locally:

```bash
bash scripts/run_mac.sh
```

or on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_windows.ps1
```

## Important deployment note

The current ErgoVision architecture is **local-first**: the Python backend owns the webcam. Do not deploy this unchanged to Render/Vercel/another remote server and expect a visitor's webcam to work; the remote Python process would see the server's hardware, not the visitor's camera.

For the hackathon, use the existing single-machine production mode:

```bash
cd frontend
npm run build
cd ..
# then run the local FastAPI launcher / existing run script
```

FastAPI serves the built React app locally, while webcam inference remains on-device.

## Demo sequence

1. Open ErgoVision and get tracking to EXCELLENT.
2. Calibrate upright posture.
3. Sit correctly for ~10 seconds so exposure drift gets a baseline and ocular EAR finishes calibrating.
4. Slouch / move head forward and hold it.
5. After 5 seconds the persistent correction overlay appears.
6. Keep bad posture: overlay remains; desktop notification repeats every 3 seconds if permission is enabled.
7. Correct posture and hold for 2 seconds.
8. Overlay changes to `Correction verified`, shows risk reduction and correction time, then disappears automatically.
9. Partially leave frame to demonstrate LOW_CONFIDENCE instead of a false GOOD score.

## Scientific wording for the demo

Call `cumulative_dose` a **prototype ergonomic exposure indicator** or **risk-seconds**, not a clinically validated dose. Call blink/proximity outputs **visual ergonomic indicators**, not a diagnosis of Computer Vision Syndrome. The custom 0–100 value is the **ErgoVision Index**, not RULA.
