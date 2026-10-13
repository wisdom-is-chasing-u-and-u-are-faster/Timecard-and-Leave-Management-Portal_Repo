import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import audit, auth, leave, punches, supervisor, timecards
from app.db.init_db import init_database

app = FastAPI(
    title="Enterprise Timecard & Leave Management Portal API",
    version="1.0.0",
    description="High-performance backend API powering the Enterprise Timecard & Leave Management PWA."
)

# Explicit allowed origins
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000")
origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initializes schema and seed data on server startup."""
    init_database()


# Health probe
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


# Mount API routers under /api/v1
api_v1_routers = [
    auth.router,
    punches.router,
    timecards.router,
    leave.router,
    supervisor.router,
    audit.router
]

for r in api_v1_routers:
    app.include_router(r, prefix="/api/v1")
    app.include_router(r, prefix="/api")

# Static files mounting for frontend PWA
base_dir = Path(__file__).resolve().parent.parent
public_dir = base_dir / "public"
pages_dir = public_dir / "pages"

if public_dir.exists():
    if pages_dir.exists():
        app.mount("/pages", StaticFiles(directory=str(pages_dir), html=True), name="pages")
    app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="public")
