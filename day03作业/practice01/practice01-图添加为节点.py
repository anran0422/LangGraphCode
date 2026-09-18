from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    name: str
    age: int
    gender: str
    height: float

class ChildState(TypedDict):
    age: int
    gender: str
    height: float

def sub_node_1(_state: ChildState):
    print("这里是在执行 sub_node_1")
    print("这里要进行的操作是：添加年龄")
    age = int(input("这里输入您的年龄："))

    return {
        "age": age
    }


def sub_node_2(_state: ChildState):
    print("这里是在执行 sub_node_2")
    print("这里要进行的操作是：添加性别")
    gender = input("这里输入您的性别：")

    return {
        "gender": gender
    }


def sub_node_3(_state: ChildState):
    print("这里是在执行 sub_node_3")
    print("这里要进行的操作是：添加身高")
    height = float(input("这里输入您的身高："))

    return {
        "height": height
    }

def create_subgraph():

    builder = StateGraph(ChildState)

    builder.add_node(sub_node_1)
    builder.add_node(sub_node_2)
    builder.add_node(sub_node_3)

    builder.add_edge(START, "sub_node_1")
    builder.add_edge("sub_node_1", "sub_node_2")
    builder.add_edge("sub_node_2", "sub_node_3")
    builder.add_edge("sub_node_3", END)

    return builder

def node_output(_state: State):
    print("这里是父图的输出节点：node_output")
    print("下面要输出子图的各个节点的状态：")


def create_graph():

    builder = StateGraph(State)

    builder.add_node("subgraph" ,create_subgraph().compile())
    builder.add_node(node_output)

    builder.add_edge(START, "subgraph")
    builder.add_edge("subgraph", "node_output")
    builder.add_edge("node_output", END)

    return builder

def main():

    memory = InMemorySaver()

    config = {
        "configurable": {
            "thread_id": "sub_node01"
        }
    }

    builder = create_graph()
    graph = builder.compile(checkpointer=memory)

    initial_input = {
        "name": "将子图添加为父图节点"
    }

    for chunk in graph.stream(initial_input ,stream_mode="values", config=config,
                              subgraphs=True):
        print()
        print(f"当前子节点输出：{chunk}")

if __name__ == '__main__':
    main()

