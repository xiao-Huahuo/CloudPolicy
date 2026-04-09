from pathlib import Path

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from app.agent_plugin.agent.memory import get_long_term_memory


@tool
def query_long_term_memory(query: str, user_id: str):
    """当需要检索用户长期记忆（偏好、背景、历史事实）时调用。"""
    long_term_memory = get_long_term_memory()
    results = long_term_memory.rag_query_top_k(query=query, user_id=user_id)
    context = "\n".join(results) if results else "未找到相关记忆。"
    return f"【长期记忆检索结果】\n{context}"


@tool
def parse_local_file(file_name: str):
    """读取本地文本文件内容（受项目目录约束）并返回前 3000 字符。"""
    candidate = Path(file_name)
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate

    candidate = candidate.resolve()
    root = Path.cwd().resolve()
    if root not in candidate.parents and candidate != root:
        return "【文件解析结果】文件路径不在当前项目目录下，拒绝读取。"

    if not candidate.exists() or not candidate.is_file():
        return f"【文件解析结果】未找到文件: {candidate}"

    if candidate.suffix.lower() not in {".txt", ".md", ".json", ".log", ".py", ".yaml", ".yml"}:
        return f"【文件解析结果】暂不支持该类型: {candidate.suffix}"

    try:
        content = candidate.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return f"【文件解析结果】读取失败: {exc}"

    return f"【文件解析结果】\n{content[:3000]}"


tools = [query_long_term_memory, parse_local_file]
tool_node = ToolNode(tools)
