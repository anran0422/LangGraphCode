"""
LangGraph 工具中的自定义数据流式传输演示
展示如何从工具内部发送自定义用户定义数据
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.config import get_stream_writer
from langchain.tools import tool

@tool
def query_database(query: str):
    """查询数据库工具"""
    # 访问流写入器以发送自定义数据
    writer = get_stream_writer()

    writer({"data":"开始查询数据库", "type": "info"})
    writer({"data":"Retrieved 0/100 records", "type": "progress"})

    # 模拟执行查询
    # 发送更多自定义数据
    writer({"data":"Retrieved 50/100 records", "type": "progress"})
    writer({"data":"Retrieved 100/100 records", "type": "progress"})
    writer({"data":"查询完成", "type": "info"})

    return f"查询 {query} 的结果：找到25条匹配记录"

class State(TypedDict):
    query: str
    result: str


# 这个节点函数定义在外面，不也是一样的吗？只是需要调用工具而已？
# 这是因为实例中， 将这个节点放在了 create_graph_with_tool 中
def node_tool(state: State):

    # 直接在节点中使用工具
    result = query_database.invoke(state["query"])
    return {"data": result}

def create_graph_with_tool():

    builder = StateGraph(State)
    builder.add_node(node_tool)
    builder.add_edge(START, "node_tool")
    builder.add_edge("node_tool", END)

    return builder.compile()

def graph_api_demo():
    print("\n" + "=" * 60 + "\n")
    print("=== LangGraph API 中的自定义数据流式传输演示 === \n")

    graph = create_graph_with_tool()

    inputs = {"query": "产品信息", "result": ""}

    print("--- 从工具中流式传输自定义数据 ---")
    try:
        # stream_mode="custom" 在流中接收自定义数据
        for mode, chunk in graph.stream(inputs, stream_mode=["custom", "updates"]):
            if mode == "custom":
                print(f"【自定义数据】: {chunk}")
            elif mode == "updates":
                print(f"【状态更新】: {chunk}")
    except Exception as e:
        print(f"错误：{e}")

def main():
    graph_api_demo()

    print("\n" + "=" * 60 + "\n")
    print("说明")
    print("1. 自定义数据流允许从节点或工具内部发送用户定义的数据")
    print("2. 使用 get_stream_writer() 获取流写入器")
    print("3. 可以发送进度更新、日志信息等任何自定义数据")
    print("4. 在流式传输时设置 stream_mode='custom' 或包含 'custom' 的模式列表")


if __name__ == '__main__':
    main()