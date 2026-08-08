"""
LangGraph 图输入输出模式和私有状态传递演示

该演示展示了：
1. 如何定义图的输入和输出模式
2. 如何在节点间传递私有状态
"""

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

# 定义输入状态模式
class InputState(TypedDict):
    question: str


# 定义输出状态模式
class OutputState(TypedDict):
    answer: str

# 定义整体状态模式，结合输入和输出
class OverallState(InputState, OutputState):
    pass

# 定义处理节点
def answer_node(state: InputState):
    """
        处理输入并生产答案的节点
    :param state:
    :return: 包含答案的字典
    """
    print(f"执行 answer_node 节点：")
    print(f"输入：{state}")

    # 示例答案
    answer = "再见" if "bye" in state["question"].lower() else "你好"
    result = {
        "answer": answer,
        "question": state["question"]
    }
    print(f"输出：{result}")
    return result

# 定义整体状态（这是在节点之前共享的公共状态）
class OverallStatePrivate(TypedDict):
    a: str

# node_1 的输出包含不属于整体状态的私有数据
class Node1Output(TypedDict):
    private_date: str

# 私有数据仅在node_1 和 node_2 之间传递
def node_1(state: OverallStatePrivate) -> Node1Output:
    """
        第一个节点，生成私有状态
    :param state: 整体状态
    :return: 包含私有数据的字典
    """
    output = {
        "private_data": "由 node_1 设置"
    }
    print(f"进入 node_1 节点")
    print(f"输入: {state}")
    print(f"输出：{output}")
    return output

# 节点2 的输出只请求 node_1 之后可用的私有数据
class Node2Input(TypedDict):
    private_data: str

def node_2(state:Node2Input) -> OverallStatePrivate:
    """
        第二个节点可以访问 node_1 的私有数据
    Args:
        state: 包含私有数据的输入状态

    Returns:
        dict: 更新的整体状态
    """
    output = {
        "a": "由 node_2 设置"
    }
    print(f"进入 node_2 节点")
    print(f"输入：{state}")
    print(f"输出：{output}")
    return output

# 节点3 只能访问整体状态（无法访问 node_1 的私有数据）
def node_3(state:OverallStatePrivate) ->OverallStatePrivate:
    """
        第三个节点，只能访问整体状态
    Args:
        state: 整体状态

    Returns:
        dict: 更新的整体状态
    """
    output = {
        "a": "由 node_3 设置"
    }
    print(f"进入 node_3 节点")
    print(f"输入：{state}")
    print(f"输出：{output}")
    return output

def demo_input_schema():
    """
        演示输入输出模式
    """
    print("=== 演示输入输出模式 ===")

    # 使用指定的输入和输出模式构建图
    builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
    builder.add_node("answer_node", answer_node) # 添加答案节点
    builder.add_edge(START, "answer_node") # 添加起始边
    builder.add_edge("answer_node", END) # 添加结束边

    graph = builder.compile()
    # 使用输入调用图并调用结果
    result = graph.invoke({
        "question": "你好"
    })
    print(f"图调用结果：{result}")

    print()

def demo_private_state():
    """
        演示私有状态传递
    """
    print("=== 演示私有状态传递 ===")

    # 连接节点序列
    # node_2 接受来自 node_1 的私有数据
    # 但是 node_3 看不到来自 node_1 的私有数据
    builder = StateGraph(OverallStatePrivate).add_sequence([node_1, node_2, node_3])
    builder.add_edge(START, "node_1")
    graph = builder.compile()

    # 使用初始状态调用图
    response = graph.invoke({
        "a": "在开始时候设置"
    })
    print()
    print(f"图调用的输出: {response}")
    print()

def main():
    """
        主函数
    """
    print("=== LangGraph 图输入输出模式和私有状态传递演示 === \n")

    # 演示输入输出模式
    demo_input_schema()

    # 演示私有状态船体
    demo_private_state()

    print("=== 演示完成 ===")

if __name__ == '__main__':
    main()