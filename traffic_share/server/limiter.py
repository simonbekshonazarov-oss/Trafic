"""
Rate limiting using Redis
"""

import time
from typing import Optional
import redis.asyncio as redis
from fastapi import HTTPException, Request, status

from traffic_share.server.config import settings
from traffic_share.server.logger import logger


class RateLimiter:
    """Rate limiter using Redis"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client: Optional[redis.Redis] = None
        self.key_prefix = settings.REDIS_KEY_PREFIX + "ratelimit:"
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis for rate limiting")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def is_rate_limited(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check if rate limit is exceeded
        Returns (is_limited: bool, info: dict)
        """
        if not self.redis_client or not settings.RATE_LIMIT_ENABLED:
            return False, {}
        
        try:
            full_key = f"{self.key_prefix}{key}"
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            # Remove old entries
            await self.redis_client.zremrangebyscore(full_key, 0, window_start)
            
            # Count current requests in window
            current_count = await self.redis_client.zcard(full_key)
            
            if current_count >= max_requests:
                # Rate limit exceeded
                ttl = await self.redis_client.ttl(full_key)
                return True, {
                    "limit": max_requests,
                    "remaining": 0,
                    "reset_in": ttl if ttl > 0 else window_seconds
                }
            
            # Add current request
            await self.redis_client.zadd(full_key, {str(current_time): current_time})
            
            # Set expiry
            await self.redis_client.expire(full_key, window_seconds)
            
            return False, {
                "limit": max_requests,
                "remaining": max_requests - current_count - 1,
                "reset_in": window_seconds
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return False, {}
    
    def parse_rate_string(self, rate_string: str) -> tuple[int, int]:
        """
        Parse rate string like "10/minute" to (max_requests, window_seconds)
        """
        parts = rate_string.split("/")
        if len(parts) != 2:
            return 60, 60  # Default: 60 requests per minute
        
        max_requests = int(parts[0])
        period = parts[1].lower()
        
        period_map = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400
        }
        
        window_seconds = period_map.get(period, 60)
        
        return max_requests, window_seconds


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit(
    request: Request,
    rate_string: str,
    key_suffix: str = None
):
    """
    FastAPI dependency for rate limiting
    
    Usage:
        @app.get("/endpoint", dependencies=[Depends(lambda req: check_rate_limit(req, "10/minute"))])
    """
    if not settings.RATE_LIMIT_ENABLED:
        return
    
    # Build rate limit key from IP or user
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}"
    
    if key_suffix:
        key = f"{key}:{key_suffix}"
    
    # Parse rate string
    max_requests, window_seconds = rate_limiter.parse_rate_string(rate_string)
    
    # Check rate limit
    is_limited, info = await rate_limiter.is_rate_limited(
        key, max_requests, window_seconds
    )
    
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {info.get('reset_in', 60)} seconds",
            headers={
                "X-RateLimit-Limit": str(info.get("limit", max_requests)),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(info.get("reset_in", window_seconds))
            }
        )
    
    # Add rate limit headers to response
    request.state.rate_limit_info = info
