"""
LangGraph Reducer函数演示 - add_messages Reducer（消息列表专用）
"""

from typing import List, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph import add_messages

# 2. add_messages Reducer(消息列表专用）
class AddMessagesState(TypedDict):
    messages: Annotated[List, add_messages]

def chat_node_1(state: AddMessagesState) -> dict:
    return {
        "messages": [(
            "assistant", "Hello from node 1"
        )]
    }

def chat_node_2(state: AddMessagesState) -> dict:
    return {
        "messages": [(
            "assistant", "Hello from node 2"
        )]
    }

def run_demo():
    print("2. add_messages Reducer（消息列表专用）演示:")
    builder = StateGraph(AddMessagesState)
    builder.add_node(chat_node_1)
    builder.add_node(chat_node_2)
    builder.add_edge(START, "chat_node_1")
    builder.add_edge(START, "chat_node_2")
    builder.add_edge("chat_node_1", END)
    builder.add_edge("chat_node_2", END)
    graph = builder.compile()

    result = graph.invoke({"messages": [("user", "Hi there!")]})
    print(f"初始状态: {{'messages': [('user', 'Hi there!')]}}")
    print(f"执行结果：{result}")

if __name__ == '__main__':
    run_demo()