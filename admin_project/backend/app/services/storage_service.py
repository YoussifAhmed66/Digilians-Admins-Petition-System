from __future__ import annotations

import re
import time

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.services.supabase_client import supabase_admin


_SAFE_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def _safe_name(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = _SAFE_RE.sub("_", name)
    return name[:180] if name else "file"


class StorageService:
    def __init__(self) -> None:
        self.sb = supabase_admin()

    async def upload_attachments(self, petition_code: str, attachments: list[UploadFile]) -> list[dict]:
        if not attachments:
            return []
        out: list[dict] = []
        bucket = self.sb.storage.from_(settings.supabase_attachments_bucket)
        ts = time.strftime("%Y%m%d%H%M%S")
        max_size = settings.max_file_size_mb * 1024 * 1024
        for file in attachments:
            original_name = (file.filename or "file").strip()
            stored_name = f"{petition_code}_{ts}_{_safe_name(original_name)}"
            path = f"attachments/{petition_code}/{stored_name}"
            content = await file.read()
            if len(content) > max_size:
                raise HTTPException(status_code=400, detail="Ø­Ø¬Ù… Ø§Ù„Ù…Ù„Ù Ø£ÙƒØ¨Ø± Ù…Ù† Ø§Ù„Ù…Ø³Ù…ÙˆØ­")
            try:
                # supabase-py Storage: upload(path, file, file_options)
                bucket.upload(path, content, {"content-type": file.content_type or "application/octet-stream"})
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"ÙØ´Ù„ Ø±ÙØ¹ Ø§Ù„Ù…Ø±ÙÙ‚: {original_name} ({str(e)})",
                ) from e
            out.append(
                {
                    "original_name": original_name,
                    "stored_name": stored_name,
                    "file_url": path,
                    "file_size": len(content),
                    "mime_type": file.content_type,
                }
            )
        return out

    def delete_files(self, bucket_name: str, paths: list[str]) -> None:
        if not paths:
            return
        try:
            self.sb.storage.from_(bucket_name).remove(paths)
        except Exception:
            # Best-effort cleanup to avoid masking original errors.
            pass

    def upload_generated(self, petition_code: str, filename: str, content: bytes, content_type: str) -> str:
        bucket = self.sb.storage.from_(settings.supabase_generated_bucket)
        path = f"generated/{petition_code}/{filename}"
        try:
            # Upsert=True allows re-generating documents upon admin decision
            bucket.upload(path, content, {"content-type": content_type, "upsert": "true"})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ÙØ´Ù„ Ø±ÙØ¹ Ø§Ù„Ù…Ø³ØªÙ†Ø¯Ø§Øª ({str(e)})") from e
        return path

    def download_file(self, bucket_name: str, path: str) -> bytes:
        try:
            return self.sb.storage.from_(bucket_name).download(path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}") from e
    def get_signed_url(self, bucket_name: str, path: str, expires_in: int = 3600) -> str:
        try:
            res = self.sb.storage.from_(bucket_name).create_signed_url(path, expires_in)
            return res.get("signedURL") or res.get("signed_url")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ÙØ´Ù„ Ø¥Ù†Ø´Ø§Ø¡ Ø±Ø§Ø¨Ø· Ø§Ù„Ù…Ù„Ù: {str(e)}") from e


