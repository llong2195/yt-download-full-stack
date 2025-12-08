"""FastAPI application entry point."""

import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import time
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.models import Base, engine
from src.routers import channels, downloads, history, queue
from src.tasks.huey_instance import huey
from src.utils import ffmpeg_installer
from src.utils.config import settings
from src.utils.error_handlers import (
    DiskSpaceException,
    DownloadException,
    NotFoundException,
    ValidationException,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Ensure directories exist
settings.ensure_directories()
installer = ffmpeg_installer.FFmpegInstaller()
if installer.is_installed():
    # Add to PATH
    installer.add_to_path()
    print("✓ FFmpeg ready")
else:
    print("⚠ FFmpeg not found - will prompt for installation")
    installer.download_and_install()


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


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests with timing information."""
    start_time = time.time()

    # Process request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {process_time:.3f}s"
        )

        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"{request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Duration: {process_time:.3f}s"
        )
        raise


# Global exception handlers
@app.exception_handler(DownloadException)
async def download_exception_handler(request: Request, exc: DownloadException):
    """Handle download-related exceptions."""
    logger.error(f"Download error: {exc.technical_details}")
    return JSONResponse(
        status_code=400,
        content={
            "error_code": exc.error_code,
            "user_message": exc.message,
            "technical_details": exc.technical_details,
        },
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle validation exceptions."""
    logger.warning(f"Validation error: {exc.message} (field: {exc.field})")
    return JSONResponse(
        status_code=400,
        content={
            "error_code": exc.error_code,
            "user_message": exc.message,
            "field": exc.field,
        },
    )


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """Handle not found exceptions."""
    logger.warning(f"Resource not found: {exc.resource_type} - {exc.resource_id}")
    return JSONResponse(
        status_code=404,
        content={
            "error_code": exc.error_code,
            "user_message": exc.message,
            "resource_type": exc.resource_type,
            "resource_id": exc.resource_id,
        },
    )


@app.exception_handler(DiskSpaceException)
async def disk_space_exception_handler(request: Request, exc: DiskSpaceException):
    """Handle disk space exceptions."""
    logger.error(f"Disk space error: {exc.technical_details}")
    return JSONResponse(
        status_code=507,  # Insufficient Storage
        content={
            "error_code": exc.error_code,
            "user_message": exc.message,
            "required_space": exc.required_space,
            "available_space": exc.available_space,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "user_message": "An unexpected error occurred. Please try again later.",
            "technical_details": str(exc) if settings.DEBUG else None,
        },
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
app.include_router(history.router, prefix="/api/history", tags=["history"])
