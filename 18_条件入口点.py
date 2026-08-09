"""
LangGraph条件入口点演示

条件入口点允许根据输入状态动态决定从哪个节点开始执行。
"""

from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 定义状态
class State(TypedDict):
    value: int
    tep: str

# 定义节点函数
def node_a(state: State) -> dict:
    """节点A"""
    print("执行节点A")
    return {"value": state["value"] + 1, "step": "A执行完毕"}

def node_b(state: State) -> dict:
    """节点B"""
    print("执行节点B")
    return {"value": state["value"] + 1, "step": "B执行完毕"}

def node_c(state: State) -> dict:
    """节点C"""
    print("执行节点C")
    return {"value": state["value"] + 1, "step": "C执行完毕"}

# 条件入口点的路由函数
def entry_condition(state: State) -> Literal["node_b", "node_c"]:
    """根据输入值决定从哪个节点开始"""
    if state.get("value", 0) > 5:
        return "node_b_alias"
    return "node_c_alias"

def run_demo():
    """演示条件入口点"""
    print("=== 条件入口点演示 ===")

    builder = StateGraph(State)

    builder.add_node(node_a)
    builder.add_node(node_b)
    builder.add_node(node_c)

    builder.add_conditional_edges(START, entry_condition, {
        "node_b_alias": "node_b",
        "node_c_alias": "node_c"
    })

    builder.add_edge("node_b", "node_a")
    builder.add_edge("node_c", "node_a")
    builder.add_edge("node_a", END)

    graph = builder.compile()

    # 执行图 - >5
    print("输入值 >5:")
    result = graph.invoke({"value": 10})
    print(f"执行结果: {result}")

    # 执行图 - <5
    print("\n输入值 <5:")
    result = graph.invoke({"value": 1})
    print(f"执行结果: {result}\n")

if __name__ == '__main__':
    run_demo()