"""
LangGraph Reducer函数演示 - 字符串连接Reducer
"""

import operator
from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 6. 字符串连接Reducer
class StringContextState(TypedDict):
    text: Annotated[str, operator.add]

def producer_1(state: StringContextState) -> dict:
    return {
        "text": "hello"
    }

def producer_2(state: StringContextState) -> dict:
    return {
        "text": " world!"
    }

def run_demo():
    print("6. operator.add Reducer（字符串连接）演示:")
    builder = StateGraph(StringContextState)
    builder.add_node("producer_1", producer_1)
    builder.add_node("producer_2", producer_2)
    builder.add_edge(START, "producer_1")
    builder.add_edge("producer_1", "producer_2") # 两个阶段并行执行或者连接最终结果是一样的
    # builder.add_edge("producer_1", END)
    builder.add_edge("producer_2", END)
    graph = builder.compile()

    result = graph.invoke({
        "text": "你好，"
    })
    print(f"初始状态:{{'text': '你好,'}}")
    print(f"执行结果：{result}")

if __name__ == '__main__':
    run_demo()