import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = ROOT / "darkleyla" / "vault-studio" / "index.html"
JS = ROOT / "darkleyla" / "vault-studio" / "registry.js"

class VaultRegistryIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        cls.js = JS.read_text(encoding="utf-8")

    def test_persona_registry_and_revision_controls_exist(self):
        for token in ("personaSearch", "personaRegistryList", "revisionList", "personaSkills", "personaTags"):
            self.assertIn(token, self.html)

    def test_asset_registry_and_backup_controls_exist(self):
        for token in ("assetRegistryList", "assetSave", "backupExport", "backupImport"):
            self.assertIn(token, self.html)

    def test_activity_ledger_exists(self):
        self.assertIn('id="view-ledger"', self.html)
        self.assertIn("activityList", self.html)

    def test_local_demo_disclosure_is_explicit(self):
        self.assertIn("LOCAL DEMO DATA", self.html)
        self.assertIn("browser storage only", self.html)
        self.assertIn("not shared", self.html)

    def test_registry_is_local_only_and_never_claims_privileged_authority(self):
        self.assertIn("localStorage", self.js)
        self.assertIn("No privileged approval was created", self.js)
        self.assertIn("does not authenticate users", self.js)
        self.assertIn("does not", self.js)

    def test_seal_requires_confirmed_catalog_state(self):
        self.assertIn('p.status !== "CONFIRMED" || p.archived', self.js)
        self.assertIn("Catalog-only seal", self.js)

if __name__ == "__main__":
    unittest.main()
