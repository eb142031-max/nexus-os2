import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

APP_DIR = Path(__file__).resolve().parents[1]


class CreatorOsBrowserSmoke(unittest.TestCase):
    def test_real_dashboard_workflows(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env.update({
                "DARKLEYLA_BOOTSTRAP_TOKEN": "browser-test-bootstrap",
                "DARKLEYLA_MASTER_KEY": "eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHg=",
                "DATABASE_URL": f"sqlite:///{Path(tmp) / 'browser.db'}",
                "DARKLEYLA_MEDIA_DIR": str(Path(tmp) / "private_media"),
            })
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            base_url = f"http://127.0.0.1:{port}"
            server = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(port)],
                cwd=APP_DIR, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            try:
                for _ in range(80):
                    if server.poll() is not None:
                        self.fail("Creator OS server exited before becoming healthy")
                    try:
                        with urlopen(base_url + "/health", timeout=1) as response:
                            if response.status == 200:
                                break
                    except Exception:
                        time.sleep(0.25)
                else:
                    self.fail("Creator OS server did not become healthy")

                with sync_playwright() as p:
                    browser = p.chromium.launch()
                    page = browser.new_page()
                    page_errors = []
                    page.on("pageerror", lambda error: page_errors.append(str(error)))
                    page.goto(base_url, wait_until="networkidle")

                    # Every navigation target exists and all IDs are unique.
                    navigation = page.locator("nav a, .dollhouse a").evaluate_all(
                        "(els) => els.map(a => ({href:a.getAttribute('href'), target:document.querySelector(a.getAttribute('href')) !== null}))"
                    )
                    self.assertGreaterEqual(len(navigation), 18)
                    self.assertTrue(all(item["target"] for item in navigation), navigation)
                    duplicate_ids = page.locator("[id]").evaluate_all(
                        "(els) => els.map(e => e.id).filter((id, i, all) => all.indexOf(id) !== i)"
                    )
                    self.assertEqual([], duplicate_ids)

                    # Bootstrap an owner key using the real API and UI.
                    page.locator("#bootstrap").fill("browser-test-bootstrap")
                    page.locator("#keyName").fill("Browser smoke key")
                    page.get_by_role("button", name="Create API key").click()
                    page.get_by_text("Key created and shown once.", exact=False).wait_for()
                    page.locator("#connection").get_by_text("Connected", exact=False).wait_for()

                    # Create an adult fictional avatar.
                    page.locator("#avatarName").fill("Browser Test Fictional Adult")
                    page.locator("#avatarKind").select_option("fictional")
                    page.locator("#avatarDescription").fill("Original synthetic adult editorial persona")
                    page.locator("#adultAttested").check()
                    page.locator("#rightsAttested").check()
                    page.get_by_role("button", name="Create avatar").click()
                    page.locator("#avatars").get_by_text("Browser Test Fictional Adult").wait_for()

                    # Save a generation draft; no provider generation endpoint is called.
                    page.locator("#jobPrompt").fill("Adult fashion editorial concept, fully clothed")
                    page.get_by_role("button", name="Save generation draft").click()
                    page.locator("#jobs").get_by_text("draft_pending_manual_execution").wait_for()

                    # Create a scheduled draft-only rule.
                    page.locator("#automationName").fill("Browser scheduled draft")
                    page.locator("#automationPrompt").fill("A new adult editorial draft concept")
                    page.get_by_role("button", name="Create scheduled draft rule").click()
                    page.locator("#automations").get_by_text("Browser scheduled draft").wait_for()

                    # Encrypt a media upload, then prepare a reviewed manual export.
                    page.locator("#mediaFile").set_input_files({
                        "name": "browser-test.png",
                        "mimeType": "image/png",
                        "buffer": b"\x89PNG\r\n\x1a\nprivate-browser-test",
                    })
                    page.get_by_role("button", name="Encrypt and store privately").click()
                    page.locator("#media").get_by_text("browser-test.png").wait_for()
                    page.locator("#exportMedia").select_option(index=1)
                    page.locator("#aiDisclosure").check()
                    page.locator("#humanReviewed").check()
                    page.get_by_role("button", name="Prepare export").click()
                    page.locator("#exportsList").get_by_text("ready_for_manual_upload").wait_for()

                    self.assertEqual([], page_errors, page_errors)
                    browser.close()
            finally:
                server.terminate()
                try:
                    server.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
