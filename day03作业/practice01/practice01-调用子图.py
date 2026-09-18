from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    user_question: str
    answer: str

class ChildState(TypedDict):
    input: str
    result: str

def sub_node_1(state: ChildState):
    print("这里是在执行 sub_node_1")
    print(f"接收输入: {state['input']}")
    # return {} 不是为了“让节点正常运行”而强制写的，而是因为这个节点执行后没有任何 State 更新。
    return {}

def sub_node_2(state: ChildState):
    print("这里是在执行 sub_node_2")
    print("处理输入")
    return {
        "result": state["input"] + "---> 已处理"
    }

def sub_node_3(state: ChildState):
    print("这里是在执行 sub_node_3")
    print(f"返回处理结果：: {state['result']}")

    result = f"最终处理结果：{state['result']}"

    return {
        "result": result
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


def node_1(state: State):

    print("这里是父图的 node_1")

    # 调用子图
    def call_subgraph(state):
        # 父图状态 ——> 子图
        user_question = state["user_question"]

        sub_graph = create_subgraph().compile()
        # 拿到子图的处理结果
        result = sub_graph.invoke({
            "input": user_question
        })

        # 子图 ——> 父图
        return {
            "answer": result
        }
    # 执行嵌套函数
    call_subgraph(state)

def node_output(_state: State):
    print("这里是父图的输出节点：node_output")

def create_graph():

    builder = StateGraph(State)

    builder.add_node(node_1)
    builder.add_node(node_output)

    builder.add_edge(START, "node_1")
    builder.add_edge("node_1", "node_output")
    builder.add_edge("node_output", END)

    return builder

def main():
    memory = InMemorySaver()
    builder = create_graph()
    config = {
        "configurable": {
            "thread_id": "sub_node02"
        }
    }
    graph = builder.compile(checkpointer=memory)

    for chunk in graph.stream({
        "user_question":" 我们以后能去到火星上吗？"
        },
        stream_mode="values",
        config=config,
        subgraphs=True
    ):
        print(f"该节点的输出信息：{chunk}")

if __name__ == '__main__':
    main()