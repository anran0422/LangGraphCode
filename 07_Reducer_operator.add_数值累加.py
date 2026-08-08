"""
LangGraph Reducer函数演示 - 数值累加Reducer
"""

import operator
from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 7. 数值累加Reducer
class NumberAddState(TypedDict):
    count: Annotated[int, operator.add]

def producer_1(state: NumberAddState) -> dict:
    return {
        "count": 5
    }

def producer_2(state: NumberAddState) -> dict:
    return {
        "count": 10
    }

def run_demo():
    print("7. operator.add Reducer（数值累加）演示:")
    builder = StateGraph(NumberAddState)
    builder.add_node("producer_1", producer_1)
    builder.add_node("producer_2", producer_2)
    builder.add_edge(START, "producer_1")
    builder.add_edge("producer_1", "producer_2") # 两个阶段并行执行或者连接最终结果是一样的
    # builder.add_edge("producer_1", END)
    builder.add_edge("producer_2", END)
    graph = builder.compile()

    result = graph.invoke({
        "count": 0
    })
    print(f"初始状态:{{'count': 0}}")
    print(f"执行结果：{result}")

if __name__ == '__main__':
    run_demo()