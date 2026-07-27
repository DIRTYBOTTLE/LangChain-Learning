import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
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

graph = graph_builder.compile(checkpointer=InMemorySaver())

# 同一个 thread_id：图会自动记住这个会话的历史，每轮只需要传新消息
config = {"configurable": {"thread_id": "xiaoming-1"}}

result = graph.invoke({"messages": [("human", "我叫小明，最喜欢的水果是芒果。")]}, config=config)
print("助手：", result["messages"][-1].content)

result = graph.invoke({"messages": [("human", "你还记得我的名字和喜欢的水果吗？")]}, config=config)
print("助手：", result["messages"][-1].content)

# 换一个 thread_id：全新的、互相隔离的会话，不会共享上面的历史
other_config = {"configurable": {"thread_id": "someone-else"}}
result = graph.invoke({"messages": [("human", "你还记得我的名字吗？")]}, config=other_config)
print("\n另一个会话的助手：", result["messages"][-1].content)
