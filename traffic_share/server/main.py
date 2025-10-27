"""
Main FastAPI application
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time

from traffic_share.server.config import settings
from traffic_share.server.database import engine, Base
from traffic_share.server.logger import logger
from traffic_share.server.limiter import rate_limiter

# Import all routes
from traffic_share.server.routes import (
    auth_routes,
    user_routes,
    traffic_routes,
    payment_routes,
    buyer_routes,
    admin_routes,
    system_routes
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Traffic Share API...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Connect to Redis for rate limiting
    try:
        await rate_limiter.connect()
        logger.info("Redis connected for rate limiting")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
    
    logger.info("Traffic Share API started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Traffic Share API...")
    
    # Disconnect from Redis
    try:
        await rate_limiter.disconnect()
    except Exception:
        pass
    
    logger.info("Traffic Share API stopped")


# Create FastAPI app
app = FastAPI(
    title="Traffic Share API",
    description="API for traffic sharing platform",
    version=settings.APP_VERSION,
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Include routers
app.include_router(auth_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(traffic_routes.router, prefix="/api")
app.include_router(payment_routes.router, prefix="/api")
app.include_router(buyer_routes.router, prefix="/api")
app.include_router(admin_routes.router, prefix="/api")
app.include_router(system_routes.router, prefix="/api")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Traffic Share API",
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "traffic_share.server.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
