from __future__ import annotations

import json
import logging
from threading import Lock
from typing import Any, Callable, Dict, Optional

from app.agent_plugin.agent.agent import AgentCore
from app.agent_plugin.bootstrap import ensure_agent_plugin_configured
from app.core.config import GlobalConfig


logger = logging.getLogger(__name__)
_LOCK = Lock()
_AGENT_CORE: AgentCore | None = None


def _get_agent_core() -> AgentCore:
    global _AGENT_CORE
    with _LOCK:
        if _AGENT_CORE is None:
            ensure_agent_plugin_configured()
            _AGENT_CORE = AgentCore()
    return _AGENT_CORE


def close_agent_core() -> None:
    global _AGENT_CORE
    with _LOCK:
        if _AGENT_CORE is not None:
            _AGENT_CORE.close()
            _AGENT_CORE = None


def _parse_sse_chunk(raw_chunk: str) -> Dict[str, Any] | None:
    if not raw_chunk or not raw_chunk.startswith("data: "):
        return None
    body = raw_chunk[len("data: ") :].strip()
    if not body or body == "[DONE]":
        return None
    try:
        return json.loads(body)
    except Exception:
        return None


def run_agent_plugin(
    user_id: int,
    prompt: str,
    conversation_id: Optional[int] = None,
    trace_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    if not GlobalConfig.AGENT_PLUGIN_ENABLED:
        return {"enabled": False, "assistant_reply": "", "tool_calls": []}

    thread_id = f"conversation_{conversation_id}" if conversation_id else f"user_{user_id}_adhoc"
    assistant_reply = ""
    tool_calls: list[dict[str, Any]] = []
    seen = set()

    try:
        core = _get_agent_core()
        for raw_chunk in core.stream_run(prompt=prompt, user_id=str(user_id), thread_id=thread_id):
            payload = _parse_sse_chunk(raw_chunk)
            if not payload:
                continue

            if payload.get("node") == "agent" and payload.get("content"):
                assistant_reply = str(payload["content"])

            for tc in payload.get("tool_calls", []) or []:
                normalized = {
                    "tool": tc.get("name", "tool"),
                    "input": json.dumps(tc.get("args", {}), ensure_ascii=False),
                    "output": "",
                }
                key = json.dumps(normalized, ensure_ascii=False, sort_keys=True)
                if key in seen:
                    continue
                seen.add(key)
                tool_calls.append(normalized)
                if trace_callback:
                    trace_callback(normalized)

    except Exception as exc:
        logger.exception("Agent plugin 执行失败，准备回退旧链路: %s", exc)
        return {"enabled": True, "assistant_reply": "", "tool_calls": [], "error": str(exc)}

    return {"enabled": True, "assistant_reply": assistant_reply, "tool_calls": tool_calls}
