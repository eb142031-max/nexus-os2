from __future__ import annotations
import base64, hashlib, json, os, secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./darkleyla_creator.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True, default=lambda: secrets.token_urlsafe(12))
    name = Column(String(100), nullable=False)
    key_hash = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)

class Integration(Base):
    __tablename__ = "integrations"
    provider = Column(String(40), primary_key=True)
    encrypted_secret = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

class Avatar(Base):
    __tablename__ = "avatars"
    id = Column(String, primary_key=True, default=lambda: secrets.token_urlsafe(12))
    name = Column(String(120), nullable=False)
    kind = Column(String(24), nullable=False)
    description = Column(Text, default="", nullable=False)
    adult_attested = Column(Boolean, nullable=False)
    rights_attested = Column(Boolean, nullable=False)
    likeness_authorized = Column(Boolean, nullable=False)
    provider_character_id = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

class GenerationJob(Base):
    __tablename__ = "generation_jobs"
    id = Column(String, primary_key=True, default=lambda: secrets.token_urlsafe(12))
    avatar_id = Column(String, ForeignKey("avatars.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    mode = Column(String(80), nullable=False)
    aspect_ratio = Column(String(16), nullable=False)
    state = Column(String(40), default="draft_pending_manual_execution", nullable=False)
    provider_job_id = Column(String(120), nullable=True)
    provider_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

class ExportRecord(Base):
    __tablename__ = "exports"
    id = Column(String, primary_key=True, default=lambda: secrets.token_urlsafe(12))
    avatar_id = Column(String, ForeignKey("avatars.id"), nullable=False)
    job_id = Column(String, ForeignKey("generation_jobs.id"), nullable=True)
    asset_url = Column(Text, nullable=False)
    ai_disclosure = Column(Boolean, default=True, nullable=False)
    human_reviewed = Column(Boolean, default=False, nullable=False)
    state = Column(String(40), default="awaiting_human_review", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_key_id = Column(String, nullable=True)
    event = Column(String(100), nullable=False)
    object_type = Column(String(60), nullable=False)
    object_id = Column(String(120), nullable=True)
    details = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Dark Leyla Creator OS", version="0.1.0", description="Standalone creator workspace API")

def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def audit(db: Session, actor: Optional[str], event: str, object_type: str, object_id: Optional[str], details: dict):
    db.add(AuditEvent(actor_key_id=actor, event=event, object_type=object_type, object_id=object_id, details=json.dumps(details, sort_keys=True)))
    db.commit()

def hash_key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def get_api_key(x_darkleyla_key: str = Header(default=""), db: Session = Depends(db_session)):
    if not x_darkleyla_key:
        raise HTTPException(401, "Missing X-DarkLeyla-Key")
    row = db.query(ApiKey).filter_by(key_hash=hash_key(x_darkleyla_key), revoked=False).first()
    if not row:
        raise HTTPException(401, "Invalid or revoked API key")
    return row

def master_key() -> bytes:
    raw = os.getenv("DARKLEYLA_MASTER_KEY", "")
    if not raw:
        raise HTTPException(503, "Credential vault is not configured. Set DARKLEYLA_MASTER_KEY.")
    try:
        key = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))
    except Exception as exc:
        raise HTTPException(503, "DARKLEYLA_MASTER_KEY must be URL-safe base64.") from exc
    if len(key) != 32:
        raise HTTPException(503, "DARKLEYLA_MASTER_KEY must decode to exactly 32 bytes.")
    return key

def encrypt_secret(secret: str) -> str:
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(master_key()).encrypt(nonce, secret.encode("utf-8"), b"darkleyla-creator-v1")
    return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")

def decrypt_secret(value: str) -> str:
    data = base64.urlsafe_b64decode(value.encode("ascii"))
    return AESGCM(master_key()).decrypt(data[:12], data[12:], b"darkleyla-creator-v1").decode("utf-8")

class KeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
class AvatarCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    kind: str = Field(pattern="^(self_likeness|fictional)$")
    description: str = Field(default="", max_length=4000)
    adult_attested: bool
    rights_attested: bool
    likeness_authorized: bool = False
    provider_character_id: Optional[str] = Field(default=None, max_length=120)
class ProviderSecret(BaseModel):
    api_key: str = Field(min_length=12, max_length=500)
class JobCreate(BaseModel):
    avatar_id: str
    prompt: str = Field(min_length=5, max_length=5000)
    mode: str = Field(default="zit-realistic", min_length=2, max_length=80)
    aspect_ratio: str = Field(default="9:16", pattern="^(1:1|2:3|3:2|3:4|4:3|4:5|5:4|9:16|16:9)$")
class ExportCreate(BaseModel):
    avatar_id: str
    job_id: Optional[str] = None
    asset_url: str = Field(min_length=8, max_length=2000)
    ai_disclosure: bool = True
    human_reviewed: bool = False

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/health")
def health():
    return {"status": "ok", "service": "dark-leyla-creator-os", "version": app.version}

@app.post("/api/v1/admin/api-keys")
def create_api_key(body: KeyCreate, request: Request, db: Session = Depends(db_session)):
    expected = os.getenv("DARKLEYLA_BOOTSTRAP_TOKEN", "")
    supplied = request.headers.get("authorization", "")
    if not expected or not secrets.compare_digest(supplied, f"Bearer {expected}"):
        raise HTTPException(403, "Bootstrap authorization failed")
    raw = "dlk_" + secrets.token_urlsafe(36)
    row = ApiKey(name=body.name, key_hash=hash_key(raw))
    db.add(row)
    db.commit()
    audit(db, row.id, "api_key.created", "api_key", row.id, {"name": body.name})
    return {"id": row.id, "name": row.name, "api_key": raw, "warning": "Shown once. Store it securely."}

@app.get("/api/v1/me")
def me(key: ApiKey = Depends(get_api_key)):
    return {"authenticated": True, "key_name": key.name, "key_id": key.id}

@app.post("/api/v1/avatars")
def create_avatar(body: AvatarCreate, db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    if not body.adult_attested or not body.rights_attested:
        raise HTTPException(422, "Adult status and rights must be affirmatively attested.")
    if body.kind == "self_likeness" and not body.likeness_authorized:
        raise HTTPException(422, "Self-likeness use requires explicit likeness authorization.")
    row = Avatar(name=body.name, kind=body.kind, description=body.description, adult_attested=body.adult_attested,
                 rights_attested=body.rights_attested, likeness_authorized=body.likeness_authorized,
                 provider_character_id=body.provider_character_id)
    db.add(row)
    db.commit()
    audit(db, key.id, "avatar.created", "avatar", row.id, {"kind": row.kind, "name": row.name})
    return {"id": row.id, "name": row.name, "kind": row.kind, "created_at": row.created_at.isoformat()}

@app.get("/api/v1/avatars")
def list_avatars(db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    rows = db.query(Avatar).order_by(Avatar.created_at.desc()).all()
    return [{"id": r.id, "name": r.name, "kind": r.kind, "description": r.description,
             "provider_character_id": r.provider_character_id, "created_at": r.created_at.isoformat()} for r in rows]

@app.put("/api/v1/integrations/celebmaker")
def save_celebmaker(body: ProviderSecret, db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    encrypted = encrypt_secret(body.api_key)
    row = db.query(Integration).filter_by(provider="celebmaker").first()
    if row:
        row.encrypted_secret, row.updated_at = encrypted, utcnow()
    else:
        db.add(Integration(provider="celebmaker", encrypted_secret=encrypted, updated_at=utcnow()))
    db.commit()
    audit(db, key.id, "integration.credential_saved", "integration", "celebmaker", {})
    return {"provider": "celebmaker", "configured": True, "secret_returned": False}

@app.get("/api/v1/integrations")
def integrations(db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    configured = {r.provider for r in db.query(Integration).all()}
    return [
        {"provider": "celebmaker", "configured": "celebmaker" in configured, "capability": "server-side API validation and options discovery; generation gated"},
        {"provider": "fanvue", "configured": False, "capability": "manual export now; OAuth requires registered developer app"},
        {"provider": "ourdream", "configured": False, "capability": "disabled pending official API and commercial rights"},
        {"provider": "joi", "configured": False, "capability": "disabled pending exact service, official API and commercial-use verification"},
    ]

async def celebmaker_request(db: Session, method: str, path: str, payload: Optional[dict] = None):
    row = db.query(Integration).filter_by(provider="celebmaker").first()
    if not row:
        raise HTTPException(409, "CelebMaker API key is not configured.")
    token = decrypt_secret(row.encrypted_secret)
    async with httpx.AsyncClient(timeout=25.0) as client:
        response = await client.request(method, f"https://celebmakerai.com/api/v1{path}",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=payload)
    if response.status_code >= 400:
        raise HTTPException(502, f"CelebMaker API returned {response.status_code}. Check provider access, scopes and credits.")
    return response.json()

@app.get("/api/v1/integrations/celebmaker/check")
async def check_celebmaker(db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    me_data = await celebmaker_request(db, "GET", "/me")
    credits = await celebmaker_request(db, "GET", "/credits")
    options = await celebmaker_request(db, "GET", "/generation-options")
    return {"connected": True, "principal": me_data, "api_available_credits": credits.get("apiAvailableCredits"),
            "image_modes": options.get("imageGeneration", {}).get("modes", []),
            "note": "Connection and options checks do not create a paid generation job."}

@app.post("/api/v1/jobs")
def create_job(body: JobCreate, db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    avatar = db.query(Avatar).filter_by(id=body.avatar_id).first()
    if not avatar:
        raise HTTPException(404, "Avatar not found.")
    if not avatar.adult_attested or not avatar.rights_attested:
        raise HTTPException(403, "Avatar lacks required attestations.")
    row = GenerationJob(avatar_id=avatar.id, prompt=body.prompt, mode=body.mode, aspect_ratio=body.aspect_ratio)
    db.add(row)
    db.commit()
    audit(db, key.id, "generation.draft_created", "generation_job", row.id, {"provider": "celebmaker", "mode": row.mode})
    return {"id": row.id, "state": row.state, "paid_provider_call_made": False,
            "message": "Draft created. Live generation remains disabled pending verified per-mode pricing and explicit spend approval."}

@app.get("/api/v1/jobs")
def list_jobs(db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    rows = db.query(GenerationJob).order_by(GenerationJob.created_at.desc()).limit(100).all()
    return [{"id": r.id, "avatar_id": r.avatar_id, "prompt": r.prompt, "mode": r.mode,
             "aspect_ratio": r.aspect_ratio, "state": r.state, "provider_job_id": r.provider_job_id,
             "created_at": r.created_at.isoformat()} for r in rows]

@app.post("/api/v1/jobs/{job_id}/execute")
def execute_job(job_id: str, db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    raise HTTPException(423, "Paid generation is intentionally locked. Connection checks and draft creation are enabled; live execution requires verified per-mode cost controls and explicit per-job spend approval.")

@app.post("/api/v1/exports")
def create_export(body: ExportCreate, db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    avatar = db.query(Avatar).filter_by(id=body.avatar_id).first()
    if not avatar:
        raise HTTPException(404, "Avatar not found.")
    if body.job_id and not db.query(GenerationJob).filter_by(id=body.job_id, avatar_id=avatar.id).first():
        raise HTTPException(404, "Job not found for this avatar.")
    if not body.ai_disclosure:
        raise HTTPException(422, "AI-generated or materially altered media must retain clear AI disclosure.")
    row = ExportRecord(avatar_id=avatar.id, job_id=body.job_id, asset_url=body.asset_url, ai_disclosure=True,
                       human_reviewed=body.human_reviewed, state="ready_for_manual_upload" if body.human_reviewed else "awaiting_human_review")
    db.add(row)
    db.commit()
    audit(db, key.id, "export.prepared", "export", row.id, {"manual_upload_only": True})
    return {"id": row.id, "state": row.state, "upload_mode": "manual_only", "fanvue_publish_called": False}

@app.get("/api/v1/exports")
def list_exports(db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    rows = db.query(ExportRecord).order_by(ExportRecord.created_at.desc()).limit(100).all()
    return [{"id": r.id, "avatar_id": r.avatar_id, "job_id": r.job_id, "asset_url": r.asset_url,
             "ai_disclosure": r.ai_disclosure, "human_reviewed": r.human_reviewed, "state": r.state,
             "created_at": r.created_at.isoformat()} for r in rows]

@app.get("/api/v1/audit")
def list_audit(db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    rows = db.query(AuditEvent).order_by(AuditEvent.id.desc()).limit(200).all()
    return [{"id": r.id, "event": r.event, "object_type": r.object_type, "object_id": r.object_id,
             "details": json.loads(r.details), "created_at": r.created_at.isoformat()} for r in rows]
