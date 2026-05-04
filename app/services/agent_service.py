import json
import logging
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from sqlmodel import Session, select

from app.ai.document_parser import parse_document
from app.models.chat_message import ChatMessage
from app.models.settings import Settings
from app.services import chat_message_service, agent_plugin_service
from app.services.agent_tool_services.base import knowledge_graph_display, original_text_display

logger = logging.getLogger(__name__)

_FILE_REF_RE = re.compile(r"(/media/(?:docs|images|avatars)/[^\s\"'<>]+)")
_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".tif"}
_UPLOAD_PARSE_MARKERS = (
    "\u3010\u6587\u4ef6\u89e3\u6790\u3011",
    "\u3010\u6587\u4ef6\u5f15\u7528\u3011",
    "\u3010\u56fe\u7247\u89e3\u6790\u3011",
    "\u3010\u56fe\u7247\u5f15\u7528\u3011",
)
_OCR_INTENT_KEYWORDS = (
    "ocr",
    "\u63d0\u53d6\u6587\u5b57",
    "\u63d0\u53d6\u6587\u672c",
    "\u63d0\u53d6\u56fe\u7247\u6587\u5b57",
    "\u63d0\u53d6\u56fe\u4e2d\u6587\u5b57",
    "\u8bc6\u522b\u6587\u5b57",
    "\u8bc6\u522b\u56fe\u7247\u6587\u5b57",
    "\u56fe\u7247\u8f6c\u6587\u5b57",
    "\u8f6c\u6210\u6587\u5b57",
    "\u539f\u6837\u63d0\u53d6",
)
_GRAPH_INTENT_KEYWORDS = (
    "\u56fe\u8c31",
    "\u53ef\u89c6\u5316",
    "\u7ed3\u6784\u5316",
    "\u5173\u7cfb\u56fe",
    "\u8282\u70b9",
    "\u89e3\u6790",
    "\u68b3\u7406",
    "\u5206\u6790",
    "\u603b\u7ed3",
    "\u77e5\u8bc6\u56fe\u8c31",
)
_UPLOAD_ACK_ONLY_REQUESTS = {
    "",
    "解析",
    "解析它",
    "解析文件",
    "解析这个文件",
    "解析一下",
    "生成图谱",
    "生成知识图谱",
    "查看图谱",
    "提取文本",
    "提取文字",
    "ocr",
}
_UPLOAD_ACK_REPLIES = {
    "已生成图谱小窗，可直接查看知识图谱并切换原文。",
    "已读取上传内容，并打开原文小窗。",
    "已提取图片文字，并打开结果小窗。",
}

AGENT_NAME = "云小圆 (CloudCycle)"

_SPLIT_PATTERN = re.compile(r"[，,；;。\n、]+")
_DATE_PATTERN = re.compile(r"(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}月\d{1,2}日)")


def _split_items(text: Optional[str]) -> List[str]:
    if not text:
        return []
    items = [item.strip() for item in _SPLIT_PATTERN.split(text) if item.strip()]
    return items[:12]


def _build_steps(process_text: Optional[str]) -> List[str]:
    steps = _split_items(process_text)
    if steps:
        return steps
    return ["准备材料", "提交申请或办理", "等待审核或处理", "领取结果或完成办理"]


def _build_materials(materials_text: Optional[str]) -> List[str]:
    materials = _split_items(materials_text)
    return materials if materials else ["身份证明材料", "申请表或登记材料", "相关证明材料"]


def _build_notices(precautions: Optional[str], risk_warnings: Optional[str]) -> List[str]:
    notices = _split_items(precautions) + _split_items(risk_warnings)
    if notices:
        return notices
    return ["注意核对材料完整性", "关注时间节点与截止日期", "避免信息填写错误"]


def _build_risks(risk_warnings: Optional[str]) -> List[str]:
    risks = _split_items(risk_warnings)
    if risks:
        return risks
    return ["材料缺失可能导致退回", "超过截止时间可能失效"]


def _build_timeline(time_deadline: Optional[str], original_text: str) -> List[Dict[str, Any]]:
    timeline: List[Dict[str, Any]] = []
    if time_deadline:
        timeline.append({"time": time_deadline, "event": "截止时间或办理节点"})
    matches = _DATE_PATTERN.findall(original_text or "")
    for date_text in matches[:3]:
        if time_deadline and date_text in time_deadline:
            continue
        timeline.append({"time": date_text, "event": "原文提及的时间点"})
    if not timeline:
        timeline.append({"time": "待确认", "event": "请结合原文确认时间节点"})
    return timeline


def _build_checklist(steps: List[str], materials: List[str]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for step in steps[:4]:
        items.append({"label": step, "status": "pending", "type": "step"})
    for material in materials[:4]:
        items.append({"label": material, "status": "pending", "type": "material"})
    return items


def _build_summary(parsed: Dict[str, Any]) -> str:
    matter = parsed.get("handling_matter") or "办理事项"
    audience = parsed.get("target_audience") or "适用人群"
    time_deadline = parsed.get("time_deadline") or "待确认"
    return f"本次为 {matter}，面向 {audience}，关键时间节点：{time_deadline}。"


def _extract_file_refs_from_text(text: Optional[str]) -> List[str]:
    refs: List[str] = []
    seen: set[str] = set()
    for match in _FILE_REF_RE.findall(str(text or "")):
        ref = match.rstrip(".,;:)]}>")
        if not ref or ref in seen:
            continue
        seen.add(ref)
        refs.append(ref)
    return refs


def _is_image_file_ref(file_ref: str) -> bool:
    return Path(str(file_ref or "")).suffix.lower() in _IMAGE_SUFFIXES


def _extract_request_text_for_intent(user_text: Optional[str]) -> str:
    raw_text = str(user_text or "")
    media_pos = raw_text.find("/media/")
    if media_pos >= 0:
        raw_text = raw_text[:media_pos]
    request_lines: List[str] = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("\u3010") and "\u3011" in stripped:
            break
        request_lines.append(line)
    request_text = "\n".join(request_lines).strip()
    return request_text or raw_text


def _detect_upload_parse_intent(user_text: Optional[str]) -> Dict[str, Any]:
    raw_text = str(user_text or "")
    file_refs = _extract_file_refs_from_text(raw_text)
    has_upload_context = bool(file_refs) or any(marker in raw_text for marker in _UPLOAD_PARSE_MARKERS)
    has_image_upload = any(_is_image_file_ref(ref) for ref in file_refs)
    request_text = _extract_request_text_for_intent(raw_text)
    lowered = request_text.lower()
    wants_ocr = has_image_upload and any(keyword in lowered or keyword in request_text for keyword in _OCR_INTENT_KEYWORDS)
    wants_graph = any(keyword in lowered or keyword in request_text for keyword in _GRAPH_INTENT_KEYWORDS)

    display_mode = "default"
    if has_upload_context:
        display_mode = "ocr_text" if wants_ocr and not wants_graph else "knowledge_graph"

    result = {
        "has_upload_context": has_upload_context,
        "has_image_upload": has_image_upload,
        "display_mode": display_mode,
        "file_refs": file_refs,
    }
    return result


def _normalize_evidence(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = item.get("title") or item.get("source") or item.get("category") or "知识条目"
        snippet = item.get("snippet") or item.get("content") or ""
        normalized.append(
            {
                "title": str(title),
                "category": item.get("category") or item.get("source"),
                "score": float(item.get("score", 0) or 0),
                "snippet": str(snippet),
                "tags": list(item.get("tags") or []),
                "source": item.get("source"),
                "content": item.get("content"),
            }
        )
    return normalized


def _append_display_card(
    display_cards: List[Dict[str, Any]],
    seen: set[str],
    card: Dict[str, Any],
) -> None:
    key = json.dumps(card, ensure_ascii=False, sort_keys=True, default=str)
    if key in seen:
        return
    seen.add(key)
    display_cards.append(card)


def _has_display_card_type(display_cards: List[Dict[str, Any]], card_type: str) -> bool:
    for card in display_cards:
        if isinstance(card, dict) and str(card.get("type") or "") == card_type:
            return True
    return False


def _extract_original_text_card_content(display_cards: List[Dict[str, Any]]) -> str:
    for card in display_cards:
        if not isinstance(card, dict) or str(card.get("type") or "") != "original_text":
            continue
        payload = card.get("payload")
        if isinstance(payload, dict) and str(payload.get("content") or "").strip():
            return str(payload.get("content") or "")
    return ""


def _extract_uploaded_body_text(user_text: Optional[str]) -> str:
    raw_text = str(user_text or "")
    if not raw_text:
        return ""

    body_lines: List[str] = []
    seen_marker = False
    for line in raw_text.splitlines():
        stripped = line.strip()
        if any(stripped.startswith(marker) for marker in _UPLOAD_PARSE_MARKERS):
            seen_marker = True
            continue
        if seen_marker:
            body_lines.append(line)

    body_text = "\n".join(body_lines).strip()
    if body_text:
        return body_text

    fallback_lines = [
        line
        for line in raw_text.splitlines()
        if not any(line.strip().startswith(marker) for marker in _UPLOAD_PARSE_MARKERS)
    ]
    return "\n".join(fallback_lines).strip()


def _normalize_chat_text_content(text: Any) -> str:
    normalized = str(text or "")
    if not normalized:
        return ""
    normalized = normalized.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")
    return normalized.strip()


def _build_uploaded_parse_reply(result: Dict[str, Any], user_text: str | None = None) -> str:
    parse_display_intent = _detect_upload_parse_intent(user_text)
    if not parse_display_intent.get("has_upload_context"):
        return ""

    display_cards = [card for card in list(result.get("display_cards", []) or []) if isinstance(card, dict)]
    if parse_display_intent.get("display_mode") == "ocr_text":
        structured = result.get("structured", {}) or {}
        content_text = (
            _extract_original_text_card_content(display_cards)
            or str(structured.get("content") or "")
            or _extract_uploaded_body_text(user_text)
        )
        content_text = _normalize_chat_text_content(content_text)
        return content_text or "已提取图片文字，并打开结果小窗。"

    if _has_display_card_type(display_cards, "knowledge_graph"):
        return "已生成图谱小窗，可直接查看知识图谱并切换原文。"
    return "已读取上传内容，并打开原文小窗。"


def _has_specific_upload_request(user_text: str | None) -> bool:
    request_text = _extract_request_text_for_intent(user_text)
    request_text = re.sub(_FILE_REF_RE, "", request_text).strip()
    request_text = re.sub(r"\s+", "", request_text).lower().strip("。.!！?？：:，,；;、")
    if request_text in _UPLOAD_ACK_ONLY_REQUESTS:
        return False
    return bool(request_text)


def _meaningful_assistant_reply(result: Dict[str, Any]) -> str:
    reply = str(result.get("assistant_reply") or "").strip()
    if not reply or reply in _UPLOAD_ACK_REPLIES:
        return ""
    if _is_json_like(reply) or _is_low_signal_reply(reply):
        return ""
    return reply


def _select_upload_assistant_reply(result: Dict[str, Any], user_text: str | None = None) -> str:
    parse_display_intent = _detect_upload_parse_intent(user_text)
    if not parse_display_intent.get("has_upload_context"):
        return ""
    if _has_specific_upload_request(user_text):
        reply = _meaningful_assistant_reply(result)
        if reply:
            return reply
    return _build_uploaded_parse_reply(result, user_text=user_text)


def run_agent(
    session: Session,
    user_id: int,
    original_text: str,
    file_url: Optional[str],
    goal: Optional[str],
    scene: Optional[str],
    mode: str = "agent",
    use_rag: bool = True,
    top_k: int = 5,
    save_to_history: bool = True,
    conversation_id: Optional[int] = None,
    trace_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    user_audience_label=None,
) -> Dict[str, Any]:
    graph_reply = ""
    tool_state: Dict[str, Any] = {}
    safe_text = original_text

    try:
        plugin_result = agent_plugin_service.run_agent_plugin(
            user_id=user_id,
            prompt=original_text,
            mode=mode,
            conversation_id=conversation_id,
            trace_callback=trace_callback,
        )
        graph_reply = plugin_result.get("assistant_reply", "") or ""
        tool_state = {
            "tool_calls": plugin_result.get("tool_calls", []),
            "structured": plugin_result.get("structured"),
            "parse_mode": plugin_result.get("parse_mode"),
            "evidence": plugin_result.get("evidence", []),
            "display_cards": plugin_result.get("display_cards", []),
        }
        safe_text = original_text
    except Exception:
        graph_reply = ""
        tool_state = {}
        safe_text = original_text

    parsed = tool_state.get("structured")
    parse_mode = tool_state.get("parse_mode")
    if not parsed or not parse_mode:
        parsed, parse_mode = parse_document(safe_text, user_id)

    if not isinstance(parsed, dict):
        if hasattr(parsed, "model_dump"):
            parsed = parsed.model_dump()
        elif hasattr(parsed, "dict"):
            parsed = parsed.dict()
        else:
            parsed = {"original_text": safe_text}

    parsed.setdefault("original_text", safe_text)
    parsed.setdefault("nodes", [])
    parsed.setdefault("links", [])
    parsed.setdefault("dynamic_payload", {})
    parsed.setdefault("visual_config", {"focus_node": None, "initial_zoom": 1.0, "text_mapping": {}})
    parsed["file_url"] = file_url or parsed.get("file_url")
    parse_display_intent = _detect_upload_parse_intent(original_text)
    if parse_display_intent.get("has_upload_context"):
        logger.info(
            "Agent parse display intent user_id=%s mode=%s display_mode=%s has_image_upload=%s file_refs=%s",
            user_id,
            mode,
            parse_display_intent.get("display_mode"),
            parse_display_intent.get("has_image_upload"),
            json.dumps(parse_display_intent.get("file_refs", []), ensure_ascii=False),
        )

    steps = _build_steps(parsed.get("handling_process"))
    materials = _build_materials(parsed.get("required_materials"))
    notices = _build_notices(parsed.get("precautions"), parsed.get("risk_warnings"))
    risks = _build_risks(parsed.get("risk_warnings"))
    timeline = _build_timeline(parsed.get("time_deadline"), original_text)
    checklist = _build_checklist(steps, materials)
    summary = _build_summary(parsed)
    if _is_low_signal_reply(graph_reply):
        if graph_reply.strip():
            logger.info("Agent reply downgraded to fallback user_id=%s parse_mode=%s reply=%s", user_id, parse_mode, graph_reply)
        graph_reply = ""

    evidence: List[Dict[str, Any]] = []
    avg_score = 0.0
    result_count = 0
    if use_rag and tool_state.get("evidence"):
        evidence = _normalize_evidence(tool_state.get("evidence", []))
        result_count = len(evidence)
        avg_score = sum(item.get("score", 0) for item in evidence) / result_count if result_count else 0.0

    confidence = 0.35
    if parse_mode == "ai":
        confidence += 0.2
    if use_rag:
        confidence += min(avg_score, 1.0) * 0.45
    confidence = round(min(confidence, 0.95), 3)

    chat_message_id = None
    user_audience_label = "通用"
    try:
        settings = session.exec(select(Settings).where(Settings.user_id == user_id)).first()
        if settings:
            mapping = {
                "elderly": "老年版",
                "student": "学生版",
                "worker": "职场版",
                "none": "通用",
            }
            user_audience_label = mapping.get(settings.default_audience, "通用")
    except Exception:
        pass

    if save_to_history:
        analysis_payload = {
            "parse_mode": parse_mode,
            "agent_name": AGENT_NAME,
            "confidence": confidence,
            "goal": goal,
            "scene": scene,
            "mode": mode,
        }
        parsed["chat_analysis"] = json.dumps(analysis_payload, ensure_ascii=False)
        message: ChatMessage = chat_message_service.create_message_from_payload(
            session=session,
            message_payload=parsed,
            user_id=user_id,
        )
        chat_message_id = message.id

    display_cards: List[Dict[str, Any]] = []
    display_seen: set[str] = set()
    show_parse_cards = parse_display_intent.get("has_upload_context")
    allow_graph_display = parse_display_intent.get("display_mode") != "ocr_text"
    for card in list(tool_state.get("display_cards", []) or []):
        if isinstance(card, dict):
            card_type = str(card.get("type") or "")
            if card_type in {"knowledge_graph", "original_text"} and not show_parse_cards:
                continue
            if not allow_graph_display and card_type == "knowledge_graph":
                continue
            _append_display_card(display_cards, display_seen, card)

    fallback_display_text = _extract_uploaded_body_text(original_text) or str(parsed.get("content") or "") or safe_text
    if show_parse_cards and fallback_display_text and not _has_display_card_type(display_cards, "original_text"):
        _append_display_card(
            display_cards,
            display_seen,
            original_text_display(
                title="原文内容",
                content=fallback_display_text,
                file_url=parsed.get("file_url"),
            ),
        )
    has_graph_payload = bool(parsed.get("nodes") or parsed.get("links") or parsed.get("dynamic_payload"))
    if show_parse_cards and allow_graph_display and has_graph_payload and not _has_display_card_type(display_cards, "knowledge_graph"):
        _append_display_card(
            display_cards,
            display_seen,
            knowledge_graph_display(
                title=parsed.get("handling_matter") or "解析图谱",
                content=parsed.get("content") or fallback_display_text,
                nodes=parsed.get("nodes") or [],
                links=parsed.get("links") or [],
                dynamic_payload=parsed.get("dynamic_payload") or {},
                visual_config=parsed.get("visual_config") or {},
            ),
        )

    result = {
        "agent_name": AGENT_NAME,
        "parse_mode": parse_mode,
        "confidence": confidence,
        "summary": summary,
        "structured": parsed,
        "assistant_reply": graph_reply,
        "mode": mode,
        "tool_calls": tool_state.get("tool_calls", []),
        "checklist": checklist,
        "timeline": timeline,
        "process_steps": steps,
        "materials": materials,
        "notices": notices,
        "risks": risks,
        "rag_metrics": {
            "result_count": result_count,
            "avg_score": round(avg_score, 3),
            "hit_rate": 1.0 if result_count > 0 else 0.0,
        },
        "evidence": evidence,
        "display_cards": display_cards,
        "chat_message_id": chat_message_id,
        "user_audience": user_audience_label,
    }
    if parse_display_intent.get("has_upload_context"):
        result["assistant_reply"] = _select_upload_assistant_reply(result, user_text=original_text)
        return result
    return result


def _is_json_like(text: str) -> bool:
    if not text:
        return False
    t = text.strip()
    if (t.startswith("{") and t.endswith("}")) or (t.startswith("[") and t.endswith("]")):
        return True
    if re.search(r'"[^"]+"\\s*:', t):
        return True
    return False


_NOISE_PHRASES = [
    "本次为咨询使用的LLM",
    "关键时间节点",
    "办理流程：",
    "材料清单：",
    "注意事项：",
    "风险提示：",
]

_LOW_SIGNAL_REPLY_PHRASES = [
    "目前没有识别到明确的通知要点",
    "请补充更完整的通知内容",
    "无法访问您提供的",
    "请检查文件路径是否正确",
    "请上传文件",
]


def _strip_noise(text: Optional[str]) -> str:
    if not text:
        return ""
    t = text.strip()
    if not t or _is_json_like(t):
        return ""
    for phrase in _NOISE_PHRASES:
        if phrase in t:
            return ""
    return t


def _clean_items(items: List[str]) -> List[str]:
    cleaned: List[str] = []
    seen = set()
    for item in items:
        t = _strip_noise(str(item))
        if not t or len(t) < 2:
            continue
        if t in seen:
            continue
        cleaned.append(t)
        seen.add(t)
    return cleaned


def _format_list(items: List[str], fallback: str) -> List[str]:
    if not items:
        return [f"- {fallback}"]
    return [f"- {item}" for item in items]


def _compact_reply_text(text: Optional[str], limit: int = 180) -> str:
    normalized = " ".join(str(text or "").split()).strip()
    if not normalized:
        return ""
    return normalized if len(normalized) <= limit else f"{normalized[: limit - 3]}..."


def _preview_generic_value(value: Any, limit: int = 120) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return _compact_reply_text(value, limit=limit)
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        parts: List[str] = []
        for item in value[:4]:
            preview = _preview_generic_value(item, limit=36)
            if preview:
                parts.append(preview)
        return "；".join(parts)
    if isinstance(value, dict):
        parts: List[str] = []
        for idx, (key, item) in enumerate(value.items()):
            if idx >= 3:
                break
            preview = _preview_generic_value(item, limit=32)
            if preview:
                parts.append(f"{key}={preview}")
        return "；".join(parts)
    return _compact_reply_text(str(value), limit=limit)


def _extract_generic_points(structured: Dict[str, Any], user_text: str | None = None, limit: int = 6) -> List[str]:
    points: List[str] = []
    dynamic_payload = structured.get("dynamic_payload") if isinstance(structured.get("dynamic_payload"), dict) else {}
    if isinstance(dynamic_payload, dict):
        for key, value in dynamic_payload.items():
            if key in {"content", "nodes", "links", "visual_config", "dynamic_payload", "parse_warning", "raw_excerpt", "text", "original_text"}:
                continue
            preview = _preview_generic_value(value)
            if not preview:
                continue
            points.append(f"{key}：{preview}")
            if len(points) >= limit:
                return points

    raw_text = str(structured.get("content") or structured.get("original_text") or user_text or "")
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("【文件解析】") or stripped.startswith("【文件引用】"):
            continue
        if stripped in {"解析它", "提取文本", "提取图片文字"}:
            continue
        if len(stripped) < 6:
            continue
        points.append(_compact_reply_text(stripped, limit=120))
        if len(points) >= limit:
            break
    return points


def _guess_document_title(structured: Dict[str, Any], user_text: str | None = None) -> str:
    candidates = [
        structured.get("handling_matter"),
        structured.get("title"),
    ]
    dynamic_payload = structured.get("dynamic_payload") if isinstance(structured.get("dynamic_payload"), dict) else {}
    if isinstance(dynamic_payload, dict):
        candidates.extend(
            [
                dynamic_payload.get("title"),
                dynamic_payload.get("name"),
                dynamic_payload.get("subject"),
                dynamic_payload.get("topic"),
            ]
        )

    for candidate in candidates:
        text = _compact_reply_text(candidate, limit=48)
        if text:
            return text

    raw_text = str(structured.get("original_text") or user_text or "")
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("【文件解析】"):
            return _compact_reply_text(stripped.replace("【文件解析】", "", 1), limit=48)
        if stripped.startswith("【文件引用】"):
            continue
        if stripped in {"解析它", "提取文本", "提取图片文字"}:
            continue
        return _compact_reply_text(stripped, limit=48)
    return "当前文档"


def _guess_document_kind(title: str, text: str) -> str:
    haystack = f"{title}\n{text}"
    keyword_map = [
        ("通知", "通知/公告"),
        ("公告", "通知/公告"),
        ("培养方案", "培养方案"),
        ("方案", "方案文档"),
        ("计划", "计划文档"),
        ("赛道", "比赛策划/赛道分析"),
        ("比赛", "比赛资料"),
        ("课程", "课程资料"),
        ("项目", "项目资料"),
        ("简历", "个人材料"),
    ]
    for needle, label in keyword_map:
        if needle in haystack:
            return label
    return "通用文档"


def _build_generic_document_reply(result: Dict[str, Any], user_text: str | None = None) -> str:
    parse_display_intent = _detect_upload_parse_intent(user_text)
    if parse_display_intent.get("has_upload_context"):
        return _select_upload_assistant_reply(result, user_text=user_text)

    structured = result.get("structured", {}) or {}
    title = _guess_document_title(structured, user_text)
    raw_text = str(structured.get("original_text") or user_text or "")
    kind = _guess_document_kind(title, raw_text)
    content_summary = _compact_reply_text(structured.get("content") or result.get("summary") or raw_text, limit=220)
    generic_points = _extract_generic_points(structured, user_text=user_text, limit=6)

    lines: List[str] = []
    lines.append("## 文档概览")
    lines.append(f"- 标题：{title}")
    lines.append(f"- 类型：{kind}")
    lines.append("- 解析结论：文件内容已成功读取，但它更像资料/方案/说明文档，不适合用“办理通知”模板输出。")
    if content_summary:
        lines.append(f"- 摘要：{content_summary}")
    lines.append("")

    lines.append("## 关键信息")
    if generic_points:
        lines.extend([f"- {item}" for item in generic_points[:6]])
    else:
        lines.append("- 已读取到文档正文，但暂未抽取出更稳定的结构化字段。")
    lines.append("")
    return "\n".join(lines)


def _is_low_signal_reply(text: str) -> bool:
    normalized = " ".join(str(text or "").split()).strip()
    if not normalized:
        return True
    return any(phrase in normalized for phrase in _LOW_SIGNAL_REPLY_PHRASES)


def _looks_like_document_text(structured: Dict[str, Any], user_text: str | None = None) -> bool:
    text = str(structured.get("original_text") or user_text or "").strip()
    if any(marker in text for marker in _UPLOAD_PARSE_MARKERS):
        return True
    if len(text) >= 180:
        return True
    meaningful_lines = [line.strip() for line in text.splitlines() if line.strip()]
    return len(meaningful_lines) >= 3


def _build_general_followup_reply(user_text: str | None = None) -> str:
    question = _compact_reply_text(user_text, limit=80)
    if question:
        return f"要判断“{question}”，我还需要知道具体事项或对应材料。你可以补充政策名称、办理对象、所在地区，或上传/粘贴原文，我再按流程、材料、时间节点帮你拆解。"
    return "我还需要知道具体事项或对应材料。你可以补充政策名称、办理对象、所在地区，或上传/粘贴原文，我再按流程、材料、时间节点帮你拆解。"


def build_agent_reply(result: Dict[str, Any], user_text: str | None = None) -> str:
    audience_label = "通用"
    if result.get("user_audience"):
        audience_label = str(result.get("user_audience"))

    parse_display_intent = _detect_upload_parse_intent(user_text)
    if parse_display_intent.get("has_upload_context"):
        return _select_upload_assistant_reply(result, user_text=user_text)

    existing_reply = _meaningful_assistant_reply(result)
    if existing_reply:
        return existing_reply

    structured = result.get("structured", {}) or {}
    has_core = any(
        structured.get(key)
        for key in [
            "handling_matter",
            "required_materials",
            "handling_process",
            "time_deadline",
            "precautions",
            "risk_warnings",
        ]
    )
    if not has_core:
        if not _looks_like_document_text(structured, user_text=user_text):
            return _build_general_followup_reply(user_text=user_text)
        return _build_generic_document_reply(result, user_text=user_text)

    handling_matter = _strip_noise(structured.get("handling_matter")) or "办理事项"
    target = _strip_noise(structured.get("target_audience")) or "适用对象"
    time_deadline = _strip_noise(structured.get("time_deadline")) or "待确认"
    location = _strip_noise(structured.get("location_entrance")) or "待确认"
    summary = _strip_noise(result.get("summary")) or f"事项：{handling_matter}；对象：{target}；时间：{time_deadline}。"

    steps = _clean_items(list(result.get("process_steps", []) or []))[:6]
    materials = _clean_items(list(result.get("materials", []) or []))[:6]
    notices = _clean_items(list(result.get("notices", []) or []))[:5]
    risks = _clean_items(list(result.get("risks", []) or []))[:4]

    lines: List[str] = []
    lines.append("## 概览")
    lines.append(f"- 办理事项：{handling_matter}")
    lines.append(f"- 适用对象：{target}")
    lines.append(f"- 关键时间：{time_deadline}")
    lines.append(f"- 地点/入口：{location}")
    lines.append(f"- 简要判断：{summary}")
    lines.append("")

    lines.append("## 你需要做什么")
    lines.extend(_format_list(steps, "先确认办理渠道与提交方式（线上/线下）"))
    lines.append("")

    lines.append("## 材料与准备")
    lines.extend(_format_list(materials, "准备身份与申请相关的基础材料"))
    lines.append("")

    lines.append("## 时间节点")
    lines.append(f"- 主要截止或关键节点：{time_deadline}")
    lines.append("")

    lines.append("## 注意事项与风险")
    lines.extend(_format_list(notices, "核对信息完整性，避免填写错误"))
    lines.extend(_format_list(risks, "材料缺失或超期可能导致退回/失效"))
    lines.append("")
    return "\n".join(lines)
