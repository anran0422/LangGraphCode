"""
LangGraph条件边演示

条件边根据当前状态动态决定下一个要执行的节点。
"""
from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    value: int
    step: str

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

# 条件边路由函数
def route_condition(state: State)-> Literal['node_b', 'node_c']:
    # 根据 value 决定走哪条路
    if state['value'] % 2 == 0:
        return "node_b_alias"
    return "node_c_alias"

def run_demo():
    """演示条件边"""
    print("=== 条件边演示 ===")

    builder = StateGraph(State)

    builder.add_node(node_a)
    builder.add_node(node_b)
    builder.add_node(node_c)

    # 入口点
    builder.add_edge(START, "node_a")

    # 添加条件边
    builder.add_conditional_edges("node_a", route_condition, {
        "node_b_alias": "node_b", # 映射到真实节点
        "node_c_alias": "node_c"
    })

    builder.add_edge("node_b", END)
    builder.add_edge("node_c", END)

    graph = builder.compile()

    # 执行图 - 偶数情况
    print("输入值为偶数:")
    result = graph.invoke({"value": 2})
    print(f"执行结果: {result}")

    # 执行图 - 奇数情况
    print("\n输入值为奇数:")
    result = graph.invoke({"value": 1})
    print(f"执行结果: {result}\n")

if __name__ == "__main__":
    run_demo()