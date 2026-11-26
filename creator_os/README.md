# Dark Leyla Creator OS — standalone MVP

Dark Leyla Creator OS is a standalone FastAPI application with a private creator dashboard, API-key authentication, encrypted provider credential storage, avatar registry, generation-draft queue, manual export center and activity records.

## Current implementation

- Server-side API keys, created once through a bootstrap-only endpoint and stored as SHA-256 hashes.
- Provider credentials encrypted at rest using AES-256-GCM; the master key is supplied only through server environment configuration.
- Avatar registry with adult-status, rights and likeness attestations.
- CelebMaker connection check (/me, /credits, /generation-options) using its documented server-side bearer-key API.
- Generation draft queue. No provider generation request is submitted and no credits are spent.
- Manual export records. No Fanvue publishing or automated upload is performed.
- Fanvue, OurDream and JOI connector status disclosures.
- API audit event history.
- SQLite for local evaluation; PostgreSQL supported through DATABASE_URL.
- Docker packaging.

## Provider status

- **CelebMaker:** credential storage and live connection/options checks are implemented. Paid generation is deliberately locked until the app has verified per-mode cost controls and explicit per-job spend approval. API-generated media has a documented 30-day retention period; a future media-ingestion worker must archive approved files promptly.
- **Fanvue:** manual export is implemented. OAuth integration requires an app registered by the owner, approved client credentials, redirect URI and scopes. Current Fanvue policy specifies OAuth 2.0 with PKCE, not personal API keys. This MVP does not publish to Fanvue.
- **OurDream:** disabled. Its terms prohibit scraping/reverse-engineering and automated access outside an officially provided API, and restrict use to personal/non-commercial purposes. Re-enable only after written commercial permission and official API documentation.
- **JOI:** disabled pending identification of the exact service, official API documentation and commercial-use rights. No browser automation, scraping or terms circumvention.

## Local run

1. Change into the creator_os directory.
2. Create a Python 3.12 virtual environment and activate it.
3. Install dependencies with pip install -r requirements.txt.
4. Copy .env.example to .env and replace both placeholder secrets with generated random values.
5. Load the environment and run uvicorn app:app --reload.
6. Open http://127.0.0.1:8000. API documentation is at /docs.

Generate an API key using the dashboard first-run form or the bootstrap endpoint:
POST /api/v1/admin/api-keys with Authorization: Bearer YOUR_BOOTSTRAP_TOKEN and JSON body {"name":"Primary Creator Key"}.

The raw key is shown once. Use it as X-DarkLeyla-Key on protected endpoints.

## Docker

Build from this directory with docker build -t dark-leyla-creator-os .
Run with docker run --env-file .env -p 8000:8000 -v darkleyla-data:/app/data dark-leyla-creator-os.
For persistent Docker SQLite, set DATABASE_URL to sqlite:////app/data/darkleyla_creator.db.

## Production deployment gate

Before public production use:
1. Configure managed PostgreSQL, private media object storage and encrypted backups.
2. Put secrets in the host's secret manager; never commit .env.
3. Terminate TLS at a trusted reverse proxy and restrict the admin bootstrap endpoint.
4. Add rate limiting, key revocation UI, account recovery and audit integrity anchoring.
5. Complete external security review and browser/accessibility tests.
6. Register the Fanvue OAuth application and confirm scopes and current API version.
7. Verify provider credit estimates and obtain explicit per-job spend approval before enabling generation.
8. Implement signed webhook verification from provider-specific documentation before accepting callbacks.
9. Test backup/restore, retention and deletion procedures.

This is a deployable MVP package, not yet a production-hardened public SaaS. It intentionally fails closed on paid generation and does not automate publishing.
