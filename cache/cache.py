import redis
import json
from typing import Optional, Any
from config import settings

_cache_client: Optional[Any] = None
_use_redis = False


async def init_cache():
    """Initialize cache (Redis or in-memory fallback)."""
    global _cache_client, _use_redis

    if settings.redis_url:
        try:
            _cache_client = redis.from_url(settings.redis_url, decode_responses=True)
            _cache_client.ping()
            _use_redis = True
            print("[OK] Connected to Redis cache")
        except Exception as e:
            print(f"[!] Redis connection failed ({e}), using in-memory cache")
            _cache_client = {}
            _use_redis = False
    else:
        _cache_client = {}
        _use_redis = False
        print("[OK] Using in-memory cache")


async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    if _use_redis and _cache_client:
        value = _cache_client.get(key)
        return json.loads(value) if value else None
    elif isinstance(_cache_client, dict):
        return _cache_client.get(key)
    return None


async def cache_set(key: str, value: Any, ttl: int = 300):
    """Set value in cache with TTL (in seconds)."""
    if _use_redis and _cache_client:
        _cache_client.setex(key, ttl, json.dumps(value, default=str))
    elif isinstance(_cache_client, dict):
        _cache_client[key] = value


async def cache_delete(key: str):
    """Delete value from cache."""
    if _use_redis and _cache_client:
        _cache_client.delete(key)
    elif isinstance(_cache_client, dict):
        _cache_client.pop(key, None)


async def close_cache():
    """Close cache connection."""
    global _cache_client, _use_redis
    if _use_redis and _cache_client:
        _cache_client.close()
        print("[OK] Redis cache closed")
    _cache_client = None
    _use_redis = False
