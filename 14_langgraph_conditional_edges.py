from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    count: int


def double(state: State) -> State:
    print(f"double 执行前：{state['count']}")
    return {"count": state["count"] * 2}


def should_continue(state: State) -> str:
    if state["count"] < 100:
        return "double"
    return END


graph_builder = StateGraph(State)
graph_builder.add_node("double", double)
graph_builder.add_edge(START, "double")
graph_builder.add_conditional_edges("double", should_continue, {"double": "double", END: END})

graph = graph_builder.compile()

result = graph.invoke({"count": 1})
print("最终结果：", result)
