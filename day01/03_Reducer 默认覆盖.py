"""
LangGraph Reducer函数演示 - 默认Reducer（覆盖更新）
"""

from typing import List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 1. Reducer 默认覆盖
class DefaultReducerState(TypedDict):
    foo: int
    bar: List[str]

def node_default_1(state: DefaultReducerState) -> dict:
    return {"foo": 2}

def node_default_2(state: DefaultReducerState) -> dict:
    return {"bar": ["bye"]}

def run_demo():
    print("1. 默认Reducer（覆盖更新）演示:")
    builder = StateGraph(DefaultReducerState)
    builder.add_node(node_default_1)
    builder.add_node(node_default_2)
    builder.add_edge(START, "node_default_1")
    builder.add_edge(START, "node_default_2")
    builder.add_edge("node_default_1", "node_default_2")
    builder.add_edge("node_default_2", END)
    graph = builder.compile()

    result = graph.invoke({
        "foo": 1,
        "bar": ['hi']
    })
    print(f"执行结果：{result}")


if __name__ == '__main__':
    run_demo()