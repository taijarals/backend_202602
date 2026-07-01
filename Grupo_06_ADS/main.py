"""
FastAPI Main Application.

Educational Gamification Platform - Backend API
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from database import settings
from api import (
    auth_router,
    users_router,
    disciplinas_router,
    turmas_router,
    desafios_router,
    miniprovas_router,
    gamificacao_router,
    equipes_router,
    missoes_router,
    enquetes_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Educational Gamification Platform API

    A comprehensive backend for an educational gamification platform with:

    - **Authentication**: User registration, login, and session management
    - **Users**: Student and professor management
    - **Disciplinas**: Subject/course management
    - **Turmas**: Class/group management with invite codes
    - **Desafios**: Challenge system with submissions and peer voting
    - **Mini Provas**: Quick tests with timer and auto-grading
    - **Gamification**: Points, levels, medals, and leaderboards
    - **Equipes**: Team management with automatic formation
    - **Missoes**: Learning journeys with progression
    - **Enquetes**: Real-time polls and feedback

    Built with FastAPI, Supabase/PostgreSQL, and modern Python practices.
    """,
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(disciplinas_router, prefix=settings.api_prefix)
app.include_router(turmas_router, prefix=settings.api_prefix)
app.include_router(desafios_router, prefix=settings.api_prefix)
app.include_router(miniprovas_router, prefix=settings.api_prefix)
app.include_router(gamificacao_router, prefix=settings.api_prefix)
app.include_router(equipes_router, prefix=settings.api_prefix)
app.include_router(missoes_router, prefix=settings.api_prefix)
app.include_router(enquetes_router, prefix=settings.api_prefix)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": f"{settings.api_prefix}/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
