from typing import TypedDict, Annotated
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

import operator

class State(TypedDict):
    state_1 : str
    state_2 : Annotated[list, operator.add]

def node_1(state: State):
    print("entering node_1")

    res = interrupt({
        "key_1": "value_1",
        "key_2": "value_2"
    })

    return {
        "state_2": res
    }

def create_graph():
    builder = StateGraph(State)

    builder.add_node(node_1)
    builder.add_edge(START, "node_1")
    builder.add_edge("node_1", END)

    return builder

def main():
    builder = create_graph()

    memory = InMemorySaver()

    graph = builder.compile(checkpointer=memory)

    config = {
        "configurable": {
            "thread_id": "thread01"
        }
    }

    print("=====第一次中断执行=====")
    result = graph.invoke({
        "state_1": "test",
        "state_2": ["1"]
    }, config=config)
    print(f"第一次执行结果：{result}")
    # {'state_1': 'test', 'state_2': ['1'],
    # '__interrupt__': [Interrupt(value={'key_1': 'value_1', 'key_2': 'value_2'},
    # id='15ac35fd50a68b89b8b02d7337ffd826')]}

    print("=====第二次恢复执行=====")
    result = graph.invoke(Command(resume=["这是给中断操作的返回值"]),
                          config=config)
    print(f"第二次执行结果：{result}")

if __name__ == '__main__':
    main()