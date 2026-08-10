from langgraph.graph import StateGraph,START,END
from day01作业.practice01.state import State
from day01作业.practice01.node import *

builder = StateGraph(State)

builder.add_node(node_calc)
builder.add_node(node_output)

builder.add_edge(START, "node_calc")
builder.add_edge("node_calc", "node_output")
builder.add_edge("node_output", END)

graph = builder.compile()

result = graph.invoke({'res': 3})
print(f"输出为 {result}")