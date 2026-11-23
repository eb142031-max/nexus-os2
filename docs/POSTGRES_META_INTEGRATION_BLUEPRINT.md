# Nexus Postgres Meta Integration Blueprint

Status: architecture proposal; documentation-only; not deployed.
Upstream: https://github.com/supabase/postgres-meta
Target repository: https://github.com/eb142031-max/nexus-os2

## 1. Decision

Use Supabase's supported APIs and PostgreSQL security controls for the current hosted Nexus backend. Do not depend on undocumented internal endpoints of Supabase's managed service.

Keep `supabase/postgres-meta` as an optional, portable metadata-management service for a privately operated or self-hosted deployment. It must never be exposed directly to the public internet.

In a self-hosted Supabase stack, postgres-meta is already part of the platform architecture and is normally consumed internally by Studio. Avoid deploying a duplicate instance without a clear operational need.

## 2. Upstream capability

postgres-meta is a TypeScript/Fastify REST service and library that normalizes PostgreSQL system-catalog metadata. Its route surface includes schemas, tables, columns, indexes, views, materialized views, functions, roles, privileges, policies, triggers, extensions, publications, SQL parsing/formatting/execution, and type generation.

The upstream README explicitly states that postgres-meta has no standalone security and must run behind a trusted proxy, locally, or in a private environment.

Repository inspection also found:
- `src/server/app.ts` registers CORS and routes but does not implement user authentication.
- `src/server/routes/query.ts` accepts SQL in the request body and executes it.
- `src/server/routes/roles.ts` exposes role list/create/update/delete operations.
- `src/server/routes/index.ts` accepts an encrypted connection header or uses the configured default database connection.
- `src/server/constants.ts` contains development defaults, including `SAMPLE_KEY` and a default database password. These must never be used in a deployed environment.
- `package.json` declares Node.js >=22.12.0. Pin dependencies and retain the lockfile.
- `package.json` declares MIT while the repository LICENSE and README declare Apache-2.0. Confirm upstream licensing metadata before redistributing a modified package; preserve the upstream LICENSE and notices.

## 3. Nexus architecture

Request path:

1. Nexus UI / Command Center
2. Supabase Auth identity verification
3. Nexus server-side authorization and tenant/project scope check
4. Operation policy engine and approval workflow
5. Internal metadata adapter
6. PostgreSQL using a dedicated least-privilege role
7. Audit event writer and independent retention

The browser must never connect directly to postgres-meta, carry database connection strings, or receive service-role/database credentials.

### TriCell responsibilities

- Observer: read-only metadata inspection and schema-drift reporting.
- Referee: validate requested operation, scope, permissions, risk, and migration plan.
- Executor: perform only explicitly authorized operations through a server-side adapter.

No agent may grant itself permissions or bypass the owner approval gate.

## 4. Permission tiers

### Tier 0 — Observe
- Read schema, table, column, index, relationship, policy, and privilege metadata.
- Generate schema documentation and type previews.
- No SQL mutation, role changes, or DDL.

### Tier 1 — Propose
- Parse and format SQL.
- Produce migration plans and diffs.
- Run non-mutating validation in an isolated development database.
- Submit a human-readable change proposal.

### Tier 2 — Approved change
- Execute an approved migration through the project's migration workflow.
- Require a named approver, exact target project, exact SQL/migration hash, expiration, and pre/post verification.
- Reject changes if the target schema or migration hash differs from the approved proposal.

### Tier 3 — Break-glass administration
- Reserved for owner-controlled, time-limited emergency access.
- Require explicit re-authentication, reason, scoped target, and enhanced audit.
- Never available to autonomous agents.

## 5. Mandatory security controls

- Keep postgres-meta on a private network; firewall its listener from public ingress.
- Place an authenticated gateway/BFF in front of it.
- Verify Supabase Auth sessions server-side; do not trust user-editable metadata for authorization.
- Enforce server-side role checks and tenant/project scoping on every operation.
- Use a read-only database role for inspection wherever possible.
- Separate read-only inspection from privileged migration execution.
- Store credentials in a secret manager; rotate them; remove all sample/default secrets.
- Set a strong random crypto key and never accept user-controlled database connection targets.
- Strip untrusted connection-routing headers at the edge and inject only server-generated values.
- Restrict database egress to approved hosts and ports.
- Configure explicit CORS origins; CORS is not authentication.
- Apply rate limits, request-size limits, query timeouts, and result-size limits.
- Log actor, tenant, target database, operation, approval ID, SQL/migration hash, timestamp, outcome, and correlation ID.
- Keep audit storage separate from the service's mutable application credentials; use append-only permissions and hash chaining.
- Run Supabase security/performance advisors and negative authorization tests before release.

## 6. Supabase hosted-project integration

For a managed Supabase project:
- Use Supabase Auth for identity.
- Use supported Supabase client/server APIs for application data.
- Use PostgreSQL migrations for schema changes.
- Apply RLS to every exposed table and grant only required privileges.
- Use server-side credentials only in trusted server environments.
- Never call undocumented internal Studio/postgres-meta endpoints as an application integration contract.

Supabase's current Data API exposure defaults have changed: do not assume newly created tables are automatically exposed. Review grants, exposed-schema settings, and RLS explicitly.

## 7. Implementation phases

1. Confirm the dedicated META OS Supabase project. Do not reuse the inactive ARGUS project without an explicit architecture decision.
2. Add a server-side Nexus database adapter and typed operation contracts.
3. Implement Observer-only metadata inventory and schema diff.
4. Add TriCell review and approval records.
5. Implement a migration proposal/approval/execution pipeline with immutable approval binding.
6. Add audit verification, monitoring, and negative authorization tests.
7. Only then evaluate a private postgres-meta deployment for self-hosted or multi-database administration needs.

## 8. Acceptance tests

- Unauthenticated requests are rejected.
- Authenticated users cannot inspect another tenant or project.
- Browser clients cannot reach postgres-meta or database credentials.
- Observer credentials cannot create, alter, or drop objects.
- Agents cannot perform Tier 2 or Tier 3 actions without the required human approval.
- Approval expires and cannot be reused for a different SQL hash or target.
- Unapproved or tampered migration plans fail closed.
- Audit records identify actor, target, decision, and outcome.
- Secrets and connection strings never appear in client bundles or logs.
- RLS and privilege tests cover both allowed and denied access paths.

## 9. Current repository/backend status

The inspected `nexus-os2` repository currently contains a README, LICENSE, `.gitignore`, and documentation; it does not yet contain the application or Supabase migration source needed for a working integration.

No Supabase project was modified or connected during this assessment. The dedicated META OS Supabase project remains to be selected. This blueprint is therefore a safe architecture handoff, not a claim of deployed functionality.
