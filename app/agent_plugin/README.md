# agent_plugin

一个可复用的 Agent 通用插件，基于 LangGraph，提供：

- 短期记忆：`SqliteSaver`（按 `thread_id` 持久化对话）
- 长期记忆：ChromaDB 向量检索
- 工具扩展：在 `agent/tools.py` 中注册 `@tool`
- SSE 流式输出：`AgentCore.stream_run()`

关系型存储（checkpoint/会话状态）复用项目全局 `database.db`，不再单独创建 `agent_plugin.db`。

## 配置方式

插件配置不再单独维护，统一由项目 `app/core/config.py` 的 `GlobalConfig` 管理，
并通过 `app/agent_plugin/bootstrap.py::ensure_agent_plugin_configured()` 注入。

## 关键环境变量

```env
AGENT_PLUGIN_ENABLED=true
AGENT_PLUGIN_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
AGENT_PLUGIN_COLLECTION_NAME=agent_plugin_memory
AGENT_PLUGIN_RAG_CHUNK_SIZE=500
AGENT_PLUGIN_RAG_METADATA_EXTRAS=category,source
AGENT_PLUGIN_RAG_FORCE_UPDATE=false
AGENT_PLUGIN_RAG_TOP_K=5
AGENT_PLUGIN_RAG_SCORE_THRESHOLD=0.7
AGENT_PLUGIN_SYSTEM_PROMPT=你是一个具备自主能力的 AI 助手。请在必要时调用工具，并给出准确、简洁、可执行的答案。
```

## 工具开发规范

- 使用 `@tool` 装饰器
- docstring 要准确描述调用场景
- 访问长期记忆必须走 `get_long_term_memory()`
- 检索时必须传入 `user_id`，禁止硬编码

## 接口

- Agent 内核：`AgentCore`
- 长期记忆：`LongTermMemory`

## 安全注意

文档和配置中不要出现真实 API Key。示例请统一使用占位符（如 `sk-xxxxx`）。

