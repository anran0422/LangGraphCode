"""
LangGraph 审阅和编辑工作流演示

该演示展示了如何使用 LangGraph 的中断功能实现人工审阅和编辑工作流。
这对于让人类在继续之前审核并编辑图状态非常有用。
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command,interrupt
from langgraph.checkpoint.memory import InMemorySaver

class ReviewState(TypedDict):
    generated_text: str

def node_review(state: ReviewState):
    print(f"执行节点: review_node")
    print(f"当前文本内容: {state['generated_text']}")
    print("工作流暂停，等待用户审阅和编辑...")

    # 请求审阅者编辑生成的内容
    updated = interrupt({
        "instruction": "请审阅并编辑以下内容",
        "content": state['generated_text']
    })

    print(f"收到编辑后的内容：{updated}")
    return {
        "generated_text": updated
    }


def create_graph():
    builder = StateGraph(ReviewState)

    builder.add_node(node_review)
    builder.add_edge(START, "node_review")
    builder.add_edge("node_review", END)

    return builder

def main():
    memory = InMemorySaver()
    builder = create_graph()
    graph = builder.compile(checkpointer=memory)
    config = {
        "configurable": {
            "thread_id": "review01"
        }
    }
    # 初始化状态并执行图
    print("1. 启动审阅工作流...")
    initial_res = graph.invoke({
        "generated_text": "这是初始起草内容"
    }, config=config)

    # 显示中断信息
    print(f"工作流中断信息: {initial_res['__interrupt__']}")

    # 模拟用户审阅和编辑过程
    print("2. 模拟用户审阅和编辑过程...")
    interrupt_value = initial_res['__interrupt__'][0].value
    print("指导说明:", interrupt_value["instruction"])
    print("原文内容:", interrupt_value["content"])

    # 获取用户编辑后的内容
    user_input = input("请输入审阅重新编辑后的内容：").strip()

    # 使用用户编辑后的内容恢复执行
    print("\n3.使用编辑后的内容恢复工作流执行...")
    final_res = graph.invoke(
        Command(resume=user_input),
        config=config
    )
    # 显示最终结果
    print(f"最终状态: {final_res}")
    print(f"最终文本内容: {final_res['generated_text']}")
    print("\n=== 演示完成 ===")

if __name__ == '__main__':
    main()