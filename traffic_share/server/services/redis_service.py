"""Redis service for caching and rate limiting."""

import redis
import json
import os
from typing import Optional, Any, Dict
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class RedisService:
    """Redis service for caching and rate limiting."""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        try:
            return self.redis_client.get(key)
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in Redis."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if expire:
                return self.redis_client.setex(key, expire, value)
            else:
                return self.redis_client.set(key, value)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment value in Redis."""
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Redis increment error: {e}")
            return None
    
    async def set_expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        try:
            return bool(self.redis_client.expire(key, seconds))
        except Exception as e:
            print(f"Redis expire error: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """Get time to live for key."""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            print(f"Redis TTL error: {e}")
            return -1
    
    async def rate_limit(self, key: str, limit: int, window: int) -> Dict[str, Any]:
        """Check rate limit for key."""
        try:
            current = await self.get(key)
            if current is None:
                await self.set(key, 1, window)
                return {"allowed": True, "remaining": limit - 1, "reset_time": window}
            
            current_count = int(current)
            if current_count >= limit:
                ttl = await self.get_ttl(key)
                return {"allowed": False, "remaining": 0, "reset_time": ttl}
            
            await self.increment(key)
            return {"allowed": True, "remaining": limit - current_count - 1, "reset_time": ttl}
        
        except Exception as e:
            print(f"Rate limit error: {e}")
            return {"allowed": True, "remaining": limit, "reset_time": 0}
    
    async def cache_user_session(self, user_id: int, session_data: Dict) -> bool:
        """Cache user session data."""
        key = f"user_session:{user_id}"
        return await self.set(key, session_data, 3600)  # 1 hour
    
    async def get_user_session(self, user_id: int) -> Optional[Dict]:
        """Get cached user session data."""
        key = f"user_session:{user_id}"
        data = await self.get(key)
        if data:
            try:
                return json.loads(data)
            except:
                return None
        return None
    
    async def cache_traffic_stats(self, stats: Dict) -> bool:
        """Cache traffic statistics."""
        key = "traffic_stats"
        return await self.set(key, stats, 300)  # 5 minutes
    
    async def get_traffic_stats(self) -> Optional[Dict]:
        """Get cached traffic statistics."""
        key = "traffic_stats"
        data = await self.get(key)
        if data:
            try:
                return json.loads(data)
            except:
                return None
        return None
    
    async def lock_resource(self, resource: str, timeout: int = 30) -> bool:
        """Lock a resource for exclusive access."""
        key = f"lock:{resource}"
        try:
            # Try to set the key with expiration
            result = self.redis_client.set(key, "locked", nx=True, ex=timeout)
            return bool(result)
        except Exception as e:
            print(f"Lock error: {e}")
            return False
    
    async def unlock_resource(self, resource: str) -> bool:
        """Unlock a resource."""
        key = f"lock:{resource}"
        return await self.delete(key)
    
    async def health_check(self) -> bool:
        """Check Redis connection health."""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            print(f"Redis health check failed: {e}")
            return False

# Global Redis service instance
redis_service = RedisService()
