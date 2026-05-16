from __future__ import annotations

import datetime as dt

from dateutil import parser as date_parser
from fastapi import HTTPException

from app.core.config import settings
from app.core.time_utils import cairo_tz
from app.services.document_service import DocumentService
from app.services.storage_service import StorageService
from app.services.supabase_client import supabase_admin


class PetitionService:
    def __init__(self) -> None:
        self.sb = supabase_admin()
        self.storage = StorageService()
        self.docs = DocumentService()
        self.tz = cairo_tz(settings.timezone)



    async def list_petitions(self) -> list[dict]:
        res = self.sb.table("petitions").select("*").order("created_at", desc=True).execute()
        return res.data

    def _ensure_pdf_for_petition(self, petition: dict) -> dict:
        if petition.get("generated_pdf_url") or not petition.get("generated_docx_url"):
            return petition

        try:
            docx_bytes = self.storage.download_file(
                settings.supabase_generated_bucket,
                petition["generated_docx_url"],
            )
            pdf_bytes = self.docs.convert_to_pdf(docx_bytes)
            pdf_path = self.storage.upload_generated(
                petition["petition_code"],
                "petition.pdf",
                pdf_bytes,
                "application/pdf",
            )
            self.sb.table("petitions").update({"generated_pdf_url": pdf_path}).eq("id", petition["id"]).execute()
            petition["generated_pdf_url"] = pdf_path
        except Exception as e:
            print(f"PDF backfill failed for petition {petition.get('id')}: {e}")

        return petition

    async def get_petition(self, petition_id: str) -> dict:
        res = self.sb.table("petitions").select("*, programs(*), tracks(*), labs(*)").eq("id", petition_id).single().execute()
        petition = res.data
        if not petition:
            raise HTTPException(status_code=404, detail="Ø§Ù„Ø·Ù„Ø¨ ØºÙŠØ± Ù…ÙˆØ¬ÙˆØ¯")
        petition = self._ensure_pdf_for_petition(petition)
# Get signed URLs for attachments
        attachments_res = self.sb.table("petition_attachments").select("*").eq("petition_id", petition_id).execute()
        attachments = attachments_res.data
        for att in attachments:
            att["signed_url"] = self.storage.get_signed_url(settings.supabase_attachments_bucket, att["file_url"])
        
        petition["attachments"] = attachments
        
        # Signed URLs for generated docs
        if petition.get("generated_docx_url"):
            petition["signed_docx_url"] = self.storage.get_signed_url(settings.supabase_generated_bucket, petition["generated_docx_url"])
        if petition.get("generated_pdf_url"):
            petition["signed_pdf_url"] = self.storage.get_signed_url(settings.supabase_generated_bucket, petition["generated_pdf_url"])
            
        # Get history log
        history_res = self.sb.table("petition_history").select("*").eq("petition_id", petition_id).order("created_at", desc=True).execute()
        petition["history"] = history_res.data

        return petition

    async def log_action(self, petition_id: str, action: str, admin_name: str, notes: str | None = None) -> dict:
        self.sb.table("petition_history").insert({
            "petition_id": petition_id,
            "action": action,
            "admin_name": admin_name,
            "admin_notes": notes
        }).execute()
        return {"success": True}

    async def make_decision(self, petition_id: str, status: str, admin_name: str, admin_notes: str | None = None) -> dict:
        if status not in ["approved", "declined"]:
            raise HTTPException(status_code=400, detail="Ù‚Ø±Ø§Ø± ØºÙŠØ± ØµØ§Ù„Ø­")
            
        # 1. Update DB
        update_res = self.sb.table("petitions").update({
            "status": status,
            "admin_notes": admin_notes,
            "decided_by": admin_name,
            "decided_at": dt.datetime.now(self.tz).isoformat()
        }).eq("id", petition_id).execute()

        # 2. Add to history
        self.sb.table("petition_history").insert({
            "petition_id": petition_id,
            "action": status,
            "admin_name": admin_name,
            "admin_notes": admin_notes
        }).execute()
        
        if not update_res.data:
            raise HTTPException(status_code=404, detail="ÙØ´Ù„ ØªØ­Ø¯ÙŠØ« Ø§Ù„Ø·Ù„Ø¨")
            
        # 2. Fetch full data to re-generate document
        petition = await self.get_petition(petition_id)
        
        # 3. Re-generate and overwrite
        try:
            petition_type = petition.get("petition_type", "external")
            exit_dt = date_parser.parse(petition["exit_datetime"]) if petition.get("exit_datetime") else None
            return_dt = date_parser.parse(petition["return_datetime"]) if petition.get("return_datetime") else None
            
            ctx = self.docs.build_context(
                petition_type=petition_type,
                student_name_ar=petition["student_name_ar"],
                military_number=petition["military_number"],
                program_name_ar=petition["programs"]["name_ar"],
                track_name_ar=petition["tracks"]["name"],
                lab_code=petition["labs"]["code"],
                exit_dt=exit_dt,
                return_dt=return_dt,
                reasons=petition.get("reasons", []),
                description=petition["description"],
                submission_date=petition["submitted_date"],
                status=status,
                admin_name=admin_name,
                admin_notes=admin_notes,
            )
            
            docx_bytes = self.docs.render_docx(ctx)
            # Always overwrite DOCX first so decision marks are persisted even
            # if PDF conversion is unavailable on the host.
            self.storage.upload_generated(petition["petition_code"], "petition.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
            try:
                pdf_bytes = self.docs.convert_to_pdf(docx_bytes)
                self.storage.upload_generated(petition["petition_code"], "petition.pdf", pdf_bytes, "application/pdf")
            except Exception as e:
                print(f"PDF regeneration failed for petition {petition_id}: {e}")
            
        except Exception as e:
            # Decision is already saved in DB; document regeneration may fail
            # due to template/office runtime issues.
            print(f"Failed to regenerate document: {e}")
            
        return update_res.data[0]



