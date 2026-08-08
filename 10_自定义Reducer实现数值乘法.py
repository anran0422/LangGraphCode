"""
LangGraph Reducer函数演示 - 自定义 mul reducer 实现数值相乘
使用全局变量区分初始化调用和正常调用
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 使用全局变量来跟踪是否是第一次调用（初始化阶段）
_is_first_call = True


# _is_first_call 的作用
# 就是让第一次 Reducer 调用时忽略 current_value；
# 没有它，第一次也会拿 current_value 正常参与乘法。
def my_mul_reducer(current_value: float, new_value: float) -> float:
    """
        自定义乘法reducer，使用全局变量区分初始化调用和正常调用
    Args:
        current_value: 当前状态值
        new_value: 新值

    Returns:
        计算后的结果ƒ
    """
    global _is_first_call
    print(f"Reducer 被调用: current_value = {current_value}, new_value = {new_value}, _is_first_call = {_is_first_call}")

    # 如果是初始化调用，直接返回new_value，避免默认值0的影响
    if _is_first_call:
        _is_first_call = False
        return new_value
    # 正常的乘法操作，包括乘以0的情况
    return current_value * new_value


class MultiReducerState(TypedDict):
    factor: Annotated[float, my_mul_reducer]

def multiply_two(state: MultiReducerState) -> dict:
    return {"factor": 2.0}

def multiply_zero(state: MultiReducerState) -> dict:
    return {"factor": 0.0}


def run_demo():
    """
        演示增强版乘法reducer的使用
    """
    global _is_first_call
    print("=== operator.mul 增强版解决方案演示 ===\n")

    # 演示1: 正常乘法操作
    print("1. 正常乘法操作演示:")
    _is_first_call = True # 重置初始化标志
    builder = StateGraph(MultiReducerState)
    builder.add_node(multiply_two)
    builder.add_edge(START, "multiply_two")
    builder.add_edge("multiply_two", END)
    graph = builder.compile()

    result = graph.invoke({
        "factor": 5.0
    })
    print(f"初始状态: {{'factor': 5.0}}")
    print(f"预期结果: 10.0 (5.0 * 2.0)\n")
    print(f"执行结果: {result}\n")

    # 演示2: 乘以0的操作
    print("2. 乘以0的操作演示:")
    _is_first_call = True # 重置初始化标志

    builder2 = StateGraph(MultiReducerState)
    builder2.add_node(multiply_zero)
    builder2.add_edge(START, "multiply_zero")
    builder2.add_edge("multiply_zero", END)
    graph2 = builder2.compile()

    result2 = graph2.invoke({
        "factor": 5.0
    })
    print(f"初始状态: {{'factor': 5.0}}")
    print(f"预期结果: 0.0 (5.0 * 0.0)\n")
    print(f"执行结果: {result2}\n")

    # 演示3: 连续乘法操作
    print("3. 连续乘法操作演示:")
    _is_first_call = True  # 重置初始化标志

    builder3 = StateGraph(MultiReducerState)
    builder3.add_node("multiply_two_1", multiply_two)
    builder3.add_node("multiply_zero", multiply_zero)
    builder3.add_node("multiply_two_2", multiply_two)

    builder3.add_edge(START, "multiply_two_1")
    builder3.add_edge("multiply_two_1", "multiply_zero")
    builder3.add_edge("multiply_zero", "multiply_two_2")
    builder3.add_edge("multiply_two_2", END)

    graph3 = builder3.compile()

    result3 = graph3.invoke({
        "factor": 5.0
    })
    print(f"初始状态: {{'factor': 5.0}}")
    print(f"预期结果: 5.0 -> 10.0 -> 0.0 -> 0.0\n")
    print(f"执行结果: {result3}\n")


if __name__ == '__main__':
    run_demo()