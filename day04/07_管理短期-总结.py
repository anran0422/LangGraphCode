"""
LangGraph 对话总结演示

该演示展示了如何使用聊天模型来总结消息历史，
而不是简单地修剪或删除消息。

这种方法可以避免在清理消息队列时丢失重要信息。
"""

from typing import TypedDict, Annotated, Sequence

from langgraph.graph import (
    StateGraph,
    START,
    MessagesState,
    add_messages,
)
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage,
    SystemMessage,
)
from langchain.chat_models import init_chat_model


# ============================================================
# State
# ============================================================

class SummaryState(TypedDict):
    messages: Annotated[list, add_messages]
    summary: str


# ============================================================
# 初始化模型
# ============================================================

model = None
summary_model = None

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

    summary_model = model.bind(max_tokens=128)

    print("成功初始化千问大模型")

except Exception as e:
    print(f"初始化模型失败：{e}")


# ============================================================
# 对话总结
# ============================================================

def summarize_conversation(
    messages: Sequence[BaseMessage],
    current_summary: str = "",
):
    """根据当前消息生成新的对话摘要。"""

    if not messages:
        return current_summary

    # --------------------------------------------------------
    # 使用真实模型生成摘要
    # --------------------------------------------------------

    if summary_model:
        try:
            summary_prompt = (
                f"当前摘要：{current_summary}\n\n"
                "新对话："
            )

            for msg in messages:
                if isinstance(msg, HumanMessage):
                    summary_prompt += f"人类：{msg.content}\n"

                elif isinstance(msg, AIMessage):
                    summary_prompt += f"AI：{msg.content}\n"

            summary_prompt += (
                "\n请提供一个简洁的摘要，"
                "包含重要的信息和上下文："
            )

            response = summary_model.invoke(
                [SystemMessage(content=summary_prompt)]
            )

            return response.content

        except Exception as e:
            print(f"调用总结模型失败：{e}")

    # --------------------------------------------------------
    # 模拟摘要生成
    # --------------------------------------------------------

    # 使用最近 3 条消息进行模拟摘要
    recent_messages = messages[-3:]

    summary_content = "".join(
        msg.content for msg in recent_messages
    )

    return f"对话摘要：{summary_content[:100]}..."


# ============================================================
# 总结节点
# ============================================================

def node_summarize(state: SummaryState):
    """检查消息数量，必要时生成摘要并保留最近消息。"""

    print("执行节点：node_summarize")

    messages = state["messages"]
    current_summary = state["summary"]

    print(f"当前消息数量：{len(messages)}")
    print(f"当前摘要：{current_summary}")

    # --------------------------------------------------------
    # 消息超过阈值，开始总结
    # --------------------------------------------------------

    if len(messages) > 4:
        print("消息数量超过阈值，开始总结对话")

        # 获取最近 4 条消息
        recent_messages = messages[-4:]

        # 生成新的摘要
        new_summary = summarize_conversation(
            recent_messages,
            current_summary,
        )

        print(f"生成新的摘要：{new_summary}")

        # 保留最近 2 条消息
        return {
            "summary": new_summary,
            "messages": messages[-2:],
        }

    # --------------------------------------------------------
    # 消息数量未超过阈值
    # --------------------------------------------------------

    print("消息数量未超过阈值，无需总结")

    return {
        "summary": current_summary,
    }


# ============================================================
# 模型调用节点
# ============================================================

def node_call_model(state: SummaryState):
    """构造模型上下文并调用聊天模型。"""

    print("执行节点：node_call_model")

    messages = state["messages"]
    summary = state["summary"]

    print(f"当前消息数量：{len(messages)}")
    print(f"当前摘要：{summary}")

    # --------------------------------------------------------
    # 构造模型上下文
    # --------------------------------------------------------

    context_messages = []

    # 如果存在摘要，先加入摘要
    if summary:
        context_messages.append(
            SystemMessage(
                content=f"之前的对话摘要：{summary}"
            )
        )

    # 无论有没有摘要，都加入当前消息
    context_messages.extend(messages)

    # --------------------------------------------------------
    # 显示模型收到的所有消息
    # --------------------------------------------------------

    print("模型上下文：")

    for i, msg in enumerate(context_messages):
        content = str(msg.content)

        print(
            f"  消息 {i + 1}: "
            f"{type(msg).__name__} - "
            f"{content[:50]}"
            f"{'...' if len(content) > 50 else ''}"
        )

    # --------------------------------------------------------
    # 调用真实模型
    # --------------------------------------------------------

    if model:
        try:
            response = model.invoke(context_messages)

            print(f"生成的回复：{response.content}")

            return {
                "messages": [response]
            }

        except Exception as e:
            print(f"调用模型出错：{e}")

    # --------------------------------------------------------
    # 模拟模型调用
    # --------------------------------------------------------

    last_message = messages[-1].content if messages else ""

    # 根据消息内容生成模拟响应

    if "名字" in last_message or "name" in last_message.lower():

        if "bob" in last_message.lower():
            response = "我记得你的名字是 bob。"

        else:
            response = "你还没有告诉我你的名字呢。"

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
# 创建图
# ============================================================

def build_graph():
    """创建并编译 LangGraph。"""

    # 创建检查点保存器
    checkpointer = InMemorySaver()

    # 创建 StateGraph
    builder = StateGraph(SummaryState)

    # 添加节点
    builder.add_node("summarize", node_summarize)
    builder.add_node("call_model", node_call_model)

    # 添加边
    builder.add_edge(START, "summarize")
    builder.add_edge("summarize", "call_model")

    # 编译图
    graph = builder.compile(
        checkpointer=checkpointer
    )

    return graph


# ============================================================
# 主函数
# ============================================================

def main():
    """主函数 - 演示对话总结功能。"""

    print("=== LangGraph 对话总结演示 ===\n")

    # 创建图
    graph = build_graph()

    # 配置线程 ID
    config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    # --------------------------------------------------------
    # 第一次调用 - 问候
    # --------------------------------------------------------

    print("1. 第一次调用 - 问候：")

    result1 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="hi, my name is bob"
                )
            ],
            "summary": "",
        },
        config,
    )

    print(f"回复：{result1['messages'][-1].content}")
    print(f"当前摘要：{result1.get('summary', '')}")

    print("\n" + "=" * 50 + "\n")

    # --------------------------------------------------------
    # 第二次调用 - 请求写诗（关于猫）
    # --------------------------------------------------------

    print("2. 第二次调用 - 请求写诗（关于猫）：")

    result2 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="write a short poem about cats"
                )
            ],
            "summary": result1.get("summary", ""),
        },
        config,
    )

    print(f"回复：{result2['messages'][-1].content}")
    print(f"当前摘要：{result2.get('summary', '')}")

    print("\n" + "=" * 50 + "\n")

    # --------------------------------------------------------
    # 第三次调用 - 请求写诗（关于狗）
    # --------------------------------------------------------

    print("3. 第三次调用 - 请求写诗（关于狗）：")

    result3 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="now do the same but for dogs"
                )
            ],
            "summary": result2.get("summary", ""),
        },
        config,
    )

    print(f"回复：{result3['messages'][-1].content}")
    print(f"当前摘要：{result3.get('summary', '')}")

    print("\n" + "=" * 50 + "\n")

    # --------------------------------------------------------
    # 第四次调用 - 询问名字
    # --------------------------------------------------------

    print("4. 第四次调用 - 询问名字：")

    result4 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="what's my name?"
                )
            ],
            "summary": result3.get("summary", ""),
        },
        config,
    )

    print(f"回复：{result4['messages'][-1].content}")
    print(f"当前摘要：{result4.get('summary', '')}")

    print("\n" + "=" * 50 + "\n")

    # --------------------------------------------------------
    # 第五次调用 - 添加更多对话以触发总结
    # --------------------------------------------------------

    print("5. 第五次调用 - 添加更多对话以触发总结：")

    conversation_history = [
        HumanMessage(content="让我们聊聊天气"),
        AIMessage(content="好的，你想聊什么地区的天气？"),
        HumanMessage(content="北京的天气怎么样？"),
        AIMessage(
            content="我无法获取实时天气信息，"
                    "但北京属于温带大陆性季风气候。"
        ),
        HumanMessage(content="what's my name?"),
    ]

    result5 = graph.invoke(
        {
            "messages": conversation_history,
            "summary": result4.get("summary", ""),
        },
        config,
    )

    print(f"回复：{result5['messages'][-1].content}")
    print(f"当前摘要：{result5.get('summary', '')}")

    print("\n=== 演示完成 ===")


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":
    main()