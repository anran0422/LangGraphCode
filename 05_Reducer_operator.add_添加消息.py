"""
LangGraph Reducer函数演示 - operator.add Reducer（列表追加）
"""

import operator
from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 3. operator.add Reducer（列表追加）
class ListAddState(TypedDict):
    data: Annotated[List[int], operator.add]

def producer_1(state: ListAddState) -> dict:
    return {
        "data": [1,2]
    }

def producer_2(state: ListAddState) -> dict:
    return {
        "data": [3,4]
    }

def run_demo():
    print("5. operator.add Reducer（列表追加）演示:")
    builder = StateGraph(ListAddState)
    builder.add_node("producer_1", producer_1)
    builder.add_node("producer_2", producer_2)
    builder.add_edge(START, "producer_1")
    builder.add_edge("producer_1", "producer_2") # 两个阶段并行执行或者连接最终结果是一样的
    # builder.add_edge("producer_1", END)
    builder.add_edge("producer_2", END)
    graph = builder.compile()

    result = graph.invoke({
        "data": [0]
    })
    print(f"初始状态:{{'data': [0]}}")
    print(f"执行结果：{result}")

if __name__ == '__main__':
    run_demo()