# Security Policy

## Supported version

Security fixes are applied to the latest version on the `main` branch.

## Reporting a vulnerability

Please avoid opening a public GitHub issue for a vulnerability that could expose user data, execute unintended code, bypass local security boundaries or weaken camera/privacy guarantees.

Report the issue privately to the repository owner through an appropriate private contact method available on their GitHub profile. Include:

- affected version or commit
- reproduction steps
- expected and actual behaviour
- potential impact
- any suggested mitigation

Please allow reasonable time for investigation before public disclosure.

## Security model

ErgoVision is designed as a local application. It does not intentionally upload webcam frames or posture data to a remote service. Security changes should preserve that boundary unless a future architecture explicitly documents otherwise.
