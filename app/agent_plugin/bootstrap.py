from __future__ import annotations

import logging
from pathlib import Path
from threading import Lock

from app.core.config import GlobalConfig
from app.agent_plugin.agent.config import AgentConfig


_INIT_LOCK = Lock()
_IS_INITIALIZED = False
logger = logging.getLogger(__name__)


def ensure_agent_plugin_configured(force: bool = False) -> None:
    global _IS_INITIALIZED
    if _IS_INITIALIZED and not force:
        return

    with _INIT_LOCK:
        if _IS_INITIALIZED and not force:
            return

        embedding_model = str(GlobalConfig.AGENT_PLUGIN_EMBEDDING_MODEL)
        embedding_path = Path(embedding_model)
        if (
            embedding_model
            and ("/" in embedding_model or "\\" in embedding_model)
            and not embedding_path.exists()
        ):
            logger.warning(
                "AgentPlugin 本地 embedding 模型路径不存在: %s",
                embedding_model,
            )

        AgentConfig.setup(
            BASE_DATA_DIR=str(GlobalConfig.AGENT_DATA_DIR),
            VECTOR_DB_PATH=GlobalConfig.AGENT_VECTOR_DB_DIRNAME,
            RELATIONAL_DB_PATH=str(GlobalConfig.DB_PATH),
            EMBEDDING_MODEL=embedding_model,
            COLLECTION_NAME=GlobalConfig.AGENT_PLUGIN_COLLECTION_NAME,
            RAG_RAW_FILE_PATH=GlobalConfig.AGENT_PLUGIN_RAG_RAW_FILE_PATH,
            RAG_CHUNK_SIZE=GlobalConfig.AGENT_PLUGIN_RAG_CHUNK_SIZE,
            RAG_METADATA_EXTRAS=GlobalConfig.AGENT_PLUGIN_RAG_METADATA_EXTRAS,
            RAG_FORCE_UPDATE=GlobalConfig.AGENT_PLUGIN_RAG_FORCE_UPDATE,
            RAG_TOP_K=GlobalConfig.AGENT_PLUGIN_RAG_TOP_K,
            RAG_SCORE_THRESHOLD=GlobalConfig.AGENT_PLUGIN_RAG_SCORE_THRESHOLD,
            LLM_MODEL=GlobalConfig.LLM_MODEL,
            LLM_API_KEY=GlobalConfig.LLM_API_KEY,
            LLM_URL_BASE=GlobalConfig.LLM_BASE_URL,
            LLM_TEMPERATURE=GlobalConfig.LLM_TEMPERATURE,
            LLM_TIMEOUT=GlobalConfig.LLM_TIMEOUT,
            SYSTEM_PROMPT=GlobalConfig.AGENT_PLUGIN_SYSTEM_PROMPT,
        )
        _IS_INITIALIZED = True
