"""
FastAPI main application for Resume Optimizer
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Import database
from core.database import init_db, cleanup_expired_sessions

# Import routers (will be created in API modules)
from api import session, upload, linkedin, company, analyze, resume, study, export_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Cleanup expired sessions on startup
    cleaned = cleanup_expired_sessions()
    print(f"✅ Cleaned up {cleaned} expired sessions")
    
    yield
    
    # Shutdown: cleanup
    print("👋 Shutting down")


# Create FastAPI app
app = FastAPI(
    title="Resume Optimizer API",
    description="AI-powered resume optimization with confidence scoring and citations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        "https://staging.d1a9rwz0d7hjvm.amplifyapp.com",  # Production (if needed)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Resume Optimizer API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Register API routers
app.include_router(session.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(upload.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(linkedin.router, prefix="/api/linkedin", tags=["linkedin"])
app.include_router(company.router, prefix="/api/company", tags=["company"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(study.router, prefix="/api/study", tags=["study"])
app.include_router(export_routes.router, prefix="/api/export", tags=["export"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    )
