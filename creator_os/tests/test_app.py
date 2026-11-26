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

if __name__ == "__main__":
    unittest.main()
