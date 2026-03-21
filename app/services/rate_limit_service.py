import logging
import time
from collections import defaultdict, deque
from typing import Deque

import redis

from app.core.config import GlobalConfig


logger = logging.getLogger(__name__)
_memory_buckets: dict[str, Deque[float]] = defaultdict(deque)


def _get_redis_client():
    try:
        client = redis.Redis(
            host=GlobalConfig.REDIS_HOST,
            port=GlobalConfig.REDIS_PORT,
            db=GlobalConfig.REDIS_DB_CACHE,
            decode_responses=True,
        )
        client.ping()
        return client
    except Exception:
        return None


_redis_client = _get_redis_client()


def allow_request(bucket: str, identifier: str) -> bool:
    key = f"rate_limit:{bucket}:{identifier}"
    limit = GlobalConfig.CRAWLER_RATE_LIMIT
    window = GlobalConfig.CRAWLER_RATE_WINDOW_SECONDS

    if _redis_client:
        try:
            current = _redis_client.incr(key)
            if current == 1:
                _redis_client.expire(key, window)
            return current <= limit
        except Exception as exc:
            logger.warning("Redis 限流失败，回退内存限流: %s", exc)

    now = time.time()
    queue = _memory_buckets[key]
    while queue and now - queue[0] > window:
        queue.popleft()
    if len(queue) >= limit:
        return False
    queue.append(now)
    return True
