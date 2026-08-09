"""
LangGraph 延迟节点执行演示

本示例展示了如何使用defer=True来实现节点延迟执行，确保该节点等待所有其他并行分支任务完成后才执行。
"""

import operator
from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    """
        状态类型定义
        aggregate: 使用operator.add reducer使这个列表为追加模式，确保每个节点的结果都能被正确合并
    """
    aggregate: Annotated[list, operator.add]

def node_a(state: State):
    """
        节点 a 启动分支
    Returns:
            包含新结果的状态更新
    """
    print(f"Adding A to {state['aggregate']}")
    return {"aggregate": ["A"]}

def node_b(state:State):
    """
        节点 b ：第一个分支
        此节点处理第一个分支的任务，与节点c并行执行。
    """
    print(f"Adding B to {state['aggregate']}")
    return {"aggregate": ["B"]}

def node_b2(state: State):
    """
        节点 b_2 ：与节点 b 同一条执行线上
        节点 b 完成后执行
    """
    print(f"Adding B_2 to {state['aggregate']}")
    return {"aggregate": ["B_2"]}

def node_c(state: State):
    """
        节点 c ：与节点 b 并行执行
    """
    print(f"Adding C to {state['aggregate']}")
    return {"aggregate": ["C"]}

def node_d(state: State):
    """
        节点d：延迟执行的汇总节点
        此节点设置了defer = True，因此会等待所有其他任务完成后才执行。
        它负责汇总所有分支的结果
    """
    print(f"Adding D to {state['aggregate']}")
    return {"aggregate": ["D"]}

# 创建图
builder = StateGraph(State)

builder.add_node(node_a)
builder.add_node(node_b)
builder.add_node(node_b2)
builder.add_node(node_c)
builder.add_node(node_d, defer=True) # 延迟，等其他节点完成，再执行

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_a", "node_c")

builder.add_edge("node_b", "node_b2")

builder.add_edge("node_b2", "node_d")
builder.add_edge("node_c", "node_d")

builder.add_edge("node_d", END)

graph = builder.compile()

result = graph.invoke({"aggregate": []})
print(result)