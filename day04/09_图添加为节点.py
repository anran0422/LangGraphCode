from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 定义共享状态
class State(TypedDict):
    text: str
    result: str

# 定义子图节点
def process_text(state: State):
    print("执行子图：process_text")
    return {
        "result": state["text"] + " -> 已处理"
    }

# 封装：创建子图
def create_subgraph():
    builder = StateGraph(State)

    builder.add_node(process_text)
    builder.add_edge(START, "process_text")
    builder.add_edge("process_text", END)

    return builder.compile()

def node_prepare(state: State):
    print("执行节点：node_prepare")
    return {
        "text": state["text"] + " 处理冒号: "
    }


# 封装：创建父图
def create_parent_graph():
    builder = StateGraph(State)

    builder.add_node(node_prepare)
    builder.add_node("subgraph", create_subgraph()) # 子图整个图作为节点，这也是我们之前学过的

    builder.add_edge(START, "node_prepare")
    builder.add_edge("node_prepare", "subgraph")
    builder.add_edge("subgraph", END)

    return builder.compile()

# 主函数：执行流程
def main():
    parent_graph = create_parent_graph()
    result = parent_graph.invoke({
        "text": "Hello LangGraph"
    })
    print(f"最终的执行结果：{result}")

# 程序入口
if __name__ == "__main__":
    main()