# Browser testing in restricted environments

The standalone Citadel app is tested in two complementary ways:

1. Real HTTP Playwright E2E: preferred, verifies actual localhost navigation and browser storage. Managed Chromium may block localhost with ERR_BLOCKED_BY_ADMINISTRATOR. A blocked test is **not** a pass.
2. Embedded DOM smoke test: load the HTML with Playwright `page.set_content` and inject a mock localStorage. This exercises mission creation, escaped input, Hall 5 approval, Warden quarantine and audit rendering, but does **not** prove HTTP serving, durable browser storage or deployment behavior.

Run static and embedded tests locally with `pytest -q tests/test_static.py tests/test_browser_embedded.py`.

Production readiness requires HTTP E2E, negative auth/RLS tests and protected preview validation.
