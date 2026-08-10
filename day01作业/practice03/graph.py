from typing import Literal
from langgraph.graph import StateGraph,START,END
from day01作业.practice03.state import State
from day01作业.practice03.node import *


builder = StateGraph(State)

builder.add_node(node_even_process)
builder.add_node(node_odd_process)
builder.add_node(node_double_process)
builder.add_node(node_plus1_process)

# 问题：第一个是条件入口点还是，条件边呢？怎么算
# 条件边判断
def odd_even_judgment(state: State) -> Literal['even','odd']:
    print(f"输入是{state['x']},当前条件边是判断奇偶性")
    if state['x'] % 2 == 0:
        return 'even'
    return "odd"

# 第二个条件边判断
def is_greater5(state: State) -> Literal['double','plus']:
    print(f"输入是{state['x']},当前条件边是判断是否 > 5")
    if state['x'] > 5:
        print("现在是 > 5，进行双倍处理")
        return "double"

    print("现在是 <=5 ，进行 + 1处理")
    return "plus"

builder.add_conditional_edges(START, odd_even_judgment, {
    "even": "node_even_process",
    "odd": "node_odd_process"
})

builder.add_conditional_edges("node_even_process", is_greater5, {
    "double": "node_double_process",
    "plus": "node_plus1_process"
})

builder.add_conditional_edges("node_odd_process", is_greater5, {
    "double": "node_double_process",
    "plus": "node_plus1_process"
})

builder.add_edge("node_double_process", END)
builder.add_edge("node_plus1_process", END)

graph = builder.compile()
result = graph.invoke({"x" : 6})
print(f"最终结果为: {result}")
