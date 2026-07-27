from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    count: int


def add_one(state: State) -> State:
    return {"count": state["count"] + 1}


def double(state: State) -> State:
    return {"count": state["count"] * 2}


graph_builder = StateGraph(State)
graph_builder.add_node("add_one", add_one)
graph_builder.add_node("double", double)
graph_builder.add_edge(START, "add_one")
graph_builder.add_edge("add_one", "double")
graph_builder.add_edge("double", END)

graph = graph_builder.compile()

print(graph.get_graph().draw_ascii())

result = graph.invoke({"count": 1})
print("最终结果：", result)
