"""Main FastAPI application for video2music."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import requests

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered video analysis for mood-based music recommendations",
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(requests.router)


@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint with basic API information."""
    return JSONResponse(
        content={
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "healthy",
            "description": "AI-powered video analysis for mood-based music recommendations",
        }
    )


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    ) 