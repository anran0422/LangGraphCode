import operator
from typing import TypedDict, Literal, Annotated, NotRequired
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command


class State(TypedDict):
    x: int
    add_res: NotRequired[int]
    mul_res: NotRequired[int]
    sub_res: NotRequired[int]
    div_res: NotRequired[float]

def node_1(state: State) -> Command[Literal["node_even", "node_odd"]]:
    x = state['x']
    if x % 2 == 0:
        print("当前为偶数，进入偶数节点，计算 - /")
        return Command(
            goto="node_even"
        )

    print("当前为奇数，进入偶数节点，计算 + *")
    return Command(

        goto="node_odd"
    )

def node_even(_state: State) -> Command[Literal["node_sub", "node_div"]]:
    return Command(
        goto=["node_sub", "node_div"]
    )

def node_odd(_state: State) -> Command[Literal["node_add", "node_mul"]]:
    return Command(
        goto=["node_add", "node_mul"]
    )

def node_add(state: State):
    return {
        "add_res": state["x"] + 2
    }

def node_mul(state: State):
    return {
        "mul_res": state["x"] * 2
    }

def node_sub(state: State):
    return {
        "sub_res": state["x"] - 2
    }

def node_div(state: State):
    return {
        "div_res": state["x"] / 2
    }

def create_graph() -> StateGraph:
    builder = StateGraph(State)

    builder.add_node(node_1)
    builder.add_node(node_even)
    builder.add_node(node_odd)
    builder.add_node(node_add)
    builder.add_node(node_mul)
    builder.add_node(node_sub)
    builder.add_node(node_div)

    builder.add_edge(START, "node_1")
    builder.add_edge(
        ["node_add",
         "node_mul",
         "node_sub",
         "node_div"], END
    )

    return builder

def main():

    builder = create_graph()
    graph = builder.compile()

    result = graph.invoke({
        "x": 3
    })

    print(f"最终结果: {result}")

if __name__ == '__main__':
    main()