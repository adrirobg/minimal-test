"""
FastAPI main application entry point
Kairos BCP - Personal Knowledge Management System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users, projects, notes, keywords, sources
import uvicorn


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        description=settings.description,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": settings.project_name,
            "version": settings.version,
            "environment": settings.environment
        }
    
    # Include routers
    app.include_router(
        auth.router,
        prefix=f"{settings.api_v1_prefix}/auth",
        tags=["authentication"]
    )
    app.include_router(
        users.router,
        prefix=f"{settings.api_v1_prefix}/users",
        tags=["users"]
    )
    app.include_router(
        projects.router,
        prefix=f"{settings.api_v1_prefix}/projects",
        tags=["projects"]
    )
    app.include_router(
        notes.router,
        prefix=f"{settings.api_v1_prefix}/notes",
        tags=["notes"]
    )
    app.include_router(
        keywords.router,
        prefix=f"{settings.api_v1_prefix}/keywords",
        tags=["keywords"]
    )
    app.include_router(
        sources.router,
        prefix=f"{settings.api_v1_prefix}/sources",
        tags=["sources"]
    )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": f"Welcome to {settings.project_name} API",
            "version": settings.version,
            "docs": "/docs",
            "health": "/health",
            "auth": f"{settings.api_v1_prefix}/auth"
        }
    
    return app


# Create app instance
app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )