from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    _THIS_DIR = Path(__file__).resolve().parent
    _BACKEND_DIR = _THIS_DIR.parent.parent
    _REPO_ROOT = _BACKEND_DIR.parent
    model_config = SettingsConfigDict(
        env_file=(
            str(_BACKEND_DIR / ".env"),
            str(_REPO_ROOT / ".env"),
            ".env",
        ),
        extra="ignore",
    )

    app_name: str = "Digilians External Exit Petition System"
    app_env: str = "development"
    secret_key: str = "change_me"

    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str
    supabase_attachments_bucket: str = "attachments"
    supabase_generated_bucket: str = "generated"

    docx_template_path: str = "docs/external.docx"

    max_file_size_mb: int = 10
    max_files_count: int = 5
    allowed_file_types: str = "pdf,jpg,jpeg,png"

    timezone: str = "Africa/Cairo"
    pdf_required: bool = False


settings = Settings()

