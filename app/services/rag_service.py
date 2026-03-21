import json
import logging
import math
from collections import Counter
from pathlib import Path
from typing import Any

import jieba

from app.core.config import GlobalConfig


logger = logging.getLogger(__name__)

try:
    import chromadb  # type: ignore
except Exception:  # pragma: no cover
    chromadb = None


def _load_documents() -> list[dict[str, Any]]:
    path = Path(GlobalConfig.KNOWLEDGE_BASE_PATH)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.exception("知识库加载失败: %s", exc)
        return []


def _tokenize(text: str) -> Counter[str]:
    return Counter(
        token.strip()
        for token in jieba.cut(text or "")
        if len(token.strip()) > 1
    )


def _cosine_similarity(vec1: Counter[str], vec2: Counter[str]) -> float:
    if not vec1 or not vec2:
        return 0.0
    common = set(vec1) & set(vec2)
    dot = sum(vec1[token] * vec2[token] for token in common)
    norm1 = math.sqrt(sum(value * value for value in vec1.values()))
    norm2 = math.sqrt(sum(value * value for value in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def _search_locally(query: str, top_k: int) -> list[dict[str, Any]]:
    query_vector = _tokenize(query)
    results = []
    for item in _load_documents():
        text = (
            f"{item.get('title', '')}\n"
            f"{item.get('content', '')}\n"
            f"{' '.join(item.get('tags', []))}"
        )
        score = _cosine_similarity(query_vector, _tokenize(text))
        if score <= 0:
            continue
        results.append(
            {
                "score": round(score, 4),
                "title": item.get("title"),
                "category": item.get("category"),
                "content": item.get("content"),
                "tags": item.get("tags", []),
            }
        )
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def search_related_context(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    if not query.strip():
        return []

    if chromadb is None:
        return _search_locally(query, top_k)

    try:
        GlobalConfig.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(GlobalConfig.CHROMA_DIR))
        collection = client.get_or_create_collection("clear_notify_policy_knowledge")
        documents = _load_documents()
        if collection.count() == 0 and documents:
            collection.add(
                ids=[str(index + 1) for index in range(len(documents))],
                documents=[
                    f"{item.get('title', '')}\n{item.get('content', '')}"
                    for item in documents
                ],
                metadatas=[
                    {
                        "title": item.get("title", ""),
                        "category": item.get("category", ""),
                        "tags": ",".join(item.get("tags", [])),
                    }
                    for item in documents
                ],
            )

        result = collection.query(query_texts=[query], n_results=top_k)
        rag_items = []
        for idx, doc in enumerate(result.get("documents", [[]])[0]):
            metadata = result.get("metadatas", [[]])[0][idx]
            distance = result.get("distances", [[]])[0][idx]
            rag_items.append(
                {
                    "score": round(1 - float(distance), 4),
                    "title": metadata.get("title"),
                    "category": metadata.get("category"),
                    "content": doc,
                    "tags": metadata.get("tags", "").split(",") if metadata.get("tags") else [],
                }
            )
        return rag_items
    except Exception as exc:  # pragma: no cover
        logger.warning("ChromaDB 查询失败，回退本地检索: %s", exc)
        return _search_locally(query, top_k)


def get_status() -> dict[str, Any]:
    docs = _load_documents()
    return {
        "backend": "chromadb" if chromadb is not None else "local-vector-fallback",
        "document_count": len(docs),
        "knowledge_base_path": str(GlobalConfig.KNOWLEDGE_BASE_PATH),
    }
