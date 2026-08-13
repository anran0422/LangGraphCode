import operator
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

class MyState(TypedDict):
    messages: Annotated[list, operator.add]

def node_1(state: MyState):
    return {
        "messages":["abc","def"]
    }

def main():

    # 数据存储到 sqlite_data 目录下面，需要目录存在
    conn = sqlite3.connect(database="./sqlite_data/langgraph_sqlite", check_same_thread=False)
    memory = SqliteSaver(conn=conn)

    builder = StateGraph(MyState)
    builder.add_node(node_1)
    builder.add_edge(START, "node_1")
    builder.add_edge("node_1", END)

    graph = builder.compile(checkpointer=memory)

    config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    initial_state = graph.get_state(config)
    print(f"初始状态：{initial_state}")

    # 执行图
    result = graph.invoke({"messages":[]}, config)
    print(f"Result: {result}")

    # 查看执行之后的状态
    final_state = graph.get_state(config)
    print(f"Final state: {final_state}")

    conn.close()

if __name__ == '__main__':
    main()