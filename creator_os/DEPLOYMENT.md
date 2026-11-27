# Deployment checklist

## Private media storage
- Mount a persistent, private volume at DARKLEYLA_MEDIA_DIR (default ./private_media).
- Media is encrypted with AES-256-GCM before it is written. Never serve this directory as static content.
- Keep DARKLEYLA_MASTER_KEY in the host secret manager and back it up securely. Losing it makes stored media and provider credentials unrecoverable.
- Back up the encrypted media volume and PostgreSQL database together; test restore before storing valuable files.
- Media API routes require X-DarkLeyla-Key. Upload accepts JPEG, PNG, WebP, GIF, MP4 and WebM up to 100 MB per file.
- Every media download is authenticated, non-cacheable, and integrity-checked.

## Before launch
- [ ] Choose a host that supports long-running Python ASGI containers and persistent PostgreSQL.
- [ ] Provision managed PostgreSQL and a private persistent volume in the same region.
- [ ] Configure TLS, domain, health checks, and restricted bootstrap token.
- [ ] Set DARKLEYLA_BOOTSTRAP_TOKEN, DARKLEYLA_MASTER_KEY and DARKLEYLA_MEDIA_DIR in the host secret manager/config.
- [ ] Set DATABASE_URL to PostgreSQL; do not use SQLite for multi-user production.
- [ ] Create the first owner API key, store it in a password manager, and rotate the bootstrap token.
- [ ] Configure CelebMaker key server-side and test only /me, /credits and /generation-options initially.
- [ ] Keep paid generation disabled until actual per-mode costs and explicit job-level budgets are enforced.
- [ ] Keep Fanvue upload manual. Register an OAuth app only if creator API access is granted.
- [ ] Do not activate OurDream or JOI connectors without official APIs and commercial-use permission.
- [ ] Run security, backup/restore, mobile, keyboard and accessibility tests.

## Deployment boundary
The encrypted media-vault code is implemented, but its persistent volume and PostgreSQL database still need hosting configuration. No cloud host, domain, database, storage volume, provider account or production secret has been configured by this repository change.
