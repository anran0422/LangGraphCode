"""
LangGraph 消息修剪演示

使用 trim_messages 对消息历史进行裁剪，
避免消息历史超过模型的上下文窗口限制。

功能：
1. 使用 MessagesState 保存消息历史
2. 使用 InMemorySaver 保存线程状态
3. 使用 trim_messages 保留最近的消息
4. 使用 count_tokens_approximately 估算 Token 数量
5. 如果配置了模型，则调用通义千问；否则使用模拟响应
"""

from typing import List

from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import MessagesState

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages.utils import (
    trim_messages,
    count_tokens_approximately,
)

from langchain.chat_models import init_chat_model


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


# ============================================================
# 2. 定义 State
# ============================================================

class ChatState(MessagesState):
    pass


# ============================================================
# 3. 模型调用节点
# ============================================================

def node_call_model(state: ChatState):
    print("执行节点：node_call_model")

    original_messages = state["messages"]

    print(f"原始消息数量：{len(original_messages)}")

    # --------------------------------------------------------
    # 对消息进行修剪
    # --------------------------------------------------------
    messages = trim_messages(
        original_messages,
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=128,
        start_on="human",
        end_on=("human", "tool"),
    )

    print(f"裁剪后的消息数量：{len(messages)}")

    # --------------------------------------------------------
    # 如果模型初始化成功，则调用真实模型
    # --------------------------------------------------------
    if model:
        try:
            response = model.invoke(messages)

            print(f"生成回答：{response}")

            return {
                "messages": [response]
            }

        except Exception as e:
            print(f"调用模型失败：{e}")

    # --------------------------------------------------------
    # 模拟模型调用
    # --------------------------------------------------------

    last_message = (
        original_messages[-1].content
        if original_messages
        else ""
    )

    # 根据用户最后一条消息生成模拟响应
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


# ============================================================
# 4. 构建 LangGraph
# ============================================================

def build_graph():

    # 创建检查点保存器
    checkpointer = InMemorySaver()

    # 创建 StateGraph
    builder = StateGraph(ChatState)

    # 添加节点
    builder.add_node(
        "node_call_model",
        node_call_model,
    )

    # START → node_call_model
    builder.add_edge(
        START,
        "node_call_model",
    )

    # 编译图
    graph = builder.compile(
        checkpointer=checkpointer
    )

    return graph


# ============================================================
# 5. 主函数
# ============================================================

def main():

    print("=== LangGraph 消息修剪演示 ===\n")

    # --------------------------------------------------------
    # 创建图
    # --------------------------------------------------------

    graph = build_graph()

    # --------------------------------------------------------
    # 配置线程 ID
    # --------------------------------------------------------

    config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    # ========================================================
    # 第一次调用
    # ========================================================

    print("1. 第一次调用 - 问候：")

    result1 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="hi, my name is bob"
                )
            ]
        },
        config,
    )

    print(
        f"回复：{result1['messages'][-1].content}"
    )

    # ========================================================
    # 第二次调用
    # ========================================================

    print("\n2. 第二次调用 - 请求写诗（关于猫）：")

    result2 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="write a short poem about cats"
                )
            ]
        },
        config,
    )

    print(
        f"回复：{result2['messages'][-1].content}"
    )

    # ========================================================
    # 第三次调用
    # ========================================================

    print("\n3. 第三次调用 - 请求写诗（关于狗）：")

    result3 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="now do the same but for dogs"
                )
            ]
        },
        config,
    )

    print(
        f"回复：{result3['messages'][-1].content}"
    )

    # ========================================================
    # 第四次调用
    # ========================================================

    print("\n4. 第四次调用 - 询问名字：")

    result4 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="what's my name?"
                )
            ]
        },
        config,
    )

    print(
        f"回复：{result4['messages'][-1].content}"
    )

    # ========================================================
    # 第五次调用：模拟大量消息
    # ========================================================

    print("\n5. 模拟大量消息以展示修剪效果：")

    many_messages: List[HumanMessage] = []

    for i in range(20):

        many_messages.append(
            HumanMessage(
                content=(
                    f"这是第{i + 1}条测试消息，"
                    "内容很长很长很长很长很长很长"
                    "很长很长很长很长很长很长"
                )
            )
        )

    result5 = graph.invoke(
        {
            "messages": (
                many_messages
                + [
                    HumanMessage(
                        content="what's my name?"
                    )
                ]
            )
        },
        config,
    )

    print(
        f"回复：{result5['messages'][-1].content}"
    )

    print("\n=== 演示完成 ===")


# ============================================================
# 6. 程序入口
# ============================================================

if __name__ == "__main__":
    main()