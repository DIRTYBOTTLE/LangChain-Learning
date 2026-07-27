import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State) -> State:
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

# 第一轮
result = graph.invoke({"messages": [("human", "我叫小明，最喜欢的水果是芒果。")]})
for m in result["messages"]:
    m.pretty_print()

# 第二轮：把上一轮返回的完整 messages 原样传回去，reducer 会自动把新消息追加进去
result = graph.invoke({"messages": result["messages"] + [("human", "你还记得我的名字和喜欢的水果吗？")]})
for m in result["messages"]:
    m.pretty_print()
