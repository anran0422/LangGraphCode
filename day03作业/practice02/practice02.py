import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import  InMemorySaver

class State(TypedDict):
    input: str
    result: Annotated[list, operator.add]

def node_input_interrupt(_state: State):
    print("这里是执行节点 node_input_interrupt")

    res = interrupt({ # 这里中断会向外部暴露值
        "key_1": "这里是key1",
        "key_2": "这里是key2"
    })

    return {"result": [res]}

def node_output(state: State):
    print("这里是执行节点 node_output")
    print(f"中断后的返回值是: {state['result']}")



def create_graph():
    builder = StateGraph(State)

    builder.add_node(node_input_interrupt)
    builder.add_node(node_output)

    builder.add_edge(START, "node_input_interrupt")
    builder.add_edge("node_input_interrupt", "node_output")
    builder.add_edge("node_output", END)

    return builder

def main():
    memory = InMemorySaver()
    builder = create_graph()
    graph = builder.compile(checkpointer=memory)

    config = {
        "configurable": {
            "thread_id": "practice02"
        }
    }
    # 中断的输出结果
    interrupt_res = graph.invoke({}, config=config)
    print(f"这里是第一次执行结果：{interrupt_res}，被中断")

    # 第二次执行
    res = graph.invoke(Command( resume="恢复输入的中断返回值"), config=config)
    print(f"这里是第二次执行结果：{res}，重新从中断节点处开始执行")

if __name__ == "__main__":
    main()
