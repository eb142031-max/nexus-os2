# Nexus Intelligent Token Economy — Implementation Plan

**Status:** Planning baseline; implementation not started  
**Parent:** META OS / Trinity Nexus  
**Subsystem:** Nexus Engine  
**Federation:** ARGUS + all Shadow systems + Trinity Nexus + Hydra Lite  
**Governing intelligence:** Triune Prime Mandala  
**Founding doctrine:** Shadow Tiger / Golden Lotus / Void Moon (protected integration reserve)  
**First validation workload:** Shadow Eye ARGUS, using synthetic or explicitly authorized fixtures  
**Governance:** TriCell Referee  
**Version:** 1.1

## 1. Objective

Reduce cost per verified successful task while preserving authorization, tenant isolation, evidence provenance, audit integrity, and human review requirements.

The subsystem is shared infrastructure. Applications integrate through a stable task contract rather than implementing independent model-cost controls.

## 2. Federation scope

The NITE federation serves:
- ARGUS / Shadow Eye
- Shadowhand
- Shadowstrike
- Shadow Academy
- Shadowhawk Recon
- Lantern Veil
- Shadow Arena
- Trinity Nexus / Nexus Engine
- Hydra Lite
- Triune Prime Mandala
- Shadow Sentry
- Shadow Psyche

This list is a working system inventory based on the established architecture. Repository ownership, runtime boundaries, and implementation status must be verified before adapters are assigned.

### Founding Doctrine Reserve

Shadow Tiger, Golden Lotus, and Void Moon are preserved as independent founding source lineages. Their supplied doctrine catalogue is recorded in [the Founding Doctrine Registry](./FOUNDING_DOCTRINE_REGISTRY.md).

The registry is a catalogue and integration contract, not evidence that source manuals have been ingested or that integrations are enabled. Each consuming system requires a version-pinned, least-privilege, auditable approval. No automatic merger or activation is permitted.

## 3. Repository and environment inspection

Initial inspection found:
- The nexus-os2 repository currently has a minimal README describing a multi-tool Python operating system with Omega Hydra orchestration.
- Its default branch is main; the planning branch is docs/nexus-token-economy-plan.
- The connected Supabase project is shadow-eye-argus (project ref puiaslzebzcuqmifmtqs) and is currently **INACTIVE**.
- Supabase schema, migrations, RLS policies, and functions could not be inspected because the database endpoint reported that it was not accessible.
- No schema changes or project restoration were performed.

**Important:** The proposed schema below is a target design, not a description of existing deployed tables. Reconcile it against the actual repository and database before implementation.

## 4. Target architecture

1. **Triune Prime Mandala** — coordinates the three intelligence branches (Jarvis, Vyper, Minerva) and their nine personas. It proposes and coordinates; it does not bypass authorization.
2. **Shadow Sentry** — defensive vigilance, monitoring, institutional continuity and incident coordination.
3. **Shadow Psyche** — persona architecture, cognitive task models, reflective evaluation and bounded behavioral simulation; not clinical diagnosis.
4. **Task Classifier** — classifies task type, complexity, risk, and verification requirements.
5. **Budget Manager** — issues enforceable per-task input/output token, model-call, time, and monetary limits.
6. **Model Router** — chooses a provider/model capability tier (economy, standard, premium, or deterministic).
7. **Effort Governor** — assigns bounded reasoning effort to agents and subagents.
8. **Data Refinery** — performs deterministic filtering, deduplication, normalization, and relevance selection before model calls.
9. **Cost Observatory** — records usage, spend, latency, outcomes, escalation, and rework.
10. **TriCell Referee / Adversary Review** — independently checks scope, permissions, approval requirements, challenges assumptions, and validates audit events.

Execution path:

intake → classify → budget → refine → route → authorize → execute → verify → human review (when required) → audit/telemetry

A model downgrade must never bypass an authorization, evidence, or human-approval requirement.

## 5. Federation contracts

Every consumer adapter must declare:
- stable system and adapter identifiers
- supported task types and schema versions
- source and destination data classifications
- minimum permissions and prohibited actions
- budget and effort profile
- verification and human-approval requirements
- provenance and audit requirements
- timeout, retry, idempotency and rollback behavior
- owner, version, compatibility range and deprecation policy

Shared routing and budgets do not imply shared unrestricted data. Tenant, case, division and source-lineage boundaries remain enforced.

Agents cannot self-grant permissions, raise budgets, widen scope, or enable a protected doctrine integration.

## 6. Core contracts

### Task budget

- task_id
- max_input_tokens
- max_output_tokens
- max_model_calls
- max_cost_usd
- max_duration_seconds
- escalation_allowance

Enforcement is server-side. Proposed default thresholds: warning at 70%; approval required for additional budget at 90%; hard stop at 100%. These thresholds are configurable policy defaults, not permission to exceed an approved cap.

### Agent execution contract

- task ID and assigned role
- allowed and prohibited actions
- effort tier
- budget reference
- completion criteria
- escalation conditions
- approval requirements

### Routing classes

- **Deterministic:** hashing, parsing, filtering, arithmetic, schema validation.
- **Economy:** routine classification, extraction, and simple transformations.
- **Standard:** ordinary coding, research synthesis, and analysis.
- **Premium:** high-complexity architecture, ambiguous evidence analysis, or justified escalation.

Select models by measured capability, latency, reliability, and price—not by agent seniority or vendor branding. Keep provider identifiers configurable.

## 7. Data model proposal

Proposed logical entities (names are provisional; do not create tables until schema reconciliation):
- agent_tasks
- model_registry
- routing_decisions
- task_budgets
- usage_events
- agent_effort_profiles
- data_refinery_jobs
- task_outcomes
- cost_audit_events
- federation_systems
- system_adapters
- doctrine_assets
- doctrine_versions
- integration_grants
- integration_audit_events

Required properties:
- tenant-scoped ownership and row-level security
- append-only usage and audit history
- idempotency keys for task and provider-call retries
- server-only provider secrets
- immutable original evidence and doctrine references
- explicit provenance for derived/filtered records
- no user-editable metadata used as an authorization claim

## 8. Data Refinery safeguards

- Preserve the original input and its cryptographic digest.
- Record the filter version, parameters, counts, and exclusion reasons.
- Make excluded records recoverable.
- Keep source identifiers and provenance on derived records.
- Never treat a filtered-out record as disproven or irrelevant to exculpatory review.
- Separate exploratory relevance ranking from admissibility or verification decisions.

## 9. Observability and success measures

Track:
- input/output tokens and provider-reported cost per task
- cost per verified successful outcome
- cost per accepted pull request (where applicable)
- model and effort tier distribution
- cache hit rate where supported
- escalation and approval rates
- latency, failure, retry, and rework rates
- dataset counts before and after each refinery stage
- adapter-level success, policy denials, rollback and compatibility failures
- doctrine integration requests, grants, revocations and usage

Do not optimize for token count alone. Compare cost and quality together using fixed evaluation tasks and baseline measurements.

## 10. Delivery milestones

### M0 — Repository and environment baseline
- Confirm the canonical application repository and runtime.
- Restore database access only after explicit operational approval if the project remains inactive.
- Inspect migrations, tables, RLS, functions, secrets handling, and CI.
- Inventory all federation repositories and existing modules.
- Exit: verified baseline and a no-duplicate implementation map.

### M1 — Contracts and deterministic core
- Add typed task, budget, routing, federation and doctrine-registry contracts.
- Implement deterministic classification and budget calculation.
- Add unit tests for boundary conditions and idempotency.
- Exit: contracts compile and deterministic tests pass.

### M2 — Budget enforcement and usage ledger
- Add server-side budget reservation and accounting.
- Record provider usage and actual cost when returned; mark estimates distinctly.
- Enforce warnings, approval gates, hard stops, and safe partial completion.
- Exit: over-budget execution is blocked and ledger totals reconcile.

### M3 — Model routing and effort profiles
- Add provider-neutral capability registry and policy-based routing.
- Add per-agent effort profiles and explicit escalation.
- Test fallback, provider outage, and premium escalation limits.
- Exit: routing decisions are explainable and reproducible.

### M4 — Data Refinery
- Add deterministic filtering, deduplication, and normalization.
- Preserve source artifacts, hashes, filter metadata, and exclusions.
- Exit: original data is recoverable and output provenance is testable.

### M5 — TriCell governance and security
- Integrate scope checks, permissions, human approval, and tamper-evident audit events.
- Verify tenant isolation and RLS policies.
- Add doctrine integration grant, revocation and rollback checks.
- Exit: unauthorized actions and cross-tenant reads/writes are denied; protected doctrine is inaccessible without an explicit scoped grant.

### M6 — Cost Observatory and ARGUS pilot
- Add dashboards and baseline-vs-optimized evaluation.
- Pilot on synthetic or explicitly authorized ARGUS workloads.
- Report cost per verified outcome, quality, latency, escalation, and rework.
- Exit: measurable savings without unacceptable quality or control regression.

## 11. Acceptance test matrix

- Low-risk routine task selects an economical or deterministic path.
- Complex task escalates only under explicit policy.
- Budget hard cap stops additional model calls.
- Agent cannot raise its own budget or permissions.
- Duplicate request does not double-charge or duplicate side effects.
- Provider outage follows bounded fallback or fails closed.
- Filtering preserves original artifact and exclusion ledger.
- Missing provenance blocks a finding from becoming verified.
- Cross-tenant access is denied by RLS and server authorization.
- Audit-chain tampering is detected.
- Human approval is required for configured high-impact actions.
- Unapproved doctrine integration is denied.
- Doctrine version mismatch blocks adapter activation.
- Revoked doctrine grant blocks subsequent use and supports rollback.
- Benchmarks report both cost and outcome quality.

## 12. Security and operational boundaries

- No provider secret in browser/mobile code or repository.
- No service-role key exposed to clients.
- RLS on all exposed tables; policies must enforce tenant ownership, not merely authenticated status.
- Use server-side authorization; do not trust user-editable profile metadata.
- Avoid security-definer functions unless a reviewed requirement proves they are necessary.
- No automatic production migration or project restoration as part of this planning change.
- No live people-search or sensitive investigation dataset in cost benchmarks; use synthetic or authorized fixtures.
- Founding doctrine originals remain read-only; consumers receive only approved, version-pinned projections.
- No real-world harmful targeting instructions or unsafe martial arts deployment through an automated agent.

## 13. Open decisions before implementation

1. Confirm whether nexus-os2 is the canonical Trinity Nexus runtime repository or only a seed project.
2. Confirm whether ARGUS Supabase is intended to remain the initial database, and authorize restoration if it is still inactive.
3. Confirm provider/model inventory and whether cost values are provider-reported or estimated.
4. Confirm deployment environment and secrets-management boundary.
5. Confirm target baseline workloads and acceptable quality regression thresholds.
6. Ingest and verify the original Shadow Tiger, Golden Lotus and Void Moon source artifacts.
7. Confirm acronym expansions, definitions, and doctrine-to-lineage mappings.
8. Confirm the exact ownership and repository mapping for every Shadow system.

## 14. Current evidence status

| Item | Status |
|---|---|
| GitHub repository access | Verified |
| nexus-os2 default branch | Verified: main |
| Planning branch | Verified: docs/nexus-token-economy-plan |
| Existing repository content | Minimal README inspected |
| Supabase project identity | Verified |
| Supabase project state | Verified: inactive |
| Supabase schema and migrations | Not inspected; database inaccessible |
| Founding lineage names/catalogue | Recorded from user-provided architecture |
| Original doctrine artifacts | Not yet ingested or verified |
| Acronym expansions and lineage mappings | Pending |
| Federation adapters / runtime code | Not implemented |
| Database changes | None |
| Production deployment | None |

This plan is intentionally staged: first establish the real code/database baseline, preserve and verify source doctrine, then implement the smallest deterministic slice before introducing model-provider dependencies.
