import time
from langgraph.graph import START,END,StateGraph
from typing_extensions import TypedDict
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

# 定义状态
class State(TypedDict):
    x: int
    result: int

# 创建图
builder = StateGraph(State)

# 创建节点
def expensive_node(state: State) -> dict[str, int]:
    time.sleep(2)
    return {"result": state['x'] * 2}

# 添加节点，并且设置缓存策略
builder.add_node(expensive_node, cache=CachePolicy(ttl=3))

# 设置入口和出口
# 两段相同意思的代码
# builder.set_entry_point("expensive_node")
# builder.set_finish_point("expensive_node")
builder.add_edge(START, "expensive_node")
builder.add_edge("expensive_node", END)

# 编译
graph = builder.compile(cache=InMemoryCache())

# 执行图
print(graph.invoke({"x": 5}, stream_mode="updates"))

# 第二次利用缓存并快速返回
print(graph.invoke({"x": 5}, stream_mode="updates"))