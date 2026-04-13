import hashlib
import json
import logging
import secrets
import time
from typing import Any, Optional

import redis

from app.core.config import GlobalConfig


logger = logging.getLogger(__name__)
_memory_store: dict[str, tuple[float, dict[str, Any]]] = {}


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


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _now() -> float:
    return time.time()


def _get_record(key: str) -> tuple[Optional[dict[str, Any]], int]:
    if _redis_client:
        try:
            raw = _redis_client.get(key)
            if not raw:
                return None, 0
            ttl = max(int(_redis_client.ttl(key)), 0)
            return json.loads(raw), ttl
        except Exception as exc:
            logger.warning("Redis auth challenge read failed, falling back to memory: %s", exc)

    entry = _memory_store.get(key)
    if not entry:
        return None, 0
    expires_at, data = entry
    remaining = int(expires_at - _now())
    if remaining <= 0:
        _memory_store.pop(key, None)
        return None, 0
    return dict(data), remaining


def _set_record(key: str, data: dict[str, Any], ttl_seconds: int) -> None:
    ttl_seconds = max(int(ttl_seconds), 1)
    if _redis_client:
        try:
            _redis_client.setex(key, ttl_seconds, json.dumps(data))
            return
        except Exception as exc:
            logger.warning("Redis auth challenge write failed, falling back to memory: %s", exc)

    _memory_store[key] = (_now() + ttl_seconds, dict(data))


def _delete_record(key: str) -> None:
    if _redis_client:
        try:
            _redis_client.delete(key)
            return
        except Exception as exc:
            logger.warning("Redis auth challenge delete failed, falling back to memory: %s", exc)
    _memory_store.pop(key, None)


def create_captcha(answer: str, ttl_seconds: int) -> str:
    captcha_id = secrets.token_urlsafe(18)
    _set_record(
        f"auth:captcha:{captcha_id}",
        {"answer_hash": _hash_code(answer.strip().lower())},
        ttl_seconds,
    )
    return captcha_id


def verify_captcha(captcha_id: str, answer: str) -> bool:
    key = f"auth:captcha:{captcha_id}"
    record, _ = _get_record(key)
    if not record:
        return False
    if record.get("answer_hash") != _hash_code(answer.strip().lower()):
        return False
    _delete_record(key)
    return True


def set_cooldown(scope: str, identifier: str, ttl_seconds: int) -> None:
    _set_record(f"auth:cooldown:{scope}:{identifier}", {"locked": True}, ttl_seconds)


def get_cooldown_remaining(scope: str, identifier: str) -> int:
    _, remaining = _get_record(f"auth:cooldown:{scope}:{identifier}")
    return remaining


def issue_code(
    channel: str,
    purpose: str,
    target: str,
    code: str,
    ttl_seconds: int,
    extra: Optional[dict[str, Any]] = None,
) -> None:
    _set_record(
        f"auth:code:{channel}:{purpose}:{target}",
        {
            "code_hash": _hash_code(code),
            "attempts": 0,
            "extra": extra or {},
        },
        ttl_seconds,
    )


def verify_code(
    channel: str,
    purpose: str,
    target: str,
    code: str,
    *,
    max_attempts: int,
    consume: bool = True,
) -> tuple[bool, str, dict[str, Any]]:
    key = f"auth:code:{channel}:{purpose}:{target}"
    record, ttl_seconds = _get_record(key)
    if not record:
        return False, "missing", {}

    expected_hash = record.get("code_hash")
    attempts = int(record.get("attempts", 0))
    if expected_hash != _hash_code(code):
        attempts += 1
        if attempts >= max_attempts:
            _delete_record(key)
            return False, "too_many_attempts", {}
        record["attempts"] = attempts
        _set_record(key, record, ttl_seconds)
        return False, "invalid", {}

    extra = record.get("extra") or {}
    if consume:
        _delete_record(key)
    return True, "ok", extra
