from __future__ import annotations

from sqlmodel import Session

from app.services import stats_service
from app.services.agent_tool_services.base import metric_board_display, ok_item_payload


def build_metric_cards_payload(session: Session, user_id: int) -> dict:
    stats = stats_service.generate_user_stats(session, user_id)
    rag_metrics = stats.get("rag_metrics", {}) or {}
    items = [
        {"label": "累计解析", "value": stats.get("total_parsed_count", 0), "unit": "条"},
        {"label": "累计节省时间", "value": stats.get("total_time_saved_minutes", 0), "unit": "分钟"},
        {"label": "平均节省时间", "value": stats.get("avg_time_saved_minutes", 0), "unit": "分钟"},
        {"label": "RAG 命中率", "value": round(float(rag_metrics.get("hit_rate", 0) or 0) * 100, 1), "unit": "%"},
        {"label": "RAG 平均分", "value": rag_metrics.get("avg_score", 0), "unit": ""},
    ]
    return ok_item_payload(
        {"scope": "me", "items": items},
        meta={"total_metrics": len(items)},
        display=[metric_board_display(title="我的分析指标", items=items)],
    )
