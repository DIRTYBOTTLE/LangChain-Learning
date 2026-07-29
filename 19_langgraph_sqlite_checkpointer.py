import os
from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
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

# 数据库放在脚本同级目录；它被 .gitignore 忽略，不会提交到仓库。
database_path = Path(__file__).with_name("checkpoints.sqlite")

# 用完后关闭连接，避免 Windows 上数据库文件一直被占用。
with SqliteSaver.from_conn_string(str(database_path)) as checkpointer:
    graph = graph_builder.compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "xiaoming-sqlite"}}

    # 第一次运行时会创建数据库；以后重新运行脚本时，下面这轮仍能读取历史。
    result = graph.invoke(
        {"messages": [("human", "我叫小明，最喜欢的水果是芒果。")]},
        config=config,
    )
    print("助手：", result["messages"][-1].content)

    result = graph.invoke(
        {"messages": [("human", "你还记得我的名字和喜欢的水果吗？")]},
        config=config,
    )
    print("助手：", result["messages"][-1].content)
