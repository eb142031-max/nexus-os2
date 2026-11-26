# Dark Leyla Creator OS build baseline

## Product decision
Standalone application with its own UI, API, database, credential vault, avatar registry, generation queue, export center and audit events. It can later connect to META OS / MIOS through a separate governed integration. It does not depend on Vercel.

## Creator identities
One shared headquarters supports three identity families:
1. User's explicitly authorized self-likeness.
2. Original adult fictional Hydra Woman.
3. Original adult fictional WebSisters.

Each identity is versioned and separately governed. The app stores adult, rights and likeness attestations as user declarations, not verified identity evidence.

## MVP services
- FastAPI service and OpenAPI docs.
- API-key auth with bootstrap-only key creation; raw API keys are shown once and only their hashes are stored.
- AES-256-GCM encrypted provider credential storage.
- SQLAlchemy database layer with SQLite local mode and PostgreSQL URL support.
- Avatar registry, generation drafts, manual export records and activity ledger.
- Docker image and GitHub Actions tests.

## Provider integration posture
- CelebMaker: documented server-side key; validate with /me, inspect /credits and /generation-options. Draft generation is supported; actual paid generation remains locked until per-mode pricing and explicit per-job spend approval are implemented. Provider media retention is 30 days.
- Fanvue: manual export only. Current policy requires OAuth 2.0 with PKCE, registered app credentials, server-side secret storage, scopes and AI-content disclosure. No direct publish operation in MVP.
- OurDream: no connector execution unless the provider offers official API access and written commercial-use permission. No scraping or browser automation.
- JOI: no connector execution until the exact service, official API, commercial-use rights and data-processing terms are verified.

## Security boundaries
- No credentials in browser code, Git, logs or screenshots.
- Browser stores only the user's Dark Leyla API key in sessionStorage.
- Provider credentials are encrypted at rest using a server-only master key.
- Paid generation and platform publishing are fail-closed.
- Human review and AI disclosure are required before an export is marked ready for manual upload.
- Production requires TLS, managed PostgreSQL, private object storage, backups, rate limiting, key revocation, external security review and audit-integrity anchoring.

## Deployment status
The branch contains a containerized MVP package. It is not yet a production deployment. A hosting target, persistent database/storage, secret manager, domain/TLS and owner-controlled provider credentials are required for deployment.
