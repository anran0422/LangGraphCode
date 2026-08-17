from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# 定义子图状态
class SubgraphState(TypedDict):
    foo: str # 这个键和父图状态共享
    bar: str

def sub_node_1(state: SubgraphState):
    print(f"执行子图节点 1， 当前状态：{state}")
    return {"bar": "bar"}

def sub_node_2(state: SubgraphState):
    print(f"执行子图节点 2， 当前状态：{state}")
    return {
        "foo": state["foo"] + state["bar"]
    }

# 定义父图状态
# LangGraph 的 reducer 是用来定义同一个状态 key 收到多个更新时如何合并的。
class State(TypedDict):
    foo: str # 共享不 Reducer？

def node_1(state: State):
    print(f"执行父图节点 1， 当前状态：{state}")
    return {
        "foo": "hi!" + state["foo"]
    }

def create_subgraph():
    sub_builder = StateGraph(SubgraphState)

    sub_builder.add_node(sub_node_1)
    sub_builder.add_node(sub_node_2)

    sub_builder.add_edge(START, "sub_node_1")
    sub_builder.add_edge("sub_node_1", "sub_node_2")
    sub_builder.add_edge("sub_node_2", END)
    return sub_builder.compile()

def create_graph():
    builder = StateGraph(State)

    builder.add_node(node_1)
    builder.add_node("sub_graph", create_subgraph())

    builder.add_edge(START, "node_1")
    builder.add_edge("node_1", "sub_graph")
    builder.add_edge("sub_graph", END)

    return builder.compile()

def main():
    graph = create_graph() # 父图子图都创建好了

    print("--- 1. 不包含子图的常规流式输出 ---")
    for chunk in graph.stream({"foo" : "这是foo"}, stream_mode="updates"):
        print(f"输出流式块：{chunk}")
    print("\n" + "=" * 50 + "\n")

    print("--- 2. 包含子图的流式输出 (subgraphs=True) ---")
    for chunk in graph.stream({"foo":"这是foo"},
                              stream_mode="updates",
                              subgraphs=True): # 同时输出子图
        print(f"输出流式块：{chunk}")
    print("\n" + "=" * 50 + "\n")

    print("--- 3. 使用 values 模式并包含子图输出 ---")
    for chunk in graph.stream(
            {"foo":"这是foo"},
            stream_mode="values",
            subgraphs=True): # 同时输出子图
        print(f"输出流式块：{chunk}")
    print("\n" + "=" * 50 + "\n")

    print("--- 4. 详细分析子图流式输出 ---")
    print("当 subgraphs=True 时，输出格式为 (namespace, chunk) 元组:")
    for chunk in graph.stream(
            {"foo":"这是foo"},
            stream_mode="values",
            subgraphs=True):  # 同时输出子图
        namespace,data = chunk
        if namespace:
            print(f"子图 {namespace[0]}输出：{data}")
        else:
            print(f"父图输出: {data}")

if __name__ == '__main__':
    main()