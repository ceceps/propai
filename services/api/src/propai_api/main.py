"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from propai_api.routers import auth, properties
from propai_core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="PropAI API",
    version="0.1.0",
    summary="AI-assisted property marketing for Prolov",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.public_base_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(properties.router)


@app.get("/health", tags=["ops"])
def health() -> dict[str, object]:
    """Liveness plus the provider posture, so a misconfigured deploy is visible."""
    return {
        "status": "ok",
        "provider_mode": settings.provider_mode.value,
        "model": settings.llm_model,
    }
