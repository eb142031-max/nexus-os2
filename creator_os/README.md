# Dark Leyla Creator OS — standalone MVP

Dark Leyla Creator OS is a standalone FastAPI application with a creator dashboard, API-key authentication, encrypted provider credential storage, avatar registry, generation-draft queue, encrypted private media vault, manual export center and audit history.

## Working capabilities
- Server-side API keys created through a bootstrap-only endpoint and stored as SHA-256 hashes.
- Provider credentials encrypted at rest using AES-256-GCM.
- Private media upload, list, download and delete endpoints. Files are encrypted before writing to a private persistent volume; there is no public media URL. Supported formats: JPEG, PNG, WebP, GIF, MP4 and WebM, up to 100 MB per file.
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

## Production gate
Before public use, configure PostgreSQL, a private persistent media volume, encrypted backups, TLS, rate limiting, bootstrap-token rotation, OAuth callback hardening, account recovery, audit integrity anchoring and an external security review. This is a deployable MVP, not a production-hardened public SaaS. Paid generation and automated publishing remain disabled.
