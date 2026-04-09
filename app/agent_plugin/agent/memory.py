import os
import json
import uuid
import hashlib
from typing import List, Dict, Optional

import chromadb
from chromadb.utils import embedding_functions

from app.agent_plugin.agent.config import AgentConfig


class LongTermMemory:
    local_ef: embedding_functions.SentenceTransformerEmbeddingFunction
    chroma_client: chromadb.ClientAPI
    collection: chromadb.Collection

    def __init__(self):
        self.local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=AgentConfig.EMBEDDING_MODEL
        )
        self.chroma_client = chromadb.PersistentClient(path=AgentConfig.VECTOR_DB_PATH)
        self.collection = self.chroma_client.get_or_create_collection(
            name=AgentConfig.COLLECTION_NAME,
            embedding_function=self.local_ef,
        )

    def _calculate_md5(self, data: List[Dict[str, str]]) -> str:
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode("utf-8")).hexdigest()

    def rag_ingest(self, user_id: str, raw_data: Optional[List[Dict[str, str]]] = None):
        final_ingest_data = []

        if os.path.exists(AgentConfig.RAG_RAW_FILE_PATH):
            try:
                with open(AgentConfig.RAG_RAW_FILE_PATH, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        final_ingest_data.extend(file_data)
                        print(
                            f"--- [长期记忆] 已从 {AgentConfig.RAG_RAW_FILE_PATH} 加载 {len(file_data)} 条初始知识 ---"
                        )
            except Exception as e:
                print(f"--- [长期记忆] 读取本地知识文件失败: {e} ---")

        if raw_data:
            final_ingest_data.extend(raw_data)

        if not final_ingest_data:
            print("--- [长期记忆] 无需同步的数据 ---")
            return

        current_hash = self._calculate_md5(final_ingest_data)

        lock_id = f"data_lock_{user_id}"
        existing_lock = self.collection.get(ids=[lock_id])

        last_hash = None
        if existing_lock and existing_lock.get("metadatas") and len(existing_lock["metadatas"]) > 0:
            last_hash = existing_lock["metadatas"][0].get("hash_lock")

        if current_hash != last_hash or AgentConfig.RAG_FORCE_UPDATE:
            print(f"--- [长期记忆] 检测到变更，开始同步 (user={user_id}) ---")

            if self.collection.count() > 0:
                self.collection.delete(where={"user_id": user_id})

            documents = []
            metadatas = []
            ids = []

            for item in final_ingest_data:
                content = str(item.get("content", "")).strip()
                if not content:
                    continue
                documents.append(content)

                meta = {"user_id": user_id}
                for key, value in item.items():
                    if key != "content":
                        meta[key] = value

                metadatas.append(meta)
                ids.append(str(uuid.uuid4()))

            if documents:
                self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

            self.collection.upsert(
                ids=[lock_id],
                documents=["HASH_LOCK_MARKER"],
                metadatas=[{"hash_lock": current_hash, "user_id": user_id}],
            )
            print(f"--- [长期记忆] 同步完成，共 {len(documents)} 条 ---")
        else:
            print("--- [长期记忆] 内容未变化，跳过同步 ---")

    def rag_query_top_k(self, query: str, user_id: str, rag_top_k: Optional[int] = None) -> List[str]:
        top_k = rag_top_k if rag_top_k is not None else AgentConfig.RAG_TOP_K

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"user_id": user_id},
            include=["documents", "distances"],
        )

        documents = (results.get("documents") or [[]])[0]
        distances = (results.get("distances") or [[]])[0]
        if not documents:
            return []

        threshold = AgentConfig.RAG_SCORE_THRESHOLD
        filtered: List[str] = []
        for index, doc in enumerate(documents):
            if not distances:
                filtered.append(doc)
                continue
            distance = distances[index] if index < len(distances) else None
            score = 1 - float(distance) if distance is not None else 0.0
            if score >= threshold:
                filtered.append(doc)

        return filtered

    # 兼容旧命名
    def rag_query_tok_k(self, query: str, user_id: str, rag_top_k: Optional[int] = None) -> List[str]:
        return self.rag_query_top_k(query=query, user_id=user_id, rag_top_k=rag_top_k)

    def summarize_and_store_knowledge(self, user_id: str, content: str):
        if not content or content.upper() == "NONE":
            return

        print(f"\n--- [系统自动提炼新记忆] {content} ---")

        self.collection.add(
            documents=[content],
            metadatas=[{"category": "AUTO_EXTRACTED", "user_id": user_id}],
            ids=[str(uuid.uuid4())],
        )

        lock_id = f"data_lock_{user_id}"
        self.collection.upsert(
            ids=[lock_id],
            documents=["HASH_LOCK_MARKER"],
            metadatas=[{"hash_lock": "FORCE_UPDATE_STALE", "user_id": user_id}],
        )

    def close(self):
        # ChromaDB Python 客户端当前无需显式 close，保留占位供后续扩展。
        return


_global_memory_instance = None


def get_long_term_memory():
    global _global_memory_instance
    if _global_memory_instance is None:
        _global_memory_instance = LongTermMemory()
    return _global_memory_instance
