import os, base64, unittest
os.environ.setdefault("DARKLEYLA_BOOTSTRAP_TOKEN", "test-bootstrap-token")
os.environ.setdefault("DARKLEYLA_MASTER_KEY", base64.urlsafe_b64encode(b"x" * 32).decode())
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_darkleyla_creator.db")
from fastapi.testclient import TestClient
from app import app

class CreatorOsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        response = cls.client.post("/api/v1/admin/api-keys",
            headers={"Authorization": "Bearer test-bootstrap-token"}, json={"name": "test-suite"})
        cls.api_key = response.json()["api_key"]
        cls.headers = {"X-DarkLeyla-Key": cls.api_key}

    def test_health(self):
        self.assertEqual(self.client.get("/health").status_code, 200)

    def test_bootstrap_denied_without_token(self):
        response = self.client.post("/api/v1/admin/api-keys", json={"name": "bad"})
        self.assertEqual(response.status_code, 403)

    def test_api_key_auth(self):
        self.assertTrue(self.client.get("/api/v1/me", headers=self.headers).json()["authenticated"])
        self.assertEqual(self.client.get("/api/v1/me").status_code, 401)

    def test_create_avatar_and_job_draft(self):
        avatar = self.client.post("/api/v1/avatars", headers=self.headers, json={
            "name": "Test Fictional Adult", "kind": "fictional", "description": "Synthetic adult character",
            "adult_attested": True, "rights_attested": True, "likeness_authorized": False
        })
        self.assertEqual(avatar.status_code, 200)
        job = self.client.post("/api/v1/jobs", headers=self.headers, json={
            "avatar_id": avatar.json()["id"], "prompt": "Adult fashion editorial portrait",
            "mode": "zit-realistic", "aspect_ratio": "9:16"
        })
        self.assertEqual(job.status_code, 200)
        self.assertFalse(job.json()["paid_provider_call_made"])

    def test_self_likeness_requires_authorization(self):
        response = self.client.post("/api/v1/avatars", headers=self.headers, json={
            "name": "Owner", "kind": "self_likeness", "adult_attested": True,
            "rights_attested": True, "likeness_authorized": False
        })
        self.assertEqual(response.status_code, 422)

    def test_unattested_avatar_denied(self):
        response = self.client.post("/api/v1/avatars", headers=self.headers, json={
            "name": "Invalid", "kind": "fictional", "adult_attested": False,
            "rights_attested": True, "likeness_authorized": False
        })
        self.assertEqual(response.status_code, 422)

    def test_celebmaker_key_is_saved_without_returning_secret(self):
        response = self.client.put("/api/v1/integrations/celebmaker", headers=self.headers,
            json={"api_key": "cmk_test_" + "a" * 32})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["secret_returned"])
        self.assertNotIn("api_key", response.json())
        providers = self.client.get("/api/v1/integrations", headers=self.headers).json()
        self.assertTrue(next(p for p in providers if p["provider"] == "celebmaker")["configured"])

    def test_invalid_celebmaker_key_rejected(self):
        response = self.client.put("/api/v1/integrations/celebmaker", headers=self.headers,
            json={"api_key": "not-a-provider-key"})
        self.assertEqual(response.status_code, 422)

    def test_fanvue_oauth_start_builds_pkce_url(self):
        os.environ["FANVUE_CLIENT_ID"] = "test-client"
        os.environ["FANVUE_CLIENT_SECRET"] = "test-secret"
        os.environ["FANVUE_REDIRECT_URI"] = "https://creator.example.test/oauth/fanvue/callback"
        response = self.client.post("/api/v1/integrations/fanvue/start", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["publishing_mode"], "manual_only")
        self.assertIn("code_challenge_method=S256", data["authorization_url"])
        self.assertIn("offline_access", data["scopes"])

    def test_automation_rule_can_be_created_paused_and_resumed(self):
        avatar = self.client.post("/api/v1/avatars", headers=self.headers, json={
            "name": "Automation Character", "kind": "fictional", "adult_attested": True,
            "rights_attested": True, "likeness_authorized": False
        }).json()
        rule = self.client.post("/api/v1/automations", headers=self.headers, json={
            "avatar_id": avatar["id"], "name": "Daily draft", "prompt_template": "Adult editorial draft prompt",
            "mode": "zit-realistic", "aspect_ratio": "9:16", "interval_minutes": 1440
        })
        self.assertEqual(rule.status_code, 200)
        rule_id = rule.json()["id"]
        paused = self.client.post("/api/v1/automations/" + rule_id + "/pause", headers=self.headers)
        self.assertFalse(paused.json()["enabled"])
        resumed = self.client.post("/api/v1/automations/" + rule_id + "/resume", headers=self.headers)
        self.assertTrue(resumed.json()["enabled"])

    def test_private_media_upload_download_and_delete(self):
        import tempfile
        from pathlib import Path
        import media_vault
        old_dir = media_vault.MEDIA_DIR
        with tempfile.TemporaryDirectory() as temp_dir:
            media_vault.MEDIA_DIR = Path(temp_dir)
            avatar = self.client.post("/api/v1/avatars", headers=self.headers, json={
                "name": "Private Media Adult", "kind": "fictional", "adult_attested": True,
                "rights_attested": True, "likeness_authorized": False
            }).json()
            uploaded = self.client.post(
                "/api/v1/media", params={"avatar_id": avatar["id"]},
                headers={**self.headers, "X-File-Name": "portrait.png", "X-Media-Type": "image/png"},
                content=b"\x89PNG\r\n\x1a\nprivate-test-image-bytes"
            )
            self.assertEqual(uploaded.status_code, 200)
            data = uploaded.json()
            self.assertTrue(data["encrypted_at_rest"])
            self.assertIsNone(data["public_url"])
            stored = next(Path(temp_dir).glob("*.enc")).read_bytes()
            self.assertNotIn(b"private-test-image-bytes", stored)
            export = self.client.post("/api/v1/exports", headers=self.headers, json={
                "avatar_id": avatar["id"], "media_id": data["id"],
                "ai_disclosure": True, "human_reviewed": True
            })
            self.assertEqual(export.status_code, 200)
            self.assertEqual(export.json()["state"], "ready_for_manual_upload")
            downloaded = self.client.get("/api/v1/media/" + data["id"], headers=self.headers)
            self.assertEqual(downloaded.content, b"\x89PNG\r\n\x1a\nprivate-test-image-bytes")
            deleted = self.client.delete("/api/v1/media/" + data["id"], headers=self.headers)
            self.assertTrue(deleted.json()["deleted"])
            self.assertEqual(self.client.get("/api/v1/media/" + data["id"], headers=self.headers).status_code, 404)
            media_vault.MEDIA_DIR = old_dir

    def test_private_media_rejects_unsupported_type(self):
        avatar = self.client.post("/api/v1/avatars", headers=self.headers, json={
            "name": "Media Type Test", "kind": "fictional", "adult_attested": True,
            "rights_attested": True, "likeness_authorized": False
        }).json()
        response = self.client.post(
            "/api/v1/media", params={"avatar_id": avatar["id"]},
            headers={**self.headers, "X-File-Name": "script.svg", "X-Media-Type": "image/svg+xml"},
            content=b"<svg/>"
        )
        self.assertEqual(response.status_code, 415)

    def test_paid_generation_is_locked(self):
        response = self.client.post("/api/v1/jobs/example/execute", headers=self.headers)
        self.assertEqual(response.status_code, 423)

    def test_manual_export_requires_ai_disclosure(self):
        avatar = self.client.post("/api/v1/avatars", headers=self.headers, json={
            "name": "Export Character", "kind": "fictional", "adult_attested": True,
            "rights_attested": True, "likeness_authorized": False
        }).json()
        response = self.client.post("/api/v1/exports", headers=self.headers, json={
            "avatar_id": avatar["id"], "asset_url": "https://example.invalid/asset.png",
            "ai_disclosure": False, "human_reviewed": True
        })
        self.assertEqual(response.status_code, 422)

    def test_dollhouse_navigation_targets_real_sections_and_actions(self):
        import re
        from pathlib import Path
        html = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
        ids = set(re.findall('id="([^"]+)"', html))
        targets = re.findall(r'href="#([^"]+)"', html)
        self.assertGreaterEqual(len(re.findall(r'class="room"', html)), 9)
        self.assertTrue(targets, "Navigation should expose section links")
        self.assertEqual([], [target for target in targets if target not in ids],
                         "Every tab and dollhouse room must target an existing section")
        handlers = set(re.findall('onclick="([A-Za-z_$][A-Za-z0-9_$]*)', html))
        functions = set(re.findall('function ([A-Za-z_$][A-Za-z0-9_$]*)', html))
        self.assertEqual([], sorted(handlers - functions),
                         "Every inline action button must call a defined JavaScript process")

if __name__ == "__main__":
    unittest.main()
