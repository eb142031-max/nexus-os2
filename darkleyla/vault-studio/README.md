# Dark Leyla OS — Vault Studio

A standalone, dependency-free development UI prototype for the Dark Leyla creative workspace.

## Integrated registry capabilities

- Persona Forge registry with browser-local profile creation, search, status filters, skill/tag metadata, and revision history.
- Local catalog review states and a catalog-only seal workflow. These states are not identity, rights, consent, production, or publication approvals.
- Asset Vault metadata records linked to persona profiles, with asset type, revision, source URL, and catalog classification.
- Browser-local activity ledger for profile, review, asset, and backup actions.
- JSON backup export and import, plus a local demo reset control.
- Persistent browser-local storage with an explicit demo-data disclosure.

## Preview scope

- Command Deck, Persona Forge, Storyboards, NEO-AI Scene Lab, Render Queue, Asset Vault, Activity Ledger, and Hall 5 Review.
- Responsive layout and local-only UI interactions.
- Procedural CSS display object with orbit rotation and lighting preset controls.

## Explicit limitations

This remains a front-end prototype. Registry records are stored in the current browser only. There is no real authentication, shared database, server-side authorization, durable server audit ledger, encrypted asset storage, file upload, model-provider connection, image/video generation, or publishing integration. Local activity history and catalog sealing are not tamper-resistant and do not grant privileged approvals. Sample project/queue telemetry remains illustrative.

The existing Python HALL 5 module is a fail-closed reference gate only. Its Boolean age/rights/consent inputs are not evidence of real identity, age, ownership, rights, or consent.

## Local preview

Open `index.html` directly in a modern browser. No package installation or external CDN is required.

## Next integration gates

1. Private authenticated application shell and verified session identity.
2. Server-side Imperium / Hall 5 policy checks; no client-supplied privilege flags.
3. Separate Supabase schema with per-project ownership, strict RLS, private object storage, and append-only server audit.
4. Server-issued approval records bound to exact asset hashes and persona revisions; invalidate approvals on modification.
5. Persona Forge and Skill Forge role/permission registry, TriCell review, and Nine-Department workflow contracts.
6. Nexus Engine provider adapters with explicit budget controls and human approval.
7. Access-restricted Vercel preview plus browser, security, and accessibility tests.

**Status:** Integrated local registry prototype on the Dark Leyla development branch. Not production-ready; no privileged approvals or external execution are enabled.
