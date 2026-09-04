"""
LangGraph 短期记忆演示

该演示展示了如何使用短期记忆（线程级持久性）使智能体能够跟踪多轮对话。
"""
import operator
from typing import TypedDict,Annotated
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver

class ChatState(TypedDict):
    messages: Annotated[list, operator.add]
    user_name: str

def node_greeting(state: ChatState):
    print("执行节点：node_greeting")
    user_name = state.get("user_name", "访客")
    greeting_message = f"你好，{user_name}！我是你的 AI 助手。"

    return {
        "messages": [("assistant", greeting_message)]
    }

def node_respond(state: ChatState):
    print("执行节点：node_respond")

    user_messages = [msg for msg in state['messages'] if msg[0] == "user"]
    if user_messages:
        last_user_message = user_messages[-1][1] # 元组的第二个位置
        user_name = state.get("user_name", "访客")

        # 根据消息生成不同的回应
        if "你好" in last_user_message or "hello" in last_user_message.lower():
            response = f"{user_name}，你好！请问有什么可以帮助你的？"
        elif "天气" in last_user_message:
            response = f"{user_name}，抱歉！我无法获取实时天气信息。"
        elif "名字" in last_user_message or "我是" in last_user_message:
            response = f"我知道你叫{user_name}，很高兴认识你！"
        else:
            response = f"我理解你说的 {user_name}，能告诉我更多吗？"
    else:
        response = "我没有看到你的消息，请再说一遍！"

    return {
        "messages": [("assistant", response)]
    }

def create_graph():

    builder = StateGraph(ChatState)

    builder.add_node(node_greeting)
    builder.add_node(node_respond)

    builder.add_edge(START, "node_greeting")
    builder.add_edge("node_greeting", "node_respond")
    builder.add_edge("node_respond", END)

    return builder

def main():
    builder = create_graph()
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    config = {
        "configurable": {
            "thread_id": "short_memory01"
        }
    }

    # 第一轮对话
    print("1. 第 1 轮对话")
    res1 = graph.invoke({
        "messages": [("user", "你好！我叫张三！")],
        "user_name": "张三"
    }, config=config)
    print("对话历史：===============")
    for role,message in res1['messages']:
        print(f" {role} : {message}")
    print()

    # 查看存储状态
    print("2. 查看存储状态")
    saved_state = graph.get_state(config=config)
    print("保存的对话历史：===============")
    for role,message in saved_state.values["messages"]:
        print(f" {role} : {message}")
    print()

    # 第二轮对话（继续之前的对话）
    print("3. 第二轮对话（继续之前的对话）:")
    result2 = graph.invoke({
        "messages": [("user", "今天天气怎么样？")],
        "user_name": "张三"
    }, config)

    print("对话历史:")
    for role, message in result2["messages"]:
        print(f" {role}: {message}")
    print()

    # 第三轮对话
    print("4. 第三轮对话:")
    result3 = graph.invoke({
        "messages": [("user", "你能记住我的名字吗？")],
        "user_name": "张三"
    }, config)

    print("对话历史:")
    for role, message in result3["messages"]:
        print(f" {role}: {message}")
    print()

    # 查看最终状态
    print("5. 最终状态:")
    final_state = graph.get_state(config)
    print("完整的对话历史:")
    for role, message in final_state.values["messages"]:
        print(f" {role}: {message}")
    print()

    print("=== 演示完成 ===")

if __name__ == "__main__":
    main()