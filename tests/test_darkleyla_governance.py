import unittest
from dataclasses import replace
from darkleyla.governance import Hall5, Mission, Denied

class GateTest(unittest.TestCase):
    def setUp(self):
        self.g = Hall5(owner_id="owner", project_id="private-vault")
        self.m = Mission(project_id="private-vault", actor_id="owner", idempotency_key="key-1",
            goal="Prepare a wardrobe storyboard", constraints="Keep it private",
            acceptance="Human reviews output", asset_id="owned-asset", character_version=1,
            estimated_credits=0, budget_credits=0,
            age_verified=True, rights_verified=True, consent_verified=True)
    def test_prepare_only(self):
        r=self.g.prepare(self.m,"owner")
        self.assertEqual(r["state"],"proposed_private_review")
        self.assertFalse(r["execution_enabled"])
        self.assertFalse(r["publish_authorized"])
    def test_retry_is_idempotent(self):
        a=self.g.prepare(self.m,"owner")
        b=self.g.prepare(self.m,"owner")
        self.assertEqual(a["id"],b["id"])
        self.assertEqual(len(self.g.handoffs),1)
    def test_payload_collision_fails(self):
        self.g.prepare(self.m,"owner")
        with self.assertRaisesRegex(Denied,"idempotency_payload_mismatch"):
            self.g.prepare(replace(self.m,goal="Changed"),"owner")
    def test_cross_project_denied(self):
        with self.assertRaisesRegex(Denied,"project_or_request_mismatch"):
            self.g.prepare(replace(self.m,project_id="other"),"owner")
    def test_wrong_actor_denied(self):
        with self.assertRaisesRegex(Denied,"unauthorized_actor"):
            self.g.prepare(self.m,"intruder")
    def test_unverified_rights_denied(self):
        with self.assertRaises(Denied):
            self.g.prepare(replace(self.m,rights_verified=False),"owner")
    def test_unverified_adult_denied(self):
        with self.assertRaises(Denied):
            self.g.prepare(replace(self.m,age_verified=False),"owner")
    def test_unverified_consent_denied(self):
        with self.assertRaises(Denied):
            self.g.prepare(replace(self.m,consent_verified=False),"owner")
    def test_budget_denied(self):
        with self.assertRaisesRegex(Denied,"budget_exceeded"):
            self.g.prepare(replace(self.m,estimated_credits=4),"owner")
    def test_invalid_version_denied(self):
        with self.assertRaises(Denied):
            self.g.prepare(replace(self.m,character_version=0),"owner")
    def test_incomplete_spec_denied(self):
        with self.assertRaises(Denied):
            self.g.prepare(replace(self.m,acceptance=""),"owner")
    def test_execute_disabled(self):
        with self.assertRaisesRegex(Denied,"execution_not_implemented"):
            self.g.execute("anything")
    def test_publish_disabled(self):
        with self.assertRaisesRegex(Denied,"publication_human_only"):
            self.g.publish("anything")
    def test_denial_is_audited(self):
        with self.assertRaises(Denied):
            self.g.prepare(self.m,"intruder")
        self.assertEqual(self.g.events[-1]["type"],"hydra.denied")

if __name__ == "__main__":
    unittest.main()
