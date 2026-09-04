import sqlite3
import uuid
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore
from langgraph.store.base import BaseStore


from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage

class ChatState(MessagesState):
    pass

def node_call_model(
        state: ChatState,
        config: RunnableConfig,
        *,
        store: BaseStore
):
    print("执行节点：node_call_model")

    # 从配置中获取用户id
    user_id = config["configurable"]["user_id"]
    namespace = ("memories", user_id)

    # 从存储中搜索相关记忆
    try:
        memories = store.search(namespace,
                                query=str(state['messages'][-1].content))
        info = "\n".join([d.value['data'] for d in memories])
        print(f"检索到的记忆：{info}")
    except Exception as e:
        print(f"检索记忆时发生错误：{e}")
        info = ""

    system_msg = f"你是一个小助手，用户信息:{info}" if info else "你是一个小助手"
    print(f"系统消息：{system_msg}")

    # 检查用户是否要求记住某些信息
    last_message = state["messages"][-1]
    if "记住" in last_message.content.lower() or "remember" in last_message.content.lower():
        # 提取需要记住的信息（简化处理）
        memory = "用户的名字是张三" if "张三" in last_message.content else "用户要求记住一些信息"
        try:
            store.put(namespace, str(uuid.uuid4()), {"data": memory})
            print(f"已存储记忆：{memory}")
        except Exception as e:
            print(f"存储记忆失败：{e}")

    #生成回复（模拟回复代替模型实际调用）
    user_message = last_message.content
    if "你好" in user_message or "hello" in user_message.lower():
        response = f"你好，我是AI助手，有什么我可以帮助你的吗？"
    elif "记住" in user_message or "remember" in user_message.lower():
        response = f"好的，我已经记住了你说的信息。"
    elif "名字" in user_message or "name" in user_message.lower():
        if info:
            response = f"根据我的记忆，你的名字是张三。"
        else:
            response = f"我还不知道你的名字，能告诉我吗？"

    print(f"生成的回复是: {response}")
    return {
        "messages": [AIMessage(content=response)]
    }

def create_graph():
    builder = StateGraph(ChatState)

    builder.add_node(node_call_model)
    builder.add_edge(START, "node_call_model")
    builder.add_edge("node_call_model", END)

    return builder

def main():
    print(f"=== SQLite 长期记忆演示 === \n")

    DB_PATH = "./sqlite_data/long_term_memory.db"

    # 使用上下文管理器保证正确初始化和清理资源
    with(
        SqliteStore.from_conn_string(DB_PATH) as store,
        SqliteSaver.from_conn_string(DB_PATH) as checkpointer,
    ):
        builder = create_graph()
        graph = builder.compile(
            checkpointer=checkpointer,
            store=store
        )

        # 第一次对话——要求记住信息
        print("第一次对话——要求记住信息")

        config1 = {
            "configurable": {
                "thread_id": "1",
                "user_id": "user_123"
            }
        }

        for chunk in graph.stream(
                {"messages": [HumanMessage(content="你好！请记住我的名字是张三！")]},
            config=config1,
            stream_mode="values"
        ):
            if chunk["messages"]:
                last_message = chunk["messages"][-1]
                if hasattr(last_message, 'content'):
                    print(f"    {type(last_message).__name__}: {last_message.content}")
                else:
                    print(f"    {type(last_message).__name__}: {last_message}")
            print()

        # 第二次对话——查询记忆
        print("第二次对话——查询记忆")
        config2 = {
            "configurable": {
                "thread_id": "2",
                "user_id": "user_123"
            }
        }
        for chunk in graph.stream(
                {"messages": [HumanMessage(content="我的名字是什么？")]},
                config=config2, # 线程不同了，看能否查到
                stream_mode="values"
        ):
            if chunk["messages"]:
                last_message = chunk["messages"][-1]
                if hasattr(last_message, 'content'):
                    print(f"    {type(last_message).__name__}: {last_message.content}")
                else:
                    print(f"    {type(last_message).__name__}: {last_message}")
            print()

        # 第三次对话——不同用户
        print("第三次对话——不同用户")
        config3 = {
            "configurable": {
                "thread_id": "3",
                "user_id": "user_456"
            }
        }
        for chunk in graph.stream(
                {"messages": [HumanMessage(content="我的名字是什么？")]},
                config=config3,  # 线程和用户同时改变
                stream_mode="values"
        ):
            if chunk["messages"]:
                last_message = chunk["messages"][-1]
                if hasattr(last_message, 'content'):
                    print(f"    {type(last_message).__name__}: {last_message.content}")
                else:
                    print(f"    {type(last_message).__name__}: {last_message}")
            print()

if __name__ == '__main__':
    main()