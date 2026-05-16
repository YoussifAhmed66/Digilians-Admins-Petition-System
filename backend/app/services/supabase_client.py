from __future__ import annotations

from supabase import Client, create_client

from app.core.config import settings


def supabase_admin() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_role_key)

