# -*- coding: utf-8 -*-
"""
Caching utilities for providers.
Reduces API calls and prevents rate limiting (403 errors).
"""
import asyncio
import functools
import hashlib
import time
from typing import Any, Callable, Dict, Optional, TypeVar
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TTLCache:
    """
    Simple in-memory cache with TTL (Time To Live).
    Thread-safe for asyncio use cases.
    """
    
    def __init__(self, default_ttl: int = 300):
        """
        Args:
            default_ttl: Default TTL in seconds (5 minutes default).
        """
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    def _make_key(self, *args, **kwargs) -> str:
        """Create a hash key from arguments."""
        key_str = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    logger.debug(f"Cache HIT: {key[:8]}...")
                    return value
                else:
                    # Expired, remove it
                    del self._cache[key]
                    logger.debug(f"Cache EXPIRED: {key[:8]}...")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        async with self._lock:
            expiry = time.time() + (ttl or self._default_ttl)
            self._cache[key] = (value, expiry)
            logger.debug(f"Cache SET: {key[:8]}... (TTL: {ttl or self._default_ttl}s)")
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            logger.debug("Cache CLEARED")
    
    def stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        now = time.time()
        valid = sum(1 for _, (_, exp) in self._cache.items() if exp > now)
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid,
            "expired_entries": len(self._cache) - valid,
        }


# Global cache instance for providers
_provider_cache = TTLCache(default_ttl=300)  # 5 minutes default


def cached(ttl: int = 300):
    """
    Decorator for caching async function results.
    
    Usage:
        @cached(ttl=600)  # 10 minutes
        async def fetch_data(team_name: str) -> dict:
            ...
    
    Args:
        ttl: Time to live in seconds.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Skip 'self' for instance methods when making cache key
            cache_args = args[1:] if args and hasattr(args[0], '__class__') else args
            key = _provider_cache._make_key(func.__name__, cache_args, kwargs)
            
            # Try cache first
            cached_value = await _provider_cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache successful results (not errors)
            if isinstance(result, dict) and "error" not in result:
                await _provider_cache.set(key, result, ttl)
            elif result is not None and not isinstance(result, dict):
                await _provider_cache.set(key, result, ttl)
            
            return result
        return wrapper
    return decorator


def get_cache() -> TTLCache:
    """Get the global provider cache instance."""
    return _provider_cache
