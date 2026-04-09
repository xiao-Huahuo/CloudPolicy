import re
from pathlib import Path
from typing import Any


def _load_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


class StaticSafetyEngine:
    PHONE_RE = re.compile(r"\b1[3-9]\d{9}\b")
    EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    ID_RE = re.compile(r"\b\d{17}[\dXx]\b")
    SECRET_RE = re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.input_blocklist = _load_lines(base_dir / "input_blocklist.txt")
        self.injection_blocklist = _load_lines(base_dir / "prompt_injection_blocklist.txt")
        self.output_blocklist = _load_lines(base_dir / "output_blocklist.txt")

    def _mask_privacy(self, text: str) -> tuple[str, list[str]]:
        out = text
        tags: list[str] = []
        if self.PHONE_RE.search(out):
            out = self.PHONE_RE.sub("[PHONE]", out)
            tags.append("privacy_phone")
        if self.EMAIL_RE.search(out):
            out = self.EMAIL_RE.sub("[EMAIL]", out)
            tags.append("privacy_email")
        if self.ID_RE.search(out):
            out = self.ID_RE.sub("[IDCARD]", out)
            tags.append("privacy_idcard")
        if self.SECRET_RE.search(out):
            out = self.SECRET_RE.sub("[SECRET]", out)
            tags.append("privacy_secret")
        return out, tags

    def audit_input(self, text: str, user_role: str = "normal") -> dict[str, Any]:
        raw = (text or "").strip()
        low = raw.lower()
        tags: list[str] = []

        for kw in self.injection_blocklist:
            if kw.lower() in low:
                return {
                    "decision": "block",
                    "reason": f"命中提示词注入规则: {kw}",
                    "risk_tags": ["prompt_injection"],
                    "sanitized_text": raw,
                }

        for kw in self.input_blocklist:
            if kw.lower() in low:
                return {
                    "decision": "block",
                    "reason": f"命中输入风险词: {kw}",
                    "risk_tags": ["input_blocklist_hit"],
                    "sanitized_text": raw,
                }

        sanitized, privacy_tags = self._mask_privacy(raw)
        tags.extend(privacy_tags)
        if sanitized != raw:
            return {
                "decision": "sanitize",
                "reason": "检测到敏感信息，已脱敏继续处理",
                "risk_tags": tags,
                "sanitized_text": sanitized,
            }

        return {
            "decision": "allow",
            "reason": "输入审核通过",
            "risk_tags": tags,
            "sanitized_text": raw,
        }

    def audit_tool_calls(
        self,
        tool_calls: list[dict[str, Any]],
        allowed_tools: set[str],
        user_role: str = "normal",
    ) -> dict[str, Any]:
        write_tools = {
            "create_todos_from_chat",
            "confirm_todo",
            "update_user_settings",
            "add_favorite",
            "rewrite_for_audience",
        }

        rewritten = []
        rewritten_any = False
        for call in tool_calls:
            name = str(call.get("name", "")).strip()
            if not name or name not in allowed_tools:
                return {
                    "decision": "deny",
                    "reason": f"未注册或不允许的工具: {name or 'unknown'}",
                    "tool_calls": [],
                }

            args = call.get("args")
            if not isinstance(args, dict):
                args = {}
                rewritten_any = True

            safe_args: dict[str, Any] = {}
            for k, v in args.items():
                if isinstance(v, str):
                    vv = v[:2000]
                    if vv != v:
                        rewritten_any = True
                    safe_args[k] = vv
                else:
                    safe_args[k] = v

            if name in write_tools and "confirm" in safe_args and not isinstance(safe_args["confirm"], bool):
                safe_args["confirm"] = False
                rewritten_any = True

            rewritten.append({"name": name, "args": safe_args, "id": call.get("id")})

        return {
            "decision": "rewrite" if rewritten_any else "allow",
            "reason": "工具调用审核通过（rewrite）" if rewritten_any else "工具调用审核通过",
            "tool_calls": rewritten,
        }

    def audit_output(self, text: str) -> dict[str, Any]:
        raw = (text or "").strip()
        low = raw.lower()

        for kw in self.output_blocklist:
            if kw.lower() in low:
                return {
                    "decision": "block",
                    "reason": f"命中输出风险词: {kw}",
                    "safe_text": "该请求涉及风险内容，无法提供相关输出。",
                }

        sanitized, tags = self._mask_privacy(raw)
        if sanitized != raw:
            return {
                "decision": "sanitize",
                "reason": f"输出已脱敏: {','.join(tags)}" if tags else "输出已脱敏",
                "safe_text": sanitized,
            }

        return {
            "decision": "allow",
            "reason": "输出审核通过",
            "safe_text": raw,
        }
