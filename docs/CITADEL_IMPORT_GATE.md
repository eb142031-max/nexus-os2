# Citadel source integration status

The v0.3 Citadel review ZIP is available as a conversation artifact, but has not been imported to this GitHub branch. Do not label this PR a completed app modernization or deployment.

## Required checks for the source import
- Preserve existing Citadel index.html and README without replacing with a different prototype.
- Strip pycache and pytest cache from release archives.
- Run `pytest -q tests/test_static.py`.
- Run browser tests on an accessible browser host; if local navigation is blocked by administrator policy, document the limitation and separately test the DOM using a mock localStorage.
- Verify mission creation, Hall 5 approve/reject, Warden quarantine, XSS escaping, reload persistence, audit export, and no network requests.
- Run Modern Web Guidance only after verifying its published package and supported commands.
- Keep the independent HYDRA Referee, synthetic-only authority, and Hall 5 review.
- No Supabase or Vercel deployment until authenticated persistence and real server-side authorization pass negative tests.
