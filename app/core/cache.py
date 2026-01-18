"""
Redis caching layer implementing Cache-Aside pattern.
Provides decorators and utilities for caching frequently accessed data.
"""
import json
import logging
from typing import Any, Optional, Callable
from functools import wraps
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager with async support and error handling."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Initialize Redis connection pool."""
        if not settings.ENABLE_CACHING:
            logger.info("Caching is disabled in configuration")
            return
        
        try:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            # Test connection
            await self.redis_client.ping()
            self._connected = True
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            self._connected = False
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False
            logger.info("Redis cache connection closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected and self.redis_client is not None
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value (deserialized from JSON) or None if not found
        """
        if not self.is_connected:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
        except Exception as e:
            logger.warning(f"Cache get error for key '{key}': {e}")
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            cache_ttl = ttl if ttl is not None else settings.CACHE_DEFAULT_TTL
            await self.redis_client.setex(key, cache_ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {cache_ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key '{key}': {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            await self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key '{key}': {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "products:*", "user:123:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.is_connected:
            return 0
        
        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern, count=100):
                keys.append(key)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"Cache DELETE PATTERN: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error for '{pattern}': {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.warning(f"Cache exists error for key '{key}': {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value after increment
        """
        if not self.is_connected:
            return 0
        
        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.warning(f"Cache increment error for key '{key}': {e}")
            return 0


# Global cache instance
cache = RedisCache()


def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Cache key string (e.g., "user:123", "orders:user:456:status:pending")
    """
    key_parts = [str(arg) for arg in args if arg is not None]
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()) if v is not None)
    return ":".join(key_parts)


def build_cache_key(prefix: str, **kwargs) -> str:
    """
    Build a cache key from prefix and kwargs.
    Filters out database sessions and None values.
    
    Args:
        prefix: Cache key prefix
        **kwargs: Key-value pairs to include in cache key
    
    Returns:
        Formatted cache key
    """
    # Filter out db sessions and None values
    clean_kwargs = {
        k: str(v) for k, v in kwargs.items() 
        if v is not None and not hasattr(v, 'execute')
    }
    
    if not clean_kwargs:
        return prefix
    
    key_parts = [f"{k}:{v}" for k, v in sorted(clean_kwargs.items())]
    return f"{prefix}:{':'.join(key_parts)}"


# NOTE: For FastAPI routes, we DON'T use decorators on route functions
# Instead, we cache manually inside the function to avoid issues with
# dependency injection and async context. See examples in routes.


async def invalidate_cache(prefix: str, *args, **kwargs) -> None:
    """
    Invalidate cache for a specific key or pattern.
    Use this when data is modified (POST, PUT, PATCH, DELETE).
    
    Args:
        prefix: Cache key prefix
        *args: Additional key components
        **kwargs: Additional key components
        
    Usage:
        # Invalidate specific user
        await invalidate_cache("user", user_id=user_id)
        
        # Invalidate all orders for a user
        await invalidate_cache("orders", user_id=user_id)
        
        # Invalidate all products
        await invalidate_cache("products")
    """
    if args or kwargs:
        # Delete specific key
        key_suffix = cache_key(*args, **kwargs)
        key = f"{prefix}:{key_suffix}"
        await cache.delete(key)
    else:
        # Delete all keys with this prefix
        await cache.delete_pattern(f"{prefix}:*")