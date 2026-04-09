import json
import sqlite3
from typing import Annotated, TypedDict, Any, Generator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.state import CompiledStateGraph

from app.agent_plugin.agent.config import AgentConfig
from app.agent_plugin.agent.memory import LongTermMemory, get_long_term_memory
from app.agent_plugin.agent.tools import tools, tool_node


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str


class AgentCore:
    model: Any
    memory_engine: LongTermMemory
    workflow: StateGraph
    conn: sqlite3.Connection
    saver: SqliteSaver
    app: CompiledStateGraph

    def __init__(self):
        self.memory_engine = get_long_term_memory()

        self.model = ChatOpenAI(
            model=AgentConfig.LLM_MODEL,
            api_key=AgentConfig.LLM_API_KEY,
            base_url=AgentConfig.LLM_URL_BASE,
            temperature=AgentConfig.LLM_TEMPERATURE,
            timeout=AgentConfig.LLM_TIMEOUT,
        ).bind_tools(tools)

        self.workflow = StateGraph(AgentState)
        self.workflow.add_node("agent", self._call_model)
        self.workflow.add_node("action", tool_node)
        self.workflow.add_node("summarize", self._summarize_and_store)
        self.workflow.set_entry_point("agent")
        self.workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            path_map={"tools": "action", "summarize": "summarize"},
        )
        self.workflow.add_edge("action", "agent")
        self.workflow.add_edge("summarize", END)

        self.conn = sqlite3.connect(AgentConfig.RELATIONAL_DB_PATH, check_same_thread=False)
        self.saver = SqliteSaver(self.conn)
        self.app = self.workflow.compile(checkpointer=self.saver)

    def _inject_runtime_args(self, state: AgentState, response: Any) -> Any:
        tool_calls = getattr(response, "tool_calls", []) or []
        for tc in tool_calls:
            if tc.get("name") != "query_long_term_memory":
                continue
            args = tc.get("args")
            if not isinstance(args, dict):
                args = {}
                tc["args"] = args
            args.setdefault("user_id", state["user_id"])
        return response

    def _call_model(self, state: AgentState):
        system_msg = SystemMessage(content=AgentConfig.SYSTEM_PROMPT)
        response = self.model.invoke([system_msg] + state["messages"])
        response = self._inject_runtime_args(state, response)
        return {"messages": [response]}

    def _should_continue(self, state: AgentState):
        last_message = state["messages"][-1]
        return "tools" if getattr(last_message, "tool_calls", None) else "summarize"

    def _summarize_and_store(self, state: AgentState):
        summary_prompt = SystemMessage(
            content="分析对话，提取 1-2 条关于用户的新信息（偏好/习惯/背景）。若无新增信息，仅回复 NONE。"
        )

        response = self.model.invoke([summary_prompt] + state["messages"])
        content = (response.content or "").strip()

        self.memory_engine.summarize_and_store_knowledge(
            user_id=state["user_id"],
            content=content,
        )

        return {}

    def stream_run(self, prompt: str, user_id: str, thread_id: str) -> Generator[str, None, None]:
        """
        同步生成器：驱动图运行并输出 SSE 数据流。
        """
        inputs = {
            "messages": [HumanMessage(content=prompt)],
            "user_id": user_id,
        }
        config = {"configurable": {"thread_id": thread_id}}

        print(f"\n{'=' * 20} 任务开始 (Thread: {thread_id}) {'=' * 20}")
        print(f"[用户输入]: {prompt}")

        for event in self.app.stream(inputs, config=config, stream_mode="updates"):
            for node_name, state_update in event.items():
                if state_update is None:
                    continue

                print(f"\n>>> [动作追踪] 进入节点 <{node_name}>")

                if "messages" not in state_update:
                    continue

                last_msg = state_update["messages"][-1]

                if node_name == "agent":
                    if getattr(last_msg, "tool_calls", None):
                        for tc in last_msg.tool_calls:
                            print(f"--- [内核决策] 调用工具 [{tc['name']}]")
                    if last_msg.content:
                        print(f"[内核回复]: {last_msg.content}")
                elif node_name == "action":
                    print("--- [系统执行] 工具执行完毕，结果已写回上下文")
                elif node_name == "summarize":
                    print("--- [知识复盘] 正在提炼并归档新记忆")

                payload = {
                    "node": node_name,
                    "user_id": user_id,
                    "content": last_msg.content if last_msg.content else "",
                    "tool_calls": [
                        {"name": tc["name"], "args": tc["args"]}
                        for tc in getattr(last_msg, "tool_calls", [])
                    ]
                    if hasattr(last_msg, "tool_calls")
                    else [],
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        print(f"\n{'=' * 20} 任务结束 {'=' * 20}")
        yield "data: [DONE]\n\n"

    def close(self):
        if self.conn:
            self.conn.close()
