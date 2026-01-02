"""
AI Video Generator API
FastAPI application for generating product review videos.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import get_settings
from app.core.database import engine, Base
from app.api.videos import router as videos_router
from app.schemas.video import HealthResponse

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create directories
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.output_dir, exist_ok=True)

app = FastAPI(
    title="AI Video Generator API",
    description="Generate product review videos using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for outputs
app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")

# Include routers
app.include_router(videos_router)


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")
