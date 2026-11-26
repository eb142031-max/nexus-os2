# Deployment checklist

## Before launch
- [ ] Choose a host that supports long-running Python ASGI containers and persistent PostgreSQL.
- [ ] Provision a managed PostgreSQL database in the same region as the app.
- [ ] Provision private object storage and an encrypted backup policy before storing user media.
- [ ] Configure TLS, domain, health checks, and a restricted bootstrap endpoint.
- [ ] Set DARKLEYLA_BOOTSTRAP_TOKEN and DARKLEYLA_MASTER_KEY in the host secret manager.
- [ ] Set DATABASE_URL to PostgreSQL; do not use SQLite for multi-user production.
- [ ] Create the first owner API key, store it in a password manager, and rotate the bootstrap token.
- [ ] Configure CelebMaker key server-side and test only /me, /credits and /generation-options initially.
- [ ] Keep paid generation disabled until actual per-mode costs and explicit job-level budgets are enforced.
- [ ] Keep Fanvue upload manual. Register an OAuth app only if creator API access is granted.
- [ ] Do not activate OurDream or JOI connectors without official APIs and commercial-use permission.
- [ ] Run security, backup/restore, mobile, keyboard and accessibility tests.
- [ ] Confirm AI disclosure and creator identity/likeness permissions before any content export.

## Deployment boundary
The container is deployable, but no cloud host, domain, database, storage bucket, provider account or production secret has been configured by this repository change.
