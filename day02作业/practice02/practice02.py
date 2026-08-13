from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    x: int
    steps: Annotated[list, lambda x,y: x + y]


def node_calc(state: State):
    print("正在运行计算节点")
    return {
        "x": state['x'] * 2,
        "steps": ['正在运行计算节点']
    }

def node_output(state: State):
    print("正在运行输出节点")
    print(f"计算结果为：{state['x']}")
    return {
        "steps": [f"正在运行输出节点,计算结果为：{state['x']}"]
    }

def create_graph():
    builder = StateGraph(State)

    builder.add_node(node_calc)
    builder.add_node(node_output)

    builder.add_edge(START, "node_calc")
    builder.add_edge("node_calc", "node_output")
    builder.add_edge("node_output", END)

    return builder

def main():

    memory = InMemorySaver()
    config = {
        "configurable": {
            "thread_id": "thread01"
        }
    }

    builder = create_graph()
    graph = builder.compile(checkpointer=memory)

    print(f"第一次传入参数调用")
    result = graph.invoke({
        "x": 4
    }, config=config)
    print(f"第一次输出结果：{result}")
    print("=============================")

    print(f"检查保存的状态")
    saved_state = graph.get_state(config)
    print(f"检查保存的状态:{saved_state.values}")
    print("=============================")

    print(f"第二次调用，只传入线程 id")
    result = graph.invoke(None, config=config)
    print(f"第二次输出结果：{result}")

if __name__ == '__main__':
    main()
