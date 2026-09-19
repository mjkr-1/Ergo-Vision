# Privacy

ErgoVision is designed around a simple rule: webcam analysis should remain local unless the architecture is intentionally changed and documented.

## What the application processes

During a running session, the backend reads webcam frames, detects face and pose landmarks, computes ergonomic measurements and stores the latest derived state in memory.

## What is not persisted

ErgoVision does not intentionally write raw webcam frames, annotated video or session history to disk. Session statistics are in-memory and disappear when the backend exits.

## Network access

Normal posture analysis does not require a remote inference API. Network access may occur when installing dependencies, downloading official MediaPipe models, or using normal Git/GitHub workflows.

## Camera stream

The React dashboard obtains the annotated camera view from the local FastAPI backend. Under the supported local deployment model, that traffic stays on the loopback interface (`127.0.0.1`).

## Accounts and telemetry

The current application has no account system, analytics service or application telemetry.

## Future hosted versions

A future browser-hosted version would need a new privacy review because browser camera capture and any remote processing would change the data boundary described here.
