from __future__ import annotations

import datetime as dt
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from docxtpl import DocxTemplate, RichText
from fastapi import HTTPException

from app.core.config import settings
from app.core.time_utils import arabic_weekday_name, format_arabic_time


REASON_FAMILY = "حالة عائلية طارئة"
REASON_EXAM = "حضور امتحان خارجي"
REASON_SPECIAL = "ظرف خاص آخر يُرجى التوضيح"
REASON_EMERGENCY = "حالة طارئة"
EXPECTED_TEMPLATE_KEYS = {
    "student_name",
    "military_number",
    "program",
    "track",
    "lab_code",
    "exit_date",
    "exit_day",
    "exit_time",
    "return_date",
    "return_day",
    "return_time",
    "reason_family",
    "reason_exam",
    "reason_special",
    "reason_emergency",
    "description",
    "submission_date",
    "decision_approved",
    "decision_declined",
    "admin_notes",
}


class DocumentService:
    def _resolve_soffice_bin(self) -> str:
        soffice_in_path = shutil.which("soffice")
        if soffice_in_path:
            return soffice_in_path

        candidates = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate

        raise HTTPException(
            status_code=500,
            detail="LibreOffice غير متوفر على السيرفر. ثبّت LibreOffice أو أضف soffice إلى PATH.",
        )
    def _resolve_template_path(self, petition_type: str = "external") -> Path:
        template_name = "internal.docx" if petition_type == "internal" else "external.docx"
        configured = Path("docs") / template_name
        
        # Override with setting if it's the default external and setting is set
        if petition_type == "external" and settings.docx_template_path != "docs/external.docx":
            configured = Path(settings.docx_template_path)
            
        if configured.is_absolute() and configured.exists():
            return configured

        repo_root = Path(__file__).resolve().parents[3]
        repo_candidate = repo_root / configured
        if repo_candidate.exists():
            return repo_candidate

        cwd_candidate = Path.cwd() / configured
        if cwd_candidate.exists():
            return cwd_candidate

        raise HTTPException(status_code=500, detail=f"ملف القالب غير موجود: {configured}")

    def build_context(
        self,
        *,
        petition_type: str,
        student_name_ar: str,
        military_number: str,
        program_name_ar: str,
        track_name_ar: str,
        lab_code: str,
        exit_dt: dt.datetime | None,
        return_dt: dt.datetime | None,
        reasons: list[str] | None,
        description: str | None,
        submission_date: str,
        status: str = "pending",
        admin_name: str | None = None,
        admin_notes: str | None = None,
    ) -> dict:
        reasons = reasons or []
        exit_date = exit_dt.date() if exit_dt else None
        return_date = return_dt.date() if return_dt else None

        def box(reason_label: str) -> str:
            return "☑" if reason_label in reasons else "☐"

        # If description is empty, provide 5 lines of dots for manual writing as per PRD/User request
        if not description:
            line = "." * 130
            display_description = f"{line}\n{line}\n{line}\n{line}\n{line}"
        else:
            display_description = description

        ctx = {
            "petition_type": petition_type,
            "student_name": student_name_ar,
            "military_number": military_number,
            "program": program_name_ar,
            "track": track_name_ar,
            "lab_code": lab_code,
            "exit_date": exit_date.strftime("%Y-%m-%d") if exit_date else "",
            "exit_day": arabic_weekday_name(exit_date) if exit_date else "",
            "exit_time": format_arabic_time(exit_dt.timetz().replace(tzinfo=None)) if exit_dt else "",
            "return_date": return_date.strftime("%Y-%m-%d") if return_date else "",
            "return_day": arabic_weekday_name(return_date) if return_date else "",
            "return_time": format_arabic_time(return_dt.timetz().replace(tzinfo=None)) if return_dt else "",
            "reason_family": box(REASON_FAMILY),
            "reason_exam": box(REASON_EXAM),
            "reason_special": box(REASON_SPECIAL),
            "reason_emergency": box(REASON_EMERGENCY),
            "description": display_description,
            "submission_date": submission_date,
            "admin_name": (admin_name or "").strip(),
            "admin_notes": (admin_notes or "").strip(),
            "decision_approved": "●" if status == "approved" else "○",
            "decision_declined": "●" if status == "declined" else "○",
        }
        return ctx

    def render_docx(self, context: dict) -> bytes:
        try:
            petition_type = context.get("petition_type", "external")
            tpl = DocxTemplate(str(self._resolve_template_path(petition_type)))
            tpl_vars = set(tpl.get_undeclared_template_variables() or set())
            if not (tpl_vars & EXPECTED_TEMPLATE_KEYS):
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "القالب لا يحتوي placeholders متوافقة مع النظام. "
                        "تأكد من وجود متغيرات مثل {{ student_name }} و {{ military_number }}."
                    ),
                )
            tpl.render(context)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp_path = tmp.name
            tpl.save(tmp_path)
            with open(tmp_path, "rb") as f:
                data = f.read()
            os.unlink(tmp_path)
            return data
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"فشل توليد ملف Word ({str(e)})") from e

    def convert_to_pdf(self, docx_bytes: bytes) -> bytes:
        with tempfile.TemporaryDirectory() as d:
            docx_path = os.path.join(d, "petition.docx")
            with open(docx_path, "wb") as f:
                f.write(docx_bytes)

            try:
                soffice_bin = self._resolve_soffice_bin()
                subprocess.run(
                    [
                        soffice_bin,
                        "--headless",
                        "--nologo",
                        "--nolockcheck",
                        "--nodefault",
                        "--nofirststartwizard",
                        "--convert-to",
                        "pdf",
                        "--outdir",
                        d,
                        docx_path,
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"فشل تحويل PDF ({str(e)})") from e

            pdf_path = os.path.join(d, "petition.pdf")
            if not os.path.exists(pdf_path):
                raise HTTPException(status_code=500, detail="فشل تحويل PDF")
            with open(pdf_path, "rb") as f:
                return f.read()

