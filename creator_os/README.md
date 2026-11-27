# Dark Leyla Creator OS — standalone MVP

Dark Leyla Creator OS is a standalone FastAPI application with a creator dashboard, API-key authentication, encrypted provider credential storage, avatar registry, generation-draft queue, encrypted private media vault, manual export center and audit history.

## Working capabilities
- Server-side API keys created through a bootstrap-only endpoint and stored as SHA-256 hashes.
- Provider credentials encrypted at rest using AES-256-GCM.
- Private media upload, list, download and delete endpoints. Files are encrypted before writing to a private persistent volume; there is no public media URL. Supported formats: JPEG, PNG, WebP, GIF, MP4 and WebM, up to 100 MB per file. The dashboard can select a vaulted asset as the source for a manual export record.
- Avatar registry with adult-status, rights and likeness attestations.
- CelebMaker credential storage and live connection/options checks. No paid generation call is made.
- Generation draft queue and scheduled automation rules. Worker enqueues drafts only and never calls providers.
- Manual export records; Fanvue publishing remains manual.
- Fanvue OAuth 2.0 with PKCE account connection.
- Audit event history.
- SQLite for local evaluation; PostgreSQL supported through DATABASE_URL.
- Docker packaging.

## Private media storage requirement
Set DARKLEYLA_MEDIA_DIR to a persistent private volume. Never expose this directory as a static/public web directory. Back up the encrypted media volume and database together. Losing DARKLEYLA_MASTER_KEY makes stored credentials and media unrecoverable.

## Provider status
- **CelebMaker:** credential storage and connection/options checks are implemented. Paid generation remains locked pending verified per-mode cost controls and explicit per-job spend approval.
- **Fanvue:** OAuth account connection is implemented; publishing remains manual and no automated upload/post is performed.
- **OurDream:** disabled pending official API and commercial-use permission.
- **JOI:** disabled pending exact service identification, official API documentation and commercial-use rights.

## Local run
1. Change into the creator_os directory.
2. Create a Python 3.12 virtual environment.
3. Install with pip install -r requirements.txt.
4. Copy .env.example to .env and replace both placeholder secrets with generated random values.
5. Run uvicorn app:app --reload and open http://127.0.0.1:8000.
6. In a second terminal, run python worker.py with the same environment and database settings.

## Zero-cost local Docker deployment

This is the recommended no-subscription pilot path. It runs the API, scheduler, PostgreSQL and encrypted media volume on your own computer; it does not deploy to a public cloud.

1. Install Docker Desktop or Docker Engine with the Compose plugin.
2. From this directory, copy `.env.example` to `.env`.
3. Replace `DARKLEYLA_BOOTSTRAP_TOKEN`, `DARKLEYLA_MASTER_KEY` and `POSTGRES_PASSWORD` with long random secrets. Keep `.env` private and never commit it.
4. Run `docker compose up --build -d`.
5. Open `http://127.0.0.1:8000` and use the first-run bootstrap token to create the owner API key.
6. Check `http://127.0.0.1:8000/health` for the service health response.

The dashboard binds to localhost only. Docker named volumes persist the PostgreSQL database and encrypted media between container restarts. Use `docker compose down` to stop the stack without deleting data. **Do not use `docker compose down -v` unless you intend to permanently delete the database and media volumes.**

For a public deployment, do not expose this local Compose setup directly to the internet. Complete the production gate below and configure a supported host, TLS, backups, rate limits and secure session handling first.

## Production gate
Before public use, configure PostgreSQL, a private persistent media volume, encrypted backups, TLS, rate limiting, bootstrap-token rotation, OAuth callback hardening, account recovery, audit integrity anchoring and an external security review. This is a deployable MVP, not a production-hardened public SaaS. Paid generation and automated publishing remain disabled.
