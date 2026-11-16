# Modern Web Guidance 1.0 — NEXUS adoption gate

Status: proposed integration; **not installed or benchmarked in this repository**.

Official upstream: https://github.com/GoogleChrome/modern-web-guidance

## Installation and privacy
Run in a disposable development environment after verifying the npm package and version:
```sh
export DISABLE_TELEMETRY=1
npx modern-web-guidance@1.0.0 install
npx modern-web-guidance@1.0.0 legacy-scan .
```
If the exact pinned package is unavailable, stop and inspect the official package metadata. Never silently fall back to latest. The interactive installer may require choosing the coding agent.

## Scope
- Review accessibility: keyboard focus, semantic forms, reduced motion, dialog behavior.
- Review performance: layout shift, image loading, main-thread tasks.
- Review security: CSP, safe DOM updates, no unsanitized HTML.
- Review browser compatibility against documented support targets.
- Preserve offline/local-first functionality and mobile usability.

## HYDRA policy
The skill is advisory only. It cannot grant authority, bypass Hall 5, alter RLS, change secrets, initiate external scans, or deploy automatically. All code modifications require diff review. Never upload private mission data to third-party tooling.

## Acceptance gates
1. Capture baseline scan results on the real Citadel source.
2. Apply changes in an isolated branch.
3. Run lint/typecheck/unit tests and Playwright keyboard/mobile/reduced-motion checks.
4. Run negative authorization and cross-domain isolation tests.
5. Review dependencies and generated code.
6. Obtain human approval before promoting a deployment.

## Current blockers
The `nexus-os2` repository currently contains no Citadel application code; it has a README, LICENSE, and .gitignore. Import the verified Citadel source or identify its canonical repository before a meaningful baseline or modernization scan.
