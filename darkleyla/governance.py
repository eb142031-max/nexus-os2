"""Fail-closed mission handoff for a private, simulated Dark Leyla workspace.

No network access, media generation, database writes, or provider execution.
Rights/age assertions MUST come from a trusted server-side verification system
before this module can be used in a production workflow.
"""
from dataclasses import dataclass, field
import hashlib
import json

class Denied(ValueError):
    pass

@dataclass(frozen=True)
class Mission:
    project_id: str
    actor_id: str
    idempotency_key: str
    goal: str
    constraints: str
    acceptance: str
    asset_id: str
    character_version: int
    estimated_credits: int
    budget_credits: int
    age_verified: bool
    rights_verified: bool
    consent_verified: bool

@dataclass
class Hall5:
    owner_id: str
    project_id: str
    events: list = field(default_factory=list)
    handoffs: dict = field(default_factory=dict)

    def prepare(self, mission: Mission, session_actor_id: str) -> dict:
        self.events.append({"type": "mission.proposed", "project": self.project_id})
        try:
            self._check(mission, session_actor_id)
            payload = {
                "project_id": mission.project_id, "actor_id": mission.actor_id,
                "goal": mission.goal.strip(), "constraints": mission.constraints.strip(),
                "acceptance": mission.acceptance.strip(), "asset_id": mission.asset_id,
                "character_version": mission.character_version,
                "estimated_credits": mission.estimated_credits,
            }
            fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            key = (mission.project_id, mission.idempotency_key)
            if key in self.handoffs:
                existing = self.handoffs[key]
                if existing["fingerprint"] != fingerprint:
                    raise Denied("idempotency_payload_mismatch")
                return dict(existing)
            result = {"id": fingerprint[:20], "fingerprint": fingerprint,
                      "state": "proposed_private_review", "execution_enabled": False,
                      "publish_authorized": False, "credits_spent": 0,
                      "payload": payload}
            self.handoffs[key] = result
            self.events.append({"type": "mission.prepared", "id": result["id"]})
            return dict(result)
        except Denied as exc:
            self.events.append({"type": "hydra.denied", "reason": str(exc)})
            raise

    def _check(self, m: Mission, session_actor_id: str):
        if not self.owner_id or session_actor_id != self.owner_id or m.actor_id != session_actor_id:
            raise Denied("unauthorized_actor")
        if not m.project_id or m.project_id != self.project_id or not m.idempotency_key:
            raise Denied("project_or_request_mismatch")
        if not all((m.goal.strip(), m.constraints.strip(), m.acceptance.strip(), m.asset_id.strip())):
            raise Denied("incomplete_spec")
        if m.character_version < 1:
            raise Denied("unversioned_character")
        if not (m.age_verified and m.rights_verified and m.consent_verified):
            raise Denied("unverified_rights_or_age")
        if m.estimated_credits < 0 or m.budget_credits < m.estimated_credits:
            raise Denied("budget_exceeded")

    def execute(self, *_):
        self.events.append({"type": "hall5.execution_blocked"})
        raise Denied("execution_not_implemented")

    def publish(self, *_):
        self.events.append({"type": "hall5.publication_blocked"})
        raise Denied("publication_human_only")
