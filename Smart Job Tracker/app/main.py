"""
AI Job Tracker API — application entrypoint.

Run with:
    uvicorn app.main:app --reload
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.database import engine, Base
from app.models import User, JobApplication  # noqa: F401 — ensure models registered
from app.routers import auth, applications, dashboard, ai
from app.middleware import (
    RateLimitMiddleware, 
    ErrorHandlingMiddleware,
    SecurityHeadersMiddleware
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("Starting AI Job Tracker API")
    
    # Test database connection
    try:
        with engine.connect() as conn:
            logger.info("✓ Database connection successful")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        raise
    
    # Auto-create tables if they don't exist (critical for first run)
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables verified/created")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Job Tracker API")
    engine.dispose()


app = FastAPI(
    title="AI Job Tracker API",
    description=(
        "A backend API for tracking internship/job applications, managing "
        "status updates, viewing dashboard analytics, and generating "
        "AI-powered next-step suggestions."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Allow the deployed frontend origin plus localhost for local development.
# FRONTEND_URL env var should be set in Render to your frontend's public URL,
# e.g. https://job-tracker-frontend.onrender.com
_frontend_url = os.getenv("FRONTEND_URL", "")
_allowed_origins = [
    "http://localhost:5173",   # Vite dev server
    "http://localhost:4173",   # Vite preview
    "http://127.0.0.1:5173",
]
if _frontend_url:
    _allowed_origins.append(_frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Security & Error Handling Middleware ─────────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(ErrorHandlingMiddleware)


# ── Custom Exception Handlers ───────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors to provide cleaner error messages.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"][1:])  # Skip 'body'
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors from config/settings."""
    logger.error(f"Configuration validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Server configuration error",
            "errors": [f"{err['loc'][0]}: {err['msg']}" for err in exc.errors()]
        }
    )


# ── Include Routers ──────────────────────────────────────────────────────────

# ── Include Routers ──────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(dashboard.router)
app.include_router(ai.router)


@app.get("/", tags=["Health"])
def root():
    """Simple health-check / welcome route."""
    return {
        "message": "AI Job Tracker API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check including database connectivity."""
    from sqlalchemy import text
    from app.config import settings
    
    db_status = "unknown"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        # Don't expose internal error details in production
        if settings.ENVIRONMENT in ["production", "staging"]:
            db_status = "disconnected"
            logger.error(f"Health check - database error: {e}")
        else:
            db_status = f"disconnected: {str(e)[:100]}"
            logger.error(f"Health check - database error: {e}")
    
    is_healthy = db_status == "connected"
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "database": db_status,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "frontend_url_configured": bool(os.getenv("FRONTEND_URL")),
    }
