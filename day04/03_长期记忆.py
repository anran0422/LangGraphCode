"""
LangGraph 长期记忆演示

该演示展示了如何使用长期记忆跨对话存储用户特定或应用程序特定的数据。

可以看到，这里存储绑定在了 user_id 上面。
"""

import operator
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.store.memory import InMemoryStore
from langchain_core.messages import HumanMessage, AIMessage


class ChatState(TypedDict):
    messages: Annotated[list, operator.add]


def node_chat(state: ChatState, *, store):
    print("执行节点：node_chat")

    user_id = "user_123"

    # ==================== 1. 从长期记忆中获取用户信息 ====================

    try:
        user_info_item = store.get(("users",), user_id)
        user_info = user_info_item.value if user_info_item else {}

        print(f"存储中获取用户信息：{user_info}")

    except Exception as e:
        print(f"获取用户信息出错：{e}")
        user_info = {}

    # ==================== 2. 获取最新的用户消息 ====================

    user_messages = [
        msg for msg in state["messages"]
        if isinstance(msg, HumanMessage)
    ]

    if user_messages:
        latest_message = user_messages[-1].content
        print(f"用户消息: {latest_message}")
    else:
        return {
            "messages": [
                AIMessage(content="我没有收到你的消息，请再说一遍。")
            ]
        }

    # ==================== 3. 从消息中提取用户信息 ====================

    # ---------- 提取姓名 ----------
    if "我叫" in latest_message or "我是" in latest_message:

        # 简单提取姓名
        if "我叫" in latest_message:
            name_start = latest_message.find("我叫") + 2
        else:
            name_start = latest_message.find("我是") + 2

        name_end = len(latest_message)

        for i in range(name_start, len(latest_message)):
            if latest_message[i] in [
                ",", "，", ".", "。", "!", "！", "?", "？"
            ]:
                name_end = i
                break

        name = latest_message[name_start:name_end].strip()

        if name:
            user_info["name"] = name

    # ---------- 提取年龄 ----------
    if "岁" in latest_message:

        age_pos = latest_message.find("岁")
        age_str = ""

        for i in range(age_pos - 1, -1, -1):
            if latest_message[i].isdigit():
                age_str = latest_message[i] + age_str
            else:
                break

        if age_str and age_str.isdigit():
            user_info["age"] = int(age_str)

    # ---------- 提取位置 ----------
    if "来自" in latest_message:

        location_start = latest_message.find("来自") + 2
        location_end = len(latest_message)

        for i in range(location_start, len(latest_message)):
            if latest_message[i] in [
                ",", "，", ".", "。", "!", "！", "?", "？"
            ]:
                location_end = i
                break

        location = latest_message[
            location_start:location_end
        ].strip()

        if location:
            user_info["location"] = location

    # ==================== 4. 保存更新后的用户信息 ====================

    if user_info:
        try:
            store.put(("users",), user_id, user_info)
            print(f"保存用户信息到存储: {user_info}")

        except Exception as e:
            print(f"保存用户信息时出错: {e}")

    # ==================== 5. 根据用户消息生成回复 ====================

    # ---------- 用户说你好 ----------
    if "你好" in latest_message or "hello" in latest_message.lower():

        if user_info.get("name"):
            response = f"你好，{user_info['name']}！很高兴再次见到你。"
        else:
            response = "你好！我是AI助手。能告诉我你的名字吗？"

    # ---------- 用户介绍自己 ----------
    elif "我叫" in latest_message or "我是" in latest_message:

        name = user_info.get("name", "朋友")
        response = f"很高兴认识你，{name}！有什么我可以帮助你的吗？"

    # ---------- 用户说再见 ----------
    elif "再见" in latest_message or "bye" in latest_message.lower():

        name = user_info.get("name", "朋友")
        response = f"再见，{name}！期待下次与你交流。"

    # ---------- 其他情况 ----------
    else:

        info_parts = []

        if user_info.get("name"):
            info_parts.append(f"名字是{user_info['name']}")

        if user_info.get("age"):
            info_parts.append(f"年龄是{user_info['age']}岁")

        if user_info.get("location"):
            info_parts.append(f"来自{user_info['location']}")

        if info_parts:
            info_summary = "，而且我知道你" + "，".join(info_parts)
            response = f"我理解你的问题。{info_summary}。让我来帮助你解答。"
        else:
            response = "我理解你的问题。让我来帮助你解答。"

    # ==================== 6. 返回 AI 消息 ====================

    print(f"生成的回复: {response}")

    return {
        "messages": [
            AIMessage(content=response)
        ]
    }


def main():
    """主函数 - 演示长期记忆功能"""

    print("=== LangGraph 长期记忆演示 ===\n")

    # ==================== 1. 创建内存存储 ====================

    store = InMemoryStore()

    # ==================== 2. 构建图 ====================

    builder = StateGraph(ChatState)

    builder.add_node("chat", node_chat)

    builder.add_edge(START, "chat")

    # ==================== 3. 编译图并使用存储 ====================

    graph = builder.compile(store=store)

    # ==================== 4. 第一轮对话 ====================

    print("1. 第一轮对话:")

    result1 = graph.invoke({
        "messages": [
            HumanMessage(content="你好，我叫张三，来自北京。")
        ]
    })

    print("对话历史:")

    for msg in result1["messages"]:
        print(f"  {type(msg).__name__}: {msg.content}")

    print()

    # ==================== 5. 第二轮对话 ====================

    print("2. 第二轮对话:")

    result2 = graph.invoke({
        "messages": [
            HumanMessage(content="我今年25岁了。")
        ]
    })

    print("对话历史:")

    for msg in result2["messages"]:
        print(f"  {type(msg).__name__}: {msg.content}")

    print()

    # ==================== 6. 第三轮对话 ====================

    print("3. 第三轮对话:")

    result3 = graph.invoke({
        "messages": [
            HumanMessage(content="你好！")
        ]
    })

    print("对话历史:")

    for msg in result3["messages"]:
        print(f"  {type(msg).__name__}: {msg.content}")

    print()

    # ==================== 7. 查看长期记忆中的内容 ====================

    print("4. 查看存储的内容:")

    try:
        user_info_item = store.get(("users",), "user_123")

        if user_info_item:
            print(f"存储的用户信息: {user_info_item.value}")
        else:
            print("未找到用户信息")

    except Exception as e:
        print(f"查看存储内容时出错: {e}")

    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    main()