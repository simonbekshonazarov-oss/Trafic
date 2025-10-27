"""Main FastAPI application for Traffic Share."""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from traffic_share.server.database import create_tables
from traffic_share.server.routes import auth_routes, user_routes, traffic_routes, buyer_routes, admin_routes, system_routes
from traffic_share.core.exceptions import TrafficShareException

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    create_tables()
    print("Database tables created successfully")
    yield
    # Shutdown
    print("Application shutting down")

# Create FastAPI app
app = FastAPI(
    title="Traffic Share API",
    description="API for traffic sharing platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this properly in production
)

# Global exception handler
@app.exception_handler(TrafficShareException)
async def traffic_share_exception_handler(request, exc):
    """Handle custom exceptions."""
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": str(exc), "error_code": exc.__class__.__name__}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "error_code": "HTTP_ERROR"}
    )

# Include routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_routes.router, prefix="/api/user", tags=["User"])
app.include_router(traffic_routes.router, prefix="/api/traffic", tags=["Traffic"])
app.include_router(buyer_routes.router, prefix="/api/buyer", tags=["Buyer"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin"])
app.include_router(system_routes.router, prefix="/api/system", tags=["System"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Traffic Share API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2025-01-27T00:00:00Z",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "traffic_share.server.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
