"""
LangGraph 消息删除演示

该演示展示了如何使用 RemoveMessage 从图状态中删除消息。
当状态的 key 带有 add_messages 这个 reducer 时（例如 MessagesState），RemoveMessage 可以正常工作。
"""

from typing import Annotated, Sequence, TypedDict

from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import (
HumanMessage,
AIMessage,
RemoveMessage,
BaseMessage
)
from langchain_core.messages.utils import count_tokens_approximately
from langchain.chat_models import init_chat_model


class CustomMessagesState(TypedDict):
    messages: Annotated[Sequence[HumanMessage], "messages"]


# ============================================================
# 1. 初始化模型
# ============================================================

model = None

try:
    model = init_chat_model(
        model="qwen3.8-max",
        model_provider="openai",
        api_key="你的API_KEY",
        base_url=(
            "https://dashscope.aliyuncs.com/"
            "api/v2/apps/protocols/compatible-mode/v1"
        ),
        use_responses_api=True,
    )

    print("成功初始化千问大模型")

except Exception as e:
    print(f"初始化模型失败：{e}")

def node_call_model(state: MessagesState):
    print("执行节点：node_call_model")

    # 获取原始消息
    original_messages = state["messages"]

    print(f"原始消息数量：{len(original_messages)}")

    # 显示所有消息
    for i, msg in enumerate(original_messages):
        content = msg.content

        print(
            f"    消息 {i + 1}: "
            f"{type(msg).__name__} - "
            f"{content[:50]}"
            f"{'...' if len(content) > 50 else ''}"
        )

    # ============================================================
    # 调用真实模型
    # ============================================================

    if model:
        try:
            response = model.invoke(state["messages"])
            print(f"生成回答：{response.content}")
            return {
                "messages": [response]
            }
        except Exception as e:
            print(f"调用模型失败：{e}")

    # ============================================================
    # 模拟模型调用
    # ============================================================
    last_message = (
        original_messages[-1].content
        if original_messages
        else ""
    )
    # 根据消息内容生成模拟响应
    if "名字" in last_message or "name" in last_message.lower():
        response = "我记得你的名字是 bob。"
    elif "诗" in last_message or "poem" in last_message.lower():
        if "猫" in last_message or "cat" in last_message.lower():
            response = (
                "这里是一首关于猫的短诗：\n"
                "小猫咪咪叫，\n"
                "尾巴摇啊摇，\n"
                "捉鼠本领高，\n"
                "主人乐陶陶。"
            )
        elif "狗" in last_message or "dog" in last_message.lower():
            response = (
                "这里是一首关于狗的短诗：\n"
                "小狗汪汪叫，\n"
                "忠诚又可靠，\n"
                "看家护院好，\n"
                "人类好朋友。"
            )
        else:
            response = "我可以为你写一首关于猫或狗的诗。"
    elif "你好" in last_message or "hi" in last_message.lower():
        response = "你好！我是 AI 助手。"

    else:
        response = "我理解你的问题，让我来帮助你解答。"

    print(f"生成的模拟回复：{response}")

    return {
        "messages": [
            AIMessage(content=response)
        ]
    }

def node_delete_messages(state: MessagesState):
    print("执行节点：node_delete_messages")
    # 获取原始消息
    original_messages = state["messages"]
    print(f"删除前消息数量：{len(original_messages)}")
    if len(original_messages) > 2:
        # 删除最早的两条消息
        to_remove = [RemoveMessage(id=m.id) for m in original_messages[:2]]
        print(f"将删除 {len(to_remove)} 条消息")
        # 显示要删除的消息
        for i, msg in enumerate(original_messages[:2]):
            content = msg.content
            print(
                f"    消息 {i + 1}: "
                f"{type(msg).__name__} - "
                f"{content[:50]}"
                f"{'...' if len(content) > 50 else ''}"
            )
        return {
            "messages": to_remove
        }
    else:
        print("消息数量不足，无需删除")
        return {}

def build_graph():
    """构建 LangGraph"""

    # 创建检查点保存器
    checkpointer = InMemorySaver()

    # 创建 StateGraph
    builder = StateGraph(MessagesState)

    # 添加节点
    builder.add_node(node_call_model)
    builder.add_node(node_delete_messages)

    # 添加边
    builder.add_edge(START, "node_call_model")
    builder.add_edge("node_call_model", "node_delete_messages")
    builder.add_edge("node_delete_messages", END)

    # 编译图
    app = builder.compile(
        checkpointer=checkpointer
    )

    return app


def main():
    """主函数 - 演示消息删除功能"""

    print("=== LangGraph 消息删除演示 ===\n")

    # ============================================================
    # 创建图
    # ============================================================

    app = build_graph()

    # ============================================================
    # 配置线程 ID
    # ============================================================

    config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    # ============================================================
    # 第一次调用 - 问候
    # ============================================================

    print("1. 第一次调用 - 问候:")

    for event in app.stream(
        {
            "messages": [
                HumanMessage(content="hi! I'm bob")
            ]
        },
        config,
        stream_mode="values",
    ):
        print(
            f"当前状态中的消息数量: "
            f"{len(event['messages'])}"
        )

        if event["messages"]:
            last_message = event["messages"][-1]

            print(
                f"最新消息: "
                f"{type(last_message).__name__} - "
                f"{last_message.content}"
            )

    print("\n" + "=" * 50 + "\n")

    # ============================================================
    # 第二次调用 - 询问名字
    # ============================================================

    print("2. 第二次调用 - 询问名字:")

    for event in app.stream(
        {
            "messages": [
                HumanMessage(content="what's my name?")
            ]
        },
        config,
        stream_mode="values",
    ):
        print(
            f"当前状态中的消息数量: "
            f"{len(event['messages'])}"
        )

        if event["messages"]:
            last_message = event["messages"][-1]

            print(
                f"最新消息: "
                f"{type(last_message).__name__} - "
                f"{last_message.content}"
            )

    print("\n" + "=" * 50 + "\n")

    # ============================================================
    # 第三次调用 - 请求写诗
    # ============================================================

    print("3. 第三次调用 - 请求写诗:")

    for event in app.stream(
        {
            "messages": [
                HumanMessage(
                    content="write a short poem about cats"
                )
            ]
        },
        config,
        stream_mode="values",
    ):
        print(
            f"当前状态中的消息数量: "
            f"{len(event['messages'])}"
        )

        if event["messages"]:
            last_message = event["messages"][-1]

            print(
                f"最新消息: "
                f"{type(last_message).__name__} - "
                f"{last_message.content}"
            )

    print("\n" + "=" * 50 + "\n")

    # ============================================================
    # 第四次调用 - 请求写诗（关于狗）
    # ============================================================

    print("4. 第四次调用 - 请求写诗（关于狗）:")

    for event in app.stream(
        {
            "messages": [
                HumanMessage(
                    content="now do the same but for dogs"
                )
            ]
        },
        config,
        stream_mode="values",
    ):
        print(
            f"当前状态中的消息数量: "
            f"{len(event['messages'])}"
        )

        if event["messages"]:
            last_message = event["messages"][-1]

            print(
                f"最新消息: "
                f"{type(last_message).__name__} - "
                f"{last_message.content}"
            )

    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    main()