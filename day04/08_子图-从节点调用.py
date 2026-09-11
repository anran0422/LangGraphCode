"""
    父图节点调用子图，本质是两个独立状态之间的数据搬运，不是"同一种状态模式"。
    LangGraph 不会自动帮你做字段映射，这一步必须你手动完成。
"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 1. 定义子图状态
class SubgraphState(TypedDict):
    text: str
    result: str

# 2. 定义子图节点
def subnode_process_text(state: SubgraphState):
    print("执行子图：process_text")
    return {
        "result": state["text"] + " -> 已处理"
    }

# 3. 定义子图
def create_subgraph():
    subgraph_builder = StateGraph(SubgraphState)
    subgraph_builder.add_node(subnode_process_text)
    subgraph_builder.add_edge(START, "subnode_process_text")
    subgraph_builder.add_edge("subnode_process_text", END)

    return subgraph_builder.compile()

# 4. 定义父图状态
class ParentState(TypedDict):
    user_input: str
    answer: str

# 5. 父图节点
def node_1(state: ParentState):
    print("这是父图节点 node_1")
    def call_subgraph(state: ParentState):
        print("在父图节点 node_1 中进行调用：call_subgraph")

        # 父图状态 → 子图状态
        subgraph_input = {
            "text": state["user_input"]
        }
        subgraph = create_subgraph()
        # 调用子图
        subgraph_result = subgraph.invoke(subgraph_input)
        # 子图状态 → 父图状态
        return {
            "answer": subgraph_result["result"]
        }

    return call_subgraph(state)

# 6. 创建父图
def create_graph():
    builder = StateGraph(ParentState)
    builder.add_node(node_1)

    builder.add_edge(START, "node_1")
    builder.add_edge("node_1", END)

    return builder.compile()

# 7. 执行
def main():
    print("这是最后的执行，把所有的都串起来了")
    graph = create_graph()
    result = graph.invoke({
        "user_input": "Hello LangGraph"
    })
    print(result)

if __name__ == '__main__':
    main()