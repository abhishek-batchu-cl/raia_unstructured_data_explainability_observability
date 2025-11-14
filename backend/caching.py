"""
Caching Module for RAIA Enterprise
===================================

Provides caching layer with:
- Redis backend
- In-memory fallback
- TTL support
- Automatic serialization
- Cache invalidation
"""

from typing import Optional, Any
from abc import ABC, abstractmethod
import json
import pickle
import hashlib
from datetime import timedelta
from functools import wraps

# ============================================================================
# Cache Interface
# ============================================================================

class CacheBackend(ABC):
    """Abstract cache backend."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache with optional TTL (seconds)."""
        pass

    @abstractmethod
    def delete(self, key: str):
        """Delete key from cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def clear(self):
        """Clear all cache."""
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        """Get cache statistics."""
        pass


# ============================================================================
# Redis Backend
# ============================================================================

class RedisCache(CacheBackend):
    """Redis cache backend."""

    def __init__(self, url: str = "redis://localhost:6379/0", prefix: str = "raia:"):
        """
        Initialize Redis cache.

        Args:
            url: Redis connection URL
            prefix: Key prefix for namespacing
        """
        try:
            import redis
            self.redis = redis.from_url(url, decode_responses=False)
            self.prefix = prefix
            # Test connection
            self.redis.ping()
            print(f"✅ Connected to Redis at {url}")
        except ImportError:
            raise ImportError("Redis support requires: pip install redis")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        try:
            value = self.redis.get(self._make_key(key))
            if value is None:
                return None
            return pickle.loads(value)
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in Redis."""
        try:
            serialized = pickle.dumps(value)
            if ttl:
                self.redis.setex(self._make_key(key), ttl, serialized)
            else:
                self.redis.set(self._make_key(key), serialized)
        except Exception as e:
            print(f"Redis set error: {e}")

    def delete(self, key: str):
        """Delete key from Redis."""
        try:
            self.redis.delete(self._make_key(key))
        except Exception as e:
            print(f"Redis delete error: {e}")

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(self.redis.exists(self._make_key(key)))
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False

    def clear(self):
        """Clear all keys with prefix."""
        try:
            keys = self.redis.keys(f"{self.prefix}*")
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            print(f"Redis clear error: {e}")

    def get_stats(self) -> dict:
        """Get Redis stats."""
        try:
            info = self.redis.info()
            return {
                "backend": "redis",
                "connected": True,
                "used_memory_mb": info.get("used_memory", 0) // (1024 * 1024),
                "total_keys": self.redis.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            return {"backend": "redis", "connected": False, "error": str(e)}


# ============================================================================
# In-Memory Backend (Fallback)
# ============================================================================

class InMemoryCache(CacheBackend):
    """In-memory cache backend (fallback when Redis unavailable)."""

    def __init__(self):
        """Initialize in-memory cache."""
        self._cache = {}
        self._ttl = {}
        print("⚠️  Using in-memory cache (Redis unavailable)")

    def _is_expired(self, key: str) -> bool:
        """Check if key is expired."""
        if key not in self._ttl:
            return False

        import time
        if time.time() > self._ttl[key]:
            self.delete(key)
            return True

        return False

    def get(self, key: str) -> Optional[Any]:
        """Get value from memory."""
        if self._is_expired(key):
            return None
        return self._cache.get(key)

    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in memory."""
        self._cache[key] = value

        if ttl:
            import time
            self._ttl[key] = time.time() + ttl

    def delete(self, key: str):
        """Delete key from memory."""
        self._cache.pop(key, None)
        self._ttl.pop(key, None)

    def exists(self, key: str) -> bool:
        """Check if key exists in memory."""
        if self._is_expired(key):
            return False
        return key in self._cache

    def clear(self):
        """Clear all memory cache."""
        self._cache.clear()
        self._ttl.clear()

    def get_stats(self) -> dict:
        """Get memory cache stats."""
        import sys
        size_bytes = sum(sys.getsizeof(v) for v in self._cache.values())

        return {
            "backend": "memory",
            "total_keys": len(self._cache),
            "size_bytes": size_bytes,
            "size_mb": size_bytes // (1024 * 1024)
        }


# ============================================================================
# Cache Manager
# ============================================================================

class CacheManager:
    """
    Unified cache manager with automatic fallback.

    Usage:
        # Try Redis, fallback to memory
        cache = CacheManager.get_instance(redis_url="redis://localhost:6379")

        # Set value
        cache.set("user:123", {"name": "John"}, ttl=300)

        # Get value
        user = cache.get("user:123")
    """

    _instance = None

    def __init__(self, backend: CacheBackend):
        """Initialize cache manager."""
        self.backend = backend
        self.hits = 0
        self.misses = 0

    @classmethod
    def get_instance(cls, redis_url: str = None) -> "CacheManager":
        """
        Get singleton cache instance.

        Args:
            redis_url: Redis connection URL (optional)

        Returns:
            CacheManager instance
        """
        if cls._instance is None:
            # Try Redis first
            if redis_url:
                try:
                    backend = RedisCache(redis_url)
                except Exception as e:
                    print(f"⚠️  Redis connection failed: {e}")
                    print("⚠️  Falling back to in-memory cache")
                    backend = InMemoryCache()
            else:
                backend = InMemoryCache()

            cls._instance = cls(backend)

        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = self.backend.get(key)

        if value is not None:
            self.hits += 1
        else:
            self.misses += 1

        return value

    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache."""
        self.backend.set(key, value, ttl)

    def delete(self, key: str):
        """Delete key from cache."""
        self.backend.delete(key)

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.backend.exists(key)

    def clear(self):
        """Clear all cache."""
        self.backend.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        backend_stats = self.backend.get_stats()

        return {
            **backend_stats,
            "cache_hits": self.hits,
            "cache_misses": self.misses,
            "hit_rate": (self.hits / (self.hits + self.misses) * 100) if (self.hits + self.misses) > 0 else 0
        }


# ============================================================================
# Cache Decorators
# ============================================================================

def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Usage:
        @cached(ttl=300, key_prefix="user")
        def get_user(user_id: str):
            # Expensive operation
            return fetch_user_from_db(user_id)

        # First call: cache miss, executes function
        user = get_user("123")

        # Second call: cache hit, returns cached value
        user = get_user("123")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(key_prefix, func.__name__, args, kwargs)

            # Try to get from cache
            cache = CacheManager.get_instance()
            cached_value = cache.get(cache_key)

            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper
    return decorator


def cache_invalidate(key_prefix: str = ""):
    """
    Decorator to invalidate cache after function execution.

    Usage:
        @cache_invalidate(key_prefix="user")
        def update_user(user_id: str, data: dict):
            # Update user in database
            ...

        # This will invalidate cache for get_user(user_id)
        update_user("123", {"name": "Jane"})
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function
            result = func(*args, **kwargs)

            # Invalidate cache
            cache_key = _generate_cache_key(key_prefix, func.__name__, args, kwargs)
            cache = CacheManager.get_instance()
            cache.delete(cache_key)

            return result

        return wrapper
    return decorator


def _generate_cache_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate cache key from function signature."""
    # Create key from function name and arguments
    key_parts = [prefix, func_name]

    # Add args
    for arg in args:
        key_parts.append(str(arg))

    # Add kwargs
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")

    # Join and hash
    key_string = ":".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()

    return f"{prefix}:{func_name}:{key_hash}"


# ============================================================================
# Cache Utilities
# ============================================================================

class CachePatterns:
    """Common caching patterns."""

    @staticmethod
    def cache_aside(cache_key: str, fetch_func, ttl: int = 300):
        """
        Cache-aside pattern (lazy loading).

        Args:
            cache_key: Cache key
            fetch_func: Function to fetch data if not in cache
            ttl: Time to live in seconds

        Returns:
            Cached or freshly fetched data
        """
        cache = CacheManager.get_instance()

        # Try cache first
        value = cache.get(cache_key)
        if value is not None:
            return value

        # Cache miss: fetch and store
        value = fetch_func()
        cache.set(cache_key, value, ttl=ttl)

        return value

    @staticmethod
    def write_through(cache_key: str, value: Any, write_func, ttl: int = 300):
        """
        Write-through pattern (update cache and storage).

        Args:
            cache_key: Cache key
            value: Value to write
            write_func: Function to write to storage
            ttl: Time to live in seconds
        """
        cache = CacheManager.get_instance()

        # Write to storage
        write_func(value)

        # Update cache
        cache.set(cache_key, value, ttl=ttl)

    @staticmethod
    def invalidate_pattern(pattern: str):
        """
        Invalidate all keys matching pattern.

        Args:
            pattern: Key pattern to invalidate
        """
        cache = CacheManager.get_instance()

        # For Redis backend
        if isinstance(cache.backend, RedisCache):
            try:
                keys = cache.backend.redis.keys(f"{cache.backend.prefix}{pattern}*")
                if keys:
                    cache.backend.redis.delete(*keys)
            except Exception as e:
                print(f"Pattern invalidation error: {e}")

        # For memory backend
        elif isinstance(cache.backend, InMemoryCache):
            keys_to_delete = [k for k in cache.backend._cache.keys() if k.startswith(pattern)]
            for key in keys_to_delete:
                cache.delete(key)


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    # Initialize cache (tries Redis, falls back to memory)
    cache = CacheManager.get_instance(redis_url="redis://localhost:6379/0")

    # Basic operations
    cache.set("user:123", {"name": "John", "age": 30}, ttl=300)
    user = cache.get("user:123")
    print(f"User: {user}")

    # Check existence
    exists = cache.exists("user:123")
    print(f"Key exists: {exists}")

    # Get stats
    stats = cache.get_stats()
    print(f"\nCache Stats:")
    import json
    print(json.dumps(stats, indent=2))

    # Test caching decorator
    @cached(ttl=60, key_prefix="expensive")
    def expensive_operation(x: int, y: int):
        """Simulate expensive operation."""
        import time
        print(f"Computing {x} + {y}...")
        time.sleep(1)
        return x + y

    # First call: slow (cache miss)
    result = expensive_operation(5, 3)
    print(f"\nFirst call result: {result}")

    # Second call: fast (cache hit)
    result = expensive_operation(5, 3)
    print(f"Second call result: {result}")

    # Cache-aside pattern
    def fetch_user_from_db():
        print("Fetching from database...")
        return {"id": "123", "name": "Alice"}

    user = CachePatterns.cache_aside("user:alice", fetch_user_from_db, ttl=300)
    print(f"\nCache-aside result: {user}")

    # Final stats
    final_stats = cache.get_stats()
    print(f"\nFinal Cache Stats:")
    print(json.dumps(final_stats, indent=2))
