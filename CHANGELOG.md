# Changelog

All notable changes to ErgoVision are documented here.

The project follows the spirit of Keep a Changelog and uses semantic versioning for user-facing releases.

## [Unreleased]

### Added

- configurable movement-break reminders
- sustained poor-posture notifications with cooldowns
- optional browser/macOS desktop notifications
- installable local macOS `.app` launcher
- explicit Mac stop/uninstall scripts
- personal neutral-posture calibration persisted locally on the Mac
- hip landmarks and relative pose depth for upper-body analysis
- torso-lean measurement
- calibrated slouch / hunch indicator
- slouch-aware scoring, classification and feedback
- live two-minute posture score trend
- local browser session-history summaries
- GitHub Actions validation workflow
- Dependabot configuration
- issue and pull request templates
- contribution, security and conduct documentation
- macOS diagnostics and repository validation scripts
- environment example and Makefile shortcuts

### Changed

- rebalanced the posture score so torso collapse and slouching materially affect the result
- expanded the camera overlay to show shoulder-to-hip torso lines when hips are visible
- hardened macOS setup and shutdown workflow
- made MediaPipe model downloads use a trusted certificate bundle
- split runtime and development Python dependencies
- refreshed architecture, API, privacy and troubleshooting documentation

## [1.0.0] - 2026-09-19

### Added

- local FastAPI + React application
- OpenCV webcam capture
- MediaPipe face and pose landmark detection
- ergonomic measurement, smoothing, classification and scoring pipeline
- live annotated camera stream
- WebSocket posture updates
- session metrics with pause, resume and reset
- automatic model provisioning
- macOS setup and run scripts
- demo mode and backend test suite
