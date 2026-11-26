"""Encrypted, authenticated private media vault for Dark Leyla Creator OS.

Files are encrypted before being written to the configured persistent volume.
There is no public/static route for stored media; every read requires an API key.
"""
from __future__ import annotations

import hashlib
import os
import secrets
from pathlib import Path
from urllib.parse import quote, unquote

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app import ApiKey, Avatar, Base, audit, db_session, get_api_key, master_key, utcnow, engine

router = APIRouter(prefix="/api/v1/media", tags=["private-media"])
MEDIA_DIR = Path(os.getenv("DARKLEYLA_MEDIA_DIR", "./private_media")).resolve()
MAX_MEDIA_BYTES = 100 * 1024 * 1024
ALLOWED_MEDIA_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "video/mp4", "video/webm",
}


class MediaAsset(Base):
    __tablename__ = "media_assets"
    id = Column(String, primary_key=True)
    avatar_id = Column(String, ForeignKey("avatars.id"), nullable=False, index=True)
    owner_key_id = Column(String, ForeignKey("api_keys.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    media_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256 = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


MediaAsset.__table__.create(bind=engine, checkfirst=True)


def _asset_path(asset_id: str) -> Path:
    # IDs are generated server-side; never accept a client-provided path.
    return MEDIA_DIR / (asset_id + ".enc")


def _matches_media_type(raw: bytes, media_type: str) -> bool:
    signatures = {
        "image/jpeg": raw.startswith(b"\xff\xd8\xff"),
        "image/png": raw.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP",
        "image/gif": raw.startswith((b"GIF87a", b"GIF89a")),
        "video/mp4": len(raw) >= 8 and raw[4:8] == b"ftyp",
        "video/webm": raw.startswith(b"\x1a\x45\xdf\xa3"),
    }
    return signatures.get(media_type, False)


@router.post("")
async def upload_private_media(
    request: Request,
    avatar_id: str,
    x_file_name: str = Header(default="upload.bin", alias="X-File-Name"),
    x_media_type: str = Header(default="application/octet-stream", alias="X-Media-Type"),
    db: Session = Depends(db_session),
    key: ApiKey = Depends(get_api_key),
):
    avatar = db.query(Avatar).filter_by(id=avatar_id).first()
    if not avatar:
        raise HTTPException(404, "Avatar not found.")
    if x_media_type.lower() not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(415, "Unsupported media type. Upload JPEG, PNG, WebP, GIF, MP4 or WebM.")
    declared_length = request.headers.get("content-length")
    if declared_length and declared_length.isdigit() and int(declared_length) > MAX_MEDIA_BYTES:
        raise HTTPException(413, "Media exceeds the 100 MB upload limit.")
    chunks = []
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > MAX_MEDIA_BYTES:
            raise HTTPException(413, "Media exceeds the 100 MB upload limit.")
        chunks.append(chunk)
    raw = b"".join(chunks)
    if not raw:
        raise HTTPException(400, "Empty media upload.")
    if not _matches_media_type(raw, x_media_type.lower()):
        raise HTTPException(415, "File signature does not match the declared media type.")
    name = Path(unquote(x_file_name).replace(chr(92), "/")).name.strip()
    if not name or len(name) > 255 or any(ord(ch) < 32 for ch in name):
        raise HTTPException(422, "Invalid file name.")
    asset_id = secrets.token_urlsafe(24)
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(master_key()).encrypt(nonce, raw, asset_id.encode("utf-8"))
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    destination = _asset_path(asset_id)
    temporary = MEDIA_DIR / (asset_id + ".tmp")
    try:
        temporary.write_bytes(nonce + ciphertext)
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    row = MediaAsset(
        id=asset_id, avatar_id=avatar.id, owner_key_id=key.id,
        file_name=name, media_type=x_media_type.lower(), size_bytes=len(raw),
        sha256=hashlib.sha256(raw).hexdigest(), created_at=utcnow(),
    )
    db.add(row)
    try:
        db.commit()
    except Exception:
        db.rollback()
        if destination.exists():
            destination.unlink()
        raise
    audit(db, key.id, "media.uploaded", "media_asset", asset_id,
          {"avatar_id": avatar.id, "size_bytes": len(raw), "media_type": row.media_type})
    return {
        "id": row.id, "avatar_id": row.avatar_id, "file_name": row.file_name,
        "media_type": row.media_type, "size_bytes": row.size_bytes,
        "sha256": row.sha256, "encrypted_at_rest": True, "public_url": None,
    }


@router.get("")
def list_private_media(db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    rows = db.query(MediaAsset).order_by(MediaAsset.created_at.desc()).limit(200).all()
    return [{
        "id": r.id, "avatar_id": r.avatar_id, "file_name": r.file_name,
        "media_type": r.media_type, "size_bytes": r.size_bytes,
        "sha256": r.sha256, "created_at": r.created_at.isoformat(),
    } for r in rows]


@router.get("/{asset_id}")
def download_private_media(asset_id: str, db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    row = db.query(MediaAsset).filter_by(id=asset_id).first()
    if not row:
        raise HTTPException(404, "Media asset not found.")
    path = _asset_path(row.id)
    if not path.is_file():
        raise HTTPException(410, "Encrypted media file is missing from the configured storage volume.")
    stored = path.read_bytes()
    try:
        raw = AESGCM(master_key()).decrypt(stored[:12], stored[12:], row.id.encode("utf-8"))
    except Exception as exc:
        raise HTTPException(500, "Media integrity or encryption-key verification failed.") from exc
    if hashlib.sha256(raw).hexdigest() != row.sha256:
        raise HTTPException(500, "Media integrity check failed.")
    safe_name = row.file_name.replace('"', "").encode("ascii", "ignore").decode("ascii") or "private-media"
    encoded_name = quote(row.file_name, safe="")
    return Response(content=raw, media_type=row.media_type, headers={
        "Content-Disposition": f'attachment; filename="{safe_name}"; filename*=UTF-8\'\'{encoded_name}',
        "Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff",
    })


@router.delete("/{asset_id}")
def delete_private_media(asset_id: str, db: Session = Depends(db_session), key: ApiKey = Depends(get_api_key)):
    row = db.query(MediaAsset).filter_by(id=asset_id).first()
    if not row:
        raise HTTPException(404, "Media asset not found.")
    path = _asset_path(row.id)
    db.delete(row)
    db.commit()
    if path.exists():
        path.unlink()
    audit(db, key.id, "media.deleted", "media_asset", asset_id, {})
    return {"deleted": True, "id": asset_id}
