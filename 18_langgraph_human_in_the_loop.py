import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


@tool
def get_weather(city: str) -> str:
    """查询指定城市当前的天气情况。"""
    fake_weather_db = {"北京": "晴，25°C", "上海": "多云，28°C"}
    return fake_weather_db.get(city, f"暂无 {city} 的天气数据")


@tool
def add(a: float, b: float) -> float:
    """计算两个数字相加的结果。"""
    return a + b


tools = [get_weather, add]
tools_by_name = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State) -> State:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def tool_executor(state: State) -> State:
    last_message = state["messages"][-1]
    results = []
    for call in last_message.tool_calls:
        # 执行工具之前，先暂停下来，把决定权交给人
        approved = interrupt(
            {"question": f"模型想调用工具 {call['name']}，参数 {call['args']}，是否允许？(yes/no)"}
        )
        if approved == "yes":
            output = tools_by_name[call["name"]].invoke(call)
        else:
            output = ToolMessage(content="用户拒绝了这次工具调用。", tool_call_id=call["id"])
        results.append(output)
    return {"messages": results}


def should_continue(state: State) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_executor)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", should_continue, {"tools": "tools", END: END})
graph_builder.add_edge("tools", "chatbot")

# interrupt/resume 依赖 checkpointer 来保存“暂停时”的状态
graph = graph_builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "approval-demo"}}

result = graph.invoke({"messages": [("human", "北京天气怎么样？")]}, config=config)

# 只要图还在等待人工确认，就一直循环：问 -> 收到答案 -> 恢复执行
while "__interrupt__" in result:
    question = result["__interrupt__"][0].value["question"]
    answer = input(f"[需要人工确认] {question} ")
    result = graph.invoke(Command(resume=answer), config=config)

for m in result["messages"]:
    m.pretty_print()
