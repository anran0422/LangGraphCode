"""
LangGraph Command 基础演示

演示如何在节点中使用 Command 对象同时更新状态和控制流程。
"""

from typing import Annotated, Literal
from typing import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.types import Command
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    current_agent: str
    is_task_completed: bool

def node_decision_agent(state: AgentState) -> Command[Literal["node_math_agent", "node_translation_agent", "__end__"]]:
    """决策代理节点，根据消息内容决定下一步操作"""
    print("执行节点: decision_agent")
    # 检查最新的消息
    role, content = state["messages"][-1]
    # last_message = state["messages"][-1] if state["messages"] else ""
    print(f"最新消息: {content}")

    # 根据消息内容决定下一步
    if "数学" in content:
        # 更新状态并跳转到数学代理
        return Command(
            update={
                "messages": [("system", "路由到数学代理")],
                "current_agent": "node_math_agent"
            },
            goto="node_math_agent"
        )
    elif "翻译" in content:
        # 更新状态并跳转到翻译代理
        return Command(
            update={
                "messages": [("system", "路由到翻译代理")],
                "current_agent": "node_translation_agent"
            },
            goto="node_translation_agent"
        )
    else:
        return Command(
            update={
                "messages": [("system", "任务完成")],
                "is_task_completed": True
            },
            goto=END
        )

# 节点函数：数学代理
def node_math_agent(state: AgentState) -> Command[Literal["node_decision_agent"]]:
    """数学代理节点"""
    print("执行节点: math_agent")

    # 执行数学计算任务
    result = "2+2=4"
    print(f"计算结果: {result}")

    # 更新状态并返回决策代理
    return Command(
        update={
            "messages": [("assistant", f"计算结果为：{result}")],
            "current_agent": "node_decision_agent"
        },
        goto="node_decision_agent"
    )

# 节点函数：翻译代理
def node_translation_agent(state: AgentState) -> Command[Literal["node_decision_agent"]]:
    """翻译代理节点"""
    print("执行节点: translation_agent")

    # 执行翻译任务
    translation = "Hello -> 你好"
    print(f"翻译结果：: {translation}")

    # 更新状态并返回决策代理
    return Command(
        update={
            "messages": [("assistant", f"结果：: {translation}")],
            "current_agent": "node_decision_agent"
        },
        goto="node_decision_agent"
    )

def main():
    """演示Command基础用法"""
    print("=== Command 基础演示 ===\n")

    builder = StateGraph(AgentState)

    builder.add_node("node_decision_agent", node_decision_agent)
    builder.add_node("node_math_agent", node_math_agent)
    builder.add_node("node_translation_agent", node_translation_agent)

    builder.add_edge(START, "node_decision_agent")

    graph = builder.compile()

    # 执行图 - 测试数学任务
    print("测试1: 数学任务")
    initial_state = {
        "messages": [('user', '我需要计算数学题')],
        "current_agent": "user",
        "is_task_completed": False
    }

    print("初始状态:", initial_state)
    result = graph.invoke(initial_state)
    print("最终状态:", result)
    print("\n" + "=" * 50 + "\n")

    # 执行图 - 测试翻译任务
    print("测试2: 翻译任务")
    initial_state = {
        "messages": [('user', '我需要翻译文本')],
        "current_agent": "user",
        "is_task_completed": False
    }

    print("初始状态:", initial_state)
    result = graph.invoke(initial_state)
    print("最终状态:", result)
    print("\n" + "=" * 50 + "\n")

    # 执行图 - 测试任务完成
    print("测试3: 任务完成")
    initial_state = {
        "messages": [('user', '你好')],
        "current_agent": "user",
        "is_task_completed": False
    }

    print("初始状态:", initial_state)
    result = graph.invoke(initial_state)
    print("最终状态:", result)
    print("\n" + "=" * 50 + "\n")


if __name__ == '__main__':
    main()