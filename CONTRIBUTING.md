# Contributing to ErgoVision

Thanks for helping improve ErgoVision. Changes should preserve the project's local-first privacy model and keep ergonomic calculations understandable and testable.

## Before you start

- Search existing issues before opening a new one.
- Use the bug or feature request templates when applicable.
- For larger architectural changes, open an issue before investing in implementation.
- Do not add cloud video upload, telemetry or external inference without explicit design discussion.

## Local setup

On macOS:

```bash
git clone https://github.com/mjkr-1/Ergo-Vision.git
cd Ergo-Vision
bash scripts/setup_mac.sh
```

Run the validation suite before submitting a pull request:

```bash
bash scripts/check.sh
```

## Development principles

- Keep camera capture single-owner inside the posture pipeline.
- Keep ergonomic math separate from transport/API code.
- Handle missing landmarks and unavailable hardware gracefully.
- Use Pydantic response models for backend API contracts.
- Keep frontend types aligned with backend schemas.
- Prefer small, focused changes over broad unrelated refactors.
- Add or update tests when behaviour changes.
- Do not commit MediaPipe `.task` model files.

## Pull requests

A good pull request should include:

- a concise explanation of the problem and solution
- testing performed
- screenshots for visible UI changes
- documentation updates for API, setup or architecture changes
- no unrelated generated files or local environment artifacts

The CI workflow must pass before merge.

## Commit messages

Use short imperative messages where possible, for example:

```text
fix: release camera cleanly on suspended launcher
feat: add posture calibration workflow
docs: clarify local privacy model
```
