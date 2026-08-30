"""
LangGraph 审批工作流演示

该演示展示了如何使用 LangGraph 的中断功能实现需要人工审批的工作流。
当工作流遇到关键操作时会暂停，并等待用户的批准或拒绝。
"""
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command,interrupt
from langgraph.checkpoint.memory import InMemorySaver


class Approval(TypedDict):
    """审批状态定义"""
    action_details: str
    status: Optional[Literal["pending", "approved", "rejected"]]

def node_approval(state: Approval) -> Command[Literal["node_proceed", "node_cancel"]]:
    print(f"执行节点: node_approval")
    print(f"操作详情: {state['action_details']}")
    print("工作流暂停，等待用户审批...")

    # 中断执行并暴露详细信息供调用方在UI中渲染
    decision = interrupt({
        "question": "批准此操作吗？",
        "details": state['action_details']
    })
    next_node = "node_proceed" if decision else "node_cancel"
    print(f"审批决定：{'批准' if decision else '拒绝'}, 路由到节点: {next_node}")

    return Command(goto=next_node)

def node_proceed(_state: Approval):
    print("执行节点: node_proceed")
    print("操作已被批准，正在执行...")
    return {"status": "approved"}

def node_cancel(_state: Approval):
    print("执行节点: node_cancel")
    print("操作已被拒绝，正在取消...")
    return {"status": "rejected"}

def create_graph():
    builder = StateGraph(Approval)

    builder.add_node(node_approval)
    builder.add_node(node_proceed)
    builder.add_node(node_cancel)

    builder.add_edge(START, "node_approval")
    builder.add_edge("node_proceed", END)
    builder.add_edge("node_cancel", END)

    return builder

def main():
    # 使用内存保存器作为检查点
    memory = InMemorySaver()
    builder = create_graph()
    graph = builder.compile(checkpointer=memory)

    config = {
        "configurable": {
            "thread_id": "approval01"
        }
    }

    print("1. 启动审批工作流...")
    initial_res = graph.invoke({
        "action_details": "转账 500",
        "status": "pending"
    }, config=config)

    # 显示中断信息
    print(f"工作流中断信息：{initial_res['__interrupt__']}")

    # 模拟用户审批过程
    print("2. 模拟用户审批过程...")
    interrupt_value = initial_res["__interrupt__"][0].value # 看过输出就知道输出的是哪个键值对
    print("问题:", interrupt_value["question"])
    print("操作详情:", interrupt_value["details"])

    # 获取用户输入
    while True:
        user_input = input("请输入审批决定(y/n):").strip().lower()
        if user_input in ['y', 'yes', '是']:
            decision = True
            break
        elif user_input in ['n', 'no', '否']:
            decision = False
            break
        else:
            print("无效输入，请输入 y/yes/是 或者 n/no/否")

    # 使用用户决定恢复执行
    print(f"\n3. 使用审批决定恢复工作流执行...")
    result = graph.invoke(Command(resume=decision), config=config)

    # 显示最终结果
    print(f"最终状态: {result}")
    print(f"操作状态: {result['status']}")
    print("\n=== 演示完成 ===")

if __name__ == '__main__':
    main()