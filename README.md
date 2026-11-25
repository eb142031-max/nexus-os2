# META OS Imperium — Triune Master Pilot

A browser-local pilot of the **DIAD Mandala Super System**:

- **Mandala I — Imperium:** governance, Conclave, MIOS, Queen Ant stewardship, Dark Leyla, and continuity/memory services.
- **TriCell Nexus:** Observe → Decide → Act, with independent review and a human authorization gate.
- **Mandala II — Legion:** DHG / Blue Wave Shark, ARGUS / Shadow Eye, Shadowhand, Black Talon, Guardian OS, Hydra Academy / Eagle Strike, Libra Guard, and field operations.

## Run the pilot

Open `index.html` in a modern browser. No build step or paid service is required.

The pilot currently provides:
- Nine-fold department registry and navigation
- Local case and evidence-reference intake
- Task creation and completion workflow
- TriCell decision submission, approval, and hold outcomes
- Role-preview permissions for Owner, Commander, Operator, and Viewer
- Browser-local SHA-256-linked audit events and chain verification
- JSON export of the audit ledger
- Basic operational analytics

## Recursive learning skill: RNPL + REA

The pilot includes the **Recursive Neural Plasticity Network Learning Protocol (RNPL)** paired with the **REA — Proprietary Version Output Engine**.

The governed cycle is Observe → Evaluate → Adapt → Reinforce → Reassess → Release. REA creates structured, versioned learning-output drafts from submitted observations, intended outcomes, and feedback. Outputs preserve the distinction between evidence and hypotheses and require human review before adoption.

This is a workflow and version-output prototype. It does **not** train neural-network weights, modify an underlying AI model, or autonomously change policy. Learning records are stored locally in the browser in this pilot.

## Important security boundary

This is a **functional local prototype**, not a production security system. Data is stored in browser localStorage and can be changed by anyone with access to that browser profile. Role selection is a demonstration control, not server-enforced authorization. The evidence registry stores metadata only; do not enter sensitive case data or upload protected evidence.

Before professional or multi-user use, implement:
1. Server-enforced identity, sessions, MFA, and role/attribute-based access control.
2. Tenant-scoped database policies and row-level security.
3. Server-side append-only audit events, signed/hash-chained with protected keys and independent retention.
4. Evidence object storage with encryption, access logging, integrity verification, retention controls, and legal hold.
5. Human approval enforcement on the server for privileged or consequential actions.
6. Backups, recovery tests, monitoring, incident response, and independent security review.

## Architecture rule

The two mandalas remain distinct domains. The TriCell is their shared constitutional decision protocol; it is not a bypass authority. Independent modules retain their own product identity and records while integrating through shared contracts for identity, permissions, workflows, evidence, audit, reporting, and human approval.

## Current branch

`feat/triune-mandala-master-os-pilot`
