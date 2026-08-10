"""
LangGraph Map-Reduce 模式演示

演示如何使用 Send 对象实现 map-reduce 设计模式。
在这种模式中，第一个节点生成一个对象列表，
然后将其他节点应用于所有这些对象。
"""

"""
OverallState 是图维护的共享状态
而 Send("node", {...}) 的第二个参数是为某一次目标节点执行临时构造的输入 State
它可以与 OverallState 不同。

class JokeState(TypedDict):
    subject: str

def make_jokes(state: JokeState):

这样就跟你前面学的 “每个节点可以有自己的 Input State Schema” 完全串起来了。
"""


import operator
from typing import Annotated, List, Sequence
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

class OverallState(TypedDict):
    subjects: List[str]
    jokes: Annotated[List[str], operator.add] # lambda x,y: x + y

# 生成需要处理的主题列表
def generate_subjects(state: OverallState) -> dict:
    """生成需要处理的主题列表"""
    print("执行节点: generate_subjects")
    subjects = ['猫', '狗', '程序员']
    print(f"生成主题列表: {subjects}")
    return {"subjects": subjects}

# Map节点：为每个主题生成笑话
def make_jokes(state: OverallState) -> dict:
    """为单个主题生成笑话"""
    subject = state.get("subject", "未知")
    print(f"执行节点: make_joke，处理主题: {subject}")
    # 根据主题生成相应笑话
    jokes_map = {
        "猫": "为什么猫不喜欢在线购物？因为它们更喜欢实体店！",
        "狗": "为什么狗不喜欢计算机？因为它们害怕被鼠标咬！",
        "程序员": "为什么程序员喜欢洗衣服？因为他们在寻找bugs！",
        "未知": "这是一个关于未知主题的神秘笑话。"
    }

    joke = jokes_map.get(subject, f"这是一个关于{subject}的即兴笑话")
    print(f"生成笑话: {joke}")
    return {"jokes": [joke]}

# 条件边函数：根据主题列表生成Send对象列表
def map_subjects_to_jokes(state: OverallState) -> Sequence[Send]:
    """将主题列表映射到joke生成任务"""
    print("执行条件边函数: map_subjects_to_jokes")
    subjects = state.get("subjects")
    print(f"映射主题到joke任务: {subjects}")

    # 为每个主题创建一个Send对象，指向make_joke节点
    # 每个Send对象包含节点名称和传递给该节点的状态
    send_list = [Send("make_jokes", {"subject": subject}) for subject in subjects]
    print(f"生成Send对象列表: {send_list}")
    return send_list

def main():
    """演示Map-Reduce模式"""
    print("=== Map-Reduce 模式演示 ===\n")

    builder = StateGraph(OverallState)

    builder.add_node(generate_subjects)
    builder.add_node(make_jokes)

    builder.add_edge(START, "generate_subjects")
    builder.add_conditional_edges("generate_subjects", map_subjects_to_jokes)
    builder.add_edge("make_jokes", END)

    graph = builder.compile()
    # 执行图
    initial_state = {"subjects": [], "jokes": []}
    print("初始状态:", initial_state)
    print("\n开始执行图...")

    result = graph.invoke(initial_state)
    print(f"\n最终结果: {result}")

    print("\n=== 演示完成 ===")

if __name__ == '__main__':
    main()