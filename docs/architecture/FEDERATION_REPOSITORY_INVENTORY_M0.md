# META OS Federation — Repository Inventory and M0 Baseline

**Review date:** 2026-11-10  
**Status:** Partial repository inventory; M0 not yet fully passed  
**Branch:** `docs/nexus-token-economy-plan`  
**Purpose:** Record verified repository evidence and identify safe integration seams before implementation.

## Executive finding

The accessible GitHub repositories do not yet demonstrate a single, canonical, implemented runtime for the complete federation. The strongest existing reusable architecture is split across:
- Shadowhand / Shadow Command: a documented consulting platform architecture and a canonical TypeScript domain contract, but its README explicitly says the application, migrations, authentication and Aegir runtime are not implemented in that repository.
- Guardian OS: a separate canonical martial-arts/community-security architecture with an isolated deterministic G5A synthetic proof fixture and tests; the documentation explicitly limits what those tests prove.
- ARGUS: the public repository currently exposes only a minimal README identifying it as investigation software.
- Trinity Nexus: the accessible `nexus-os2` README is minimal and describes a multi-tool Python OS with Omega Hydra orchestration; the current repo is being used as a planning host, not yet verified as the federation runtime.
- `super-funicular`: its README identifies a blank Codespaces Next.js starter, not an established federation service.

This is a documentation/code-surface inventory, not a complete audit of every private or unindexed file. GitHub code search did not return a full repository tree. Findings below distinguish verified files from planned structures and unknowns.

## Repository findings

### 1. `eb142031-max/shadowhandmonastery` — Shadow Command / Shadowhand

**Verified source files**
- `README.md`
- `SHADOW_CHARTER.md`
- `docs/ARCHITECTURE.md`
- `docs/SPRINT_01.md`
- `packages/types/core.ts`

**Verified architecture**
- Product mission: AI-assisted security operations for consultants and investigators.
- Operational domains locked in charter: Shadow Intelligence, Shadow Defense, Shadow Investigations.
- Planned stack: Next.js, TypeScript, Tailwind, shadcn/ui; Supabase/Postgres/Auth/Storage; server-side OpenAI gateway; Vercel; pnpm workspaces.
- Planned architecture layers: client, type-safe API gateway, database/RLS, AI orchestration (Aegir Shadow Abbot).
- Specialist roles in canonical types: Shadow Scholar, Shadow Sentinel, Shadow Investigator, Shadow Scribe.
- Core types include organization, user, client, engagement, case, finding, evidence, asset, task, report, audit event, Aegir request/response and case summary.
- `CORE_TYPES_VERSION` is `1.0.0`.
- The charter requires human review for consequential actions, organization isolation, least privilege, audit trails, server-side secrets, and reuse of canonical types.

**Important implementation truth**
The repository README explicitly states that the application, database migrations, authentication, and Aegir runtime described in the plans are not implemented here yet. The architecture directory tree is a target structure; Sprint 1 is a specification, not a completion report. The documented database and UI paths must not be treated as present implementation until independently verified.

**Integration recommendation**
Use the existing core types as a source contract after version and ownership review. Do not copy the same entities into NITE or create a second AuditEvent interface. Add NITE/federation contracts as a separately versioned package or extension only after approval; do not silently mutate locked core types.

### 2. `eb142031-max/-hydra-omega-ecosystem-.ellbush1420-bushido.github.com-` — Guardian OS + separate game prototype

**Verified source files**
- `README.md`
- `docs/guardian/GUARDIAN_OS_PRIMARY_ARCHITECTURE.md`
- `docs/guardian/G5A_BOUNDARY.md`
- `tests/guardian.test.cjs`
- `.github/workflows/guardian-checks.yml`

**Verified Guardian architecture**
- Guardian's mission covers martial arts/self-defense, fitness, safer sacred/community spaces, volunteer security-team education, youth/family programs and instructor education.
- Martial rank and Guardian functional qualification are explicitly separate rails.
- Human TriCell roles are Steward, Trainer and Instructor.
- The recursive learning loop connects audit, capability profile, gap analysis, bounded Hydra Lab scenario, UDL transformation, content, training, outcome/AAR, corrective action, reassessment and verified improvement.
- Content remains draft until human curriculum approval; physical/defensive-tactics content requires qualified instructor/safety review.
- The canonical data spine links organization/site/people/credentials to assessment, findings, training, scenario, AAR and reassessment.
- G0–G7 stage gates are defined.

**Verified G5A fixture boundary**
- Deterministic local synthetic evidence-chain fixture.
- Includes linked draft records for assessment, finding, gap, prescription, bounded scenario, UDL variants, booklet, lesson plan, Draken narration draft, OS module, exercise, simulated outcome/AAR, corrective action and reassessment.
- Editing content invalidates approval/publication hashes.
- The demo starts unapproved.
- The fixture explicitly does not implement an AI generator, LMS, server authentication, persistence, security-grade approval storage, video production or a real participant trial.
- Trusted in-process actor objects need verified server identities before deployment.
- No G0–G7 gate is declared passed by the fixture tests.
- GitHub Actions workflow runs Node tests, demo and review export drift check. This inventory inspected the workflow and tests; it did not execute them in this session.

**Separate game boundary**
The README explicitly keeps the game prototype separate from Guardian OS and says future Operations Deck integration should consume committed match events without changing game rules. Game ranks must not be conflated with Academy Nine-Gate/Tri-Axis progression or TriCell capability assignment.

**Integration recommendation**
Guardian is the clearest existing source of a deterministic, bounded training-evidence workflow. Treat its G5A fixture as a candidate adapter reference, not as production-ready shared infrastructure. Keep Guardian credential rails, youth/privacy safeguards and curriculum approval local to Guardian.

### 3. `eb142031-max/Shadow-eye-Argus-` — ARGUS / Shadow Eye

**Verified source files**
- `README.md`

**Verified content**
- README title: Shadow-eye-Argus-
- Description: “Investigation software”.

**Unknown / unverified**
- No implementation modules, APIs, data model, tests, evidence chain, authorization workflow or adapter contract were verified through the accessible code search and fetched README.
- The connected Supabase project named `shadow-eye-argus` is inactive; schema and migrations could not be inspected.

**Integration recommendation**
Do not assume Shadowhand's planned case/evidence types are identical to ARGUS's eventual model. Define a mapping contract only after ARGUS source code, schema and authorization model are inspected. The first NITE pilot remains synthetic or explicitly authorized and must not use live subject data by default.

### 4. `eb142031-max/nexus-os2` — Trinity Nexus planning host

**Verified source files**
- `README.md`
- NITE plan and doctrine registry on branch `docs/nexus-token-economy-plan`

**Verified content**
- README describes “Nexus OS 2 - Multi-tool Python operating system with Omega Hydra orchestration”.
- No runtime integration, provider router, NITE ledger, TriCell enforcement or multi-system adapter was verified in the README-level inspection.
- The branch currently carries planning artifacts only.

**Integration recommendation**
Continue using this repository as the architecture/planning host for now. Do not designate it as the canonical production runtime until code, deployment, ownership and test evidence are inspected.

### 5. `eb142031-max/super-funicular` — Codespaces starter

**Verified source**
- README identifies a blank Codespaces Next.js starter and instructs the user to run `npm run dev`.

**Integration recommendation**
Do not treat this repository as an established Shadow, Hydra Lite or Nexus runtime without further source evidence. It is not a canonical dependency for M0.

## Cross-system contracts and candidate reuse

| Capability | Existing evidence | Safe reuse position |
|---|---|---|
| Organization/case/evidence domain types | Shadowhand `packages/types/core.ts` | Candidate source contract; version-pin and review |
| Human review and organization isolation principles | Shadowhand charter | Adopt as policy baseline; runtime enforcement not verified |
| Specialist persona routing concepts | Shadowhand core types and architecture | Candidate domain adapter; no live Aegir runtime verified |
| TriCell human role model | Guardian architecture | Keep Guardian role/credential semantics distinct |
| Deterministic linked evidence workflow | Guardian G5A synthetic fixture | Candidate pattern for tests and provenance |
| Audit chain / evidence custody for ARGUS | Not verified in accessible ARGUS repo | Do not claim implementation |
| Shared NITE budget/model routing | Not verified in any inspected runtime | New subsystem required after canonical runtime decision |
| Protected founding doctrine registry | NITE planning branch | Registry is documentation only; source ingestion pending |

## M0 gaps and blockers

1. **Canonical runtime not selected.** `nexus-os2` is a planning host, Shadowhand is a planned product architecture, Guardian has a bounded fixture, and ARGUS source is minimal.
2. **ARGUS schema unavailable.** Supabase project is inactive; no schema/migration evidence.
3. **Full repository tree unavailable from current inspection path.** This report is based on fetched files and indexed search results, not exhaustive tree enumeration.
4. **Shadow product inventory incomplete.** Shadowstrike, Shadow Academy, Shadowhawk Recon, Lantern Veil and Shadow Arena repository ownership and code locations are not confirmed by this inventory.
5. **Founding source manuals not ingested.** Shadow Tiger, Golden Lotus and Void Moon remain named protected lineages; no doctrine source asset is marked verified.
6. **No cross-system tests exist in the inspected material.** Existing Guardian tests are local synthetic fixture tests, not federation contract tests.

## Recommended next sequence

### M0 closeout
- Obtain an exhaustive repository/file inventory for each private repo.
- Confirm repository ownership and canonical runtime for ARGUS, Shadowhand, Guardian/Shadowstrike, Trinity Nexus and Hydra Lite.
- Restore ARGUS Supabase only with explicit operational approval; inspect schema/migrations/RLS after access is restored.
- Locate Shadowstrike/Shadow Academy/Shadowhawk Recon/Lantern Veil/Shadow Arena source repositories or confirm they are planned modules.

### M1 contract design
- Define provider-neutral federation task envelope and adapter manifest.
- Reuse or map Shadowhand domain types rather than duplicate them.
- Define a Guardian-specific capability/credential adapter that keeps martial and functional rails separate.
- Define ARGUS evidence/provenance mapping only after source verification.
- Add doctrine asset and scoped integration-grant contracts; no consumer enabled by default.

### M2 deterministic proof
- Build a small local contract-validation package and synthetic fixtures.
- Verify authorization, scope, budget caps, provenance, idempotency, audit and rollback behavior before provider/model calls.
- Keep all production DB and deployment actions gated.

## Evidence status

- Repository names and default branches: observed through connected GitHub repository listing.
- Shadowhand charter, architecture, core types and README: fetched and inspected.
- Guardian architecture, G5A boundary, README, test source and CI workflow: fetched and inspected.
- ARGUS README and Nexus README: fetched and inspected.
- `super-funicular` README: fetched and inspected.
- Supabase ARGUS project inactive state: previously verified; schema inaccessible.
- Full repository trees, deployment health, production runtime behavior and all Shadow division source repositories: not established.
