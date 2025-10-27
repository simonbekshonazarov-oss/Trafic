"""Logging middleware for request/response logging."""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from traffic_share.server.services.redis_service import redis_service

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(f"Response: {response.status_code} for {request.method} {request.url.path} "
                      f"in {process_time:.3f}s")
            
            # Add processing time to response headers
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log to Redis for analytics
            await self._log_to_redis(request, response, process_time)
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(f"Error processing {request.method} {request.url.path}: {str(e)} "
                        f"in {process_time:.3f}s")
            
            # Re-raise the exception
            raise
    
    async def _log_to_redis(self, request: Request, response: Response, process_time: float):
        """Log request/response data to Redis for analytics."""
        try:
            log_data = {
                "timestamp": time.time(),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "client_ip": request.client.host if request.client else "unknown"
            }
            
            # Store in Redis with TTL of 24 hours
            await redis_service.set(f"request_log:{int(time.time())}", log_data, 86400)
            
        except Exception as e:
            logger.error(f"Failed to log to Redis: {e}")
