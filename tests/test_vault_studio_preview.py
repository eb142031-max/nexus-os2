import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = ROOT / "darkleyla" / "vault-studio" / "index.html"

class VaultStudioPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HTML.read_text(encoding="utf-8")

    def test_core_views_exist(self):
        for view in ("overview", "personas", "storyboard", "scene", "renders", "vault", "review"):
            with self.subTest(view=view):
                self.assertIn(f'id="view-{view}"', self.source)

    def test_preview_discloses_simulation(self):
        self.assertIn("Local demo state only", self.source)
        self.assertIn("No provider, storage, or publishing service is connected", self.source)
        self.assertIn("Client-side checkboxes are planning aids only", self.source)

    def test_execution_and_publication_are_not_enabled(self):
        self.assertIn("Execution", self.source)
        self.assertIn("Publication", self.source)
        self.assertIn("disabled in P0 preview", self.source)

    def test_no_external_script_or_stylesheet_dependencies(self):
        self.assertNotIn("<script src=", self.source)
        self.assertNotIn('<link rel="stylesheet"', self.source)

    def test_mobile_layout_is_present(self):
        self.assertIn("@media(max-width:680px)", self.source)

if __name__ == "__main__":
    unittest.main()
