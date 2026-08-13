"""
LangGraph 1.0 持久化存储演示 - 内存存储 (In-Memory)

特点：
- 数据暂存于内存，程序关闭后丢失
- 无需额外配置
- 适用于本地测试和临时验证工作流逻辑
"""
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
import operator

class PersistenceState(TypedDict):
    messages: Annotated[list, operator.add]
    step_count : Annotated[int, operator.add]

def node_step_one(state: PersistenceState):
    print("执行步骤 1")
    return {
        "messages": ["执行了步骤 1"],
        "step_count": 1
    }

def node_step_two(state: PersistenceState):
    print("执行步骤 2")
    return {
        "messages": ["执行了步骤 2"],
        "step_count": 1
    }

def node_step_three(state: PersistenceState):
    print("执行步骤 3")
    return {
        "messages": ["执行了步骤 3"],
        "step_count": 1
    }

def create_graph():
    builder = StateGraph(PersistenceState)

    builder.add_node(node_step_one)
    builder.add_node(node_step_two)
    builder.add_node(node_step_three)

    builder.add_edge(START, "node_step_one")
    builder.add_edge("node_step_one", "node_step_two")
    builder.add_edge("node_step_two", "node_step_three")
    builder.add_edge("node_step_three", END)

    return builder

def main():
    print("=== LangGraph 1.0 内存持久化存储演示 ===\n")

    # 创建内存存储
    memory = InMemorySaver()

    # 编译图并且使用内存存储
    graph = create_graph()
    graph = graph.compile(checkpointer=memory)

    # 配置线程ID用于存储状态
    config = {
        "configurable": {
            "thread_id": "demo_thread_1"
        }
    }

    print("1. 首次执行工作流")
    result = graph.invoke({
        "messages": ["开始执行"],
        "step_count":0
    }, config)
    print(f"执行结果: {result}\n")

    print("2. 检查存储的状态：")
    saved_state = graph.get_state(config)
    print(f"保存的状态:{saved_state.values}")
    print(f"下一个节点：{saved_state.next}\n")

    print("3. 恢复执行工作流")
    # 由于工作流已经完成，这里会直接返回最终结果
    result2 = graph.invoke(None, config) # “不要给这个 thread 新的输入，从已有 checkpoint 状态继续。”
    print(f"恢复执行结果: {result2}\n")

    print("=== 演示结束 ===")

if __name__ == '__main__':
    main()
