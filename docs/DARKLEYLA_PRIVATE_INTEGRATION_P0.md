# Dark Leyla private integration — P0 (review only)

**Selected targets, verified 2026-11-15**
- GitHub source: `eb142031-max/nexus-os2`, dedicated review branch.
- Supabase: `NexusOS` project ref `zpvwjgjknodsbvacjrex`; no public tables observed. **No migrations executed.**
- Vercel: `meta-os` project `prj_Gv6A4240GJ72hHHUlFoLOll0rFRO`; Next.js, SSO protection enabled. **No deployment or project configuration change.**
- Google Drive: Dark Leyla/Black Vault archive found, but CloudFront HALL 5 HTML source has not been downloaded/verified.
- Base44: zero apps listed. No app created or paid builder usage.
- Gmail: no mailbox access required, no messages read or sent.

## P0 boundaries

This branch contributes only a Python standard-library reference gate for a future HALL 5 mission handoff. The branch is not integrated into the Vercel Next.js app, nor a Supabase runtime. It deliberately has no provider adapter, no image or video rendering, no publishing, no network calls and no credentials.

**Never treat Boolean verification fields as evidence of real identity or consent.** Production implementation needs authenticated, server-side, auditable attestations and project ownership checks.

## Production gate requirements (not yet met)

1. Obtain and inspect actual HALL 5 HTML source; static security audit and interactive browser tests (mobile, keyboard, JSON export and navigation).
2. Create **separate, private** Supabase schema with strict RLS, per-project ownership, encrypted private assets, server-only secret access, and append-only Eyes audit; run policy tests before enabling any endpoint.
3. Implement Next.js server routes and sessions; enforce HYDRA fail-closed validation on server. Browser/client state never grants Hall 5 approval.
4. Add real review evidence and tamper-resistant approval objects bound to exact asset hash and character revision; invalidate on modification.
5. Add an explicit optional provider adapter after verifying API docs and revoking any previously shared credentials. No live paid calls until budget approval.
6. Make preview deployment access-restricted and require browser smoke tests; no production promotion or public domain exposure.

## Run tests

```bash
python -m unittest discover -s tests -p 'test_darkleyla_governance.py' -v
```

**Security posture:** fail-closed reference prototype, not production auth, consent verification, asset encryption, or proof of deployment readiness.
