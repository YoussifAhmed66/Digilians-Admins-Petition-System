from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes.admin import router as admin_router

# ---------------------------------------------------------------------------
# CORS — add your Vercel frontend URL to ALLOWED_ORIGINS env var (comma-sep)
# e.g. ALLOWED_ORIGINS=https://admin-petitions.vercel.app,http://localhost:3000
# ---------------------------------------------------------------------------
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS: list[str] = (
    ["*"] if _raw_origins.strip() == "*" else [o.strip() for o in _raw_origins.split(",") if o.strip()]
)


def create_app() -> FastAPI:
    app = FastAPI(title="Admin Petitions API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Admin routes
    app.include_router(admin_router, prefix="/api")

    # Serve Static Files
    # We go up 3 levels: app/ -> backend/ -> project_root/ -> frontend/
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    frontend_path = os.path.join(base_dir, "frontend")
    
    if os.path.exists(frontend_path):
        app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            # Fallback to index.html for SPA routing
            index_path = os.path.join(frontend_path, "index.html")
            return FileResponse(index_path)

    return app


app = create_app()
