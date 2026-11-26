"""FastAPI application entrypoint."""

from fastapi import FastAPI

from authapi.api import api_router

app = FastAPI(
    title="Auth API",
    description=(
        "Reusable authentication service with JWT, refresh tokens, "
        "RBAC, and password recovery"
    ),
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
