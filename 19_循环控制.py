from typing import Literal, Dict, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.errors import GraphRecursionError

class LoopState(TypedDict):
    count: int
    result: str
    max_count: int

def node_a(state: LoopState) -> dict:
    """
        节点a：处理逻辑并更新计数
    """
    print(f"执行节点a，当前计数: {state['count']}")
    return {
        "count": state['count'] + 1,
        "result": f"已经处理 {state['count'] + 1} 次 —— 主要处理"
    }

def node_b(state: LoopState) -> dict:
    """
        节点b：辅助处理
    """
    print(f"执行节点b，当前计数: {state['count']}")
    return {
        "result": f"已经处理 {state['count']} 次 —— 辅助处理"
    }

def route(state: LoopState) -> Literal["node_b", END]:
    # 终止条件，达到最大计数则结束
    if state['count'] >= state['max_count']:
        print(f"满足终止条件，计数 {state['count']} >= {state['max_count']}，返回END")
        return END

    print(f"未满足终止条件，计数 {state['count']} < {state['max_count']}，返回b")
    return "node_b"

def run_demo():
    builder = StateGraph(LoopState)

    builder.add_node(node_a)
    builder.add_node(node_b)

    builder.add_edge(START, "node_a")

    builder.add_conditional_edges("node_a", route)
    builder.add_edge("node_b", "node_a")

    graph = builder.compile()

    # 执行图
    print("=== 开始执行工作流 ===")

    try:
        result = graph.invoke({
            "count": 0,
            "result": "",
            "max_count": 3
        }, config= {
            "recursion_limit": 6 # 设置递归限制
        })
        print("=== 执行结果 ===")
        print(result)
    except GraphRecursionError as e:
        print(f"递归错误:{e}\n")

if __name__ == '__main__':
    run_demo()