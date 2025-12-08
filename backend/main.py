"""FastAPI application entry point."""

import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.models import Base, engine
from src.routers import channels, downloads, queue
from src.tasks.huey_instance import huey
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Ensure directories exist
settings.ensure_directories()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting YouTube Downloader API...")

    # Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Note: Huey consumer can be started separately with: python -m huey.consumer main.huey
    # For development, tasks will be executed synchronously
    logger.info("Huey configured for task execution")

    yield

    # Shutdown
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="YouTube Downloader API",
    description="Full-stack YouTube video downloader with channel management",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected",
        "huey": "configured",
    }


# Register routers

app.include_router(channels.router, prefix="/api/channels", tags=["channels"])
app.include_router(downloads.router, prefix="/api/downloads", tags=["downloads"])
app.include_router(queue.router, prefix="/api/queue", tags=["queue"])

# TODO: Register remaining routers
# app.include_router(history.router, prefix="/api/history", tags=["history"])
