from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    data01: str
    data02: str
    data03: str
    data04: str

def node_01(_state: State):
    print("开始执行 node_01")

    return {
        "data01": "this is the first data"
    }


def node_02(_state: State):
    print("开始执行 node_02")

    return {
        "data02": "this is the second data"
    }

version = 1

def node_03(_state: State):
    print("开始执行 node_03")
    if version == 1:
        return {
            "data03": "this is the third data"
        }

    return {
        "data03": "这是时间旅行后重新生成的数据 data03"
    }


def node_04(_state: State):
    print("开始执行 node_04")

    return {
        "data04": "this is the fourth data"
    }

def create_graph():
    builder = StateGraph(State)

    builder.add_node(node_01)
    builder.add_node(node_02)
    builder.add_node(node_03)
    builder.add_node(node_04)

    builder.add_edge(START, "node_01")
    builder.add_edge("node_01", "node_02")
    builder.add_edge("node_02", "node_03")
    builder.add_edge("node_03", "node_04")
    builder.add_edge("node_04", END)

    return builder

def main():
    global version

    memory = InMemorySaver()
    builder = create_graph()
    graph = builder.compile(checkpointer=memory)

    version = 1
    config = {"configurable":{"thread_id":"practice03"}}
    res = graph.invoke({}, config=config)
    print(f"第一次完整执行的结果: {res}")

    # 获取历史
    history_state = list(
        graph.get_state_history(config=config)
    )

    for i, state in enumerate(history_state):
        print(f"这里是第 {i+1} 个节点")
        print(f"当前节点状态是: {state}")

    print("开始时间旅行")
    version = 2
    past_2_state = history_state[2]

    print(f"回溯节点的下一个节点: {past_2_state.next}")
    # 该如何重新生成一个数据回传呢？
    for chunk in graph.stream(None, stream_mode="values",
                         config=past_2_state.config):
        print(f"这是执行时间旅行各节点的执行过程：{chunk}")

if __name__ == '__main__':
    main()