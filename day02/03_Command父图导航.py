"""
LangGraph Command 父图导航演示

演示如何使用 Command 对象从子图导航到父图节点。
"""


"""
父图和子图的同名 State key 可以作为共享通道进行通信，而 child_data 只属于子图。官方子图文档也是这样描述的：
父图和子图存在共享 State key 时，可以直接把编译后的子图添加为父图节点。

所以你可以记成：

普通子图：父子图同名 State key 可以共享。

但如果子图使用 Command(graph=Command.PARENT, update=...) 主动向父图更新共享 key，那么父图中这些被更新的 key 要定义 Reducer。
"""
import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

def overwrite(old, new):
    return new

class FatherState(TypedDict):
    messages: Annotated[list, operator.add]
    task_status: Annotated[str, overwrite]
    subtask_result: Annotated[str, overwrite]

class ChildState(TypedDict):
    messages: Annotated[list, operator.add]
    task_status: str
    subtask_result: str
    child_data: str

# 父图节点：主控制器
def node_main_controller(state: FatherState) -> Command[Literal["node_subgraph"]]:
    """
        主控制器节点
        因为更新状态，又想导航，所以使用了 Command
        如果只是导航，可以普通连接，但是就没了更新状态
    """
    print("执行节点: main_controller (父图)")

    # 启动子任务
    return Command(
        update={
            "messages": [('system', '启动子任务')],
            "task_status": "subtask_started"
        },
        goto="node_subgraph"
    )

# 父图节点：任务结束
def node_finish_task(state: FatherState) -> dict:
    """任务结束节点"""
    print("执行节点: task_finisher (父图)")
    return {
        "messages": [('system', '任务完成')],
        "task_status": "completed"
    }

# 子图节点：数据处理器
# 不能写 Command[Literal['node_finish_task']]
# 子图中不存在这个节点，所以类型不需要写得很详细
def node_subgraph(state: ChildState) -> Command:
    """数据处理器节点（在子图中）"""
    print("执行节点: data_processor (子图)")

    processed_data = "处理后的数据"
    print(f"处理结果: {processed_data}")

    # 导航回父图的task_finisher节点
    return Command(
        update={
            "messages": [('subtask', f'子任务完成：{processed_data}')],
            "task_status": "subtask_finished",
            "subtask_result": processed_data
        },
        goto="node_finish_task",
        graph = Command.PARENT
    )

def create_subgraph() -> StateGraph:
    builder = StateGraph(ChildState)

    builder.add_node(node_subgraph)

    builder.add_edge(START, "node_subgraph")

    return builder.compile()

def main():
    builder = StateGraph(FatherState)

    builder.add_node(node_main_controller)
    builder.add_node(node_finish_task)
    builder.add_node("node_subgraph", create_subgraph()) # 创建子图作为节点

    builder.add_edge(START, "node_main_controller")

    # Command，本质可以认为就是一条件边，再多一个更新状态
    # 所以之前有导航，这里不需要再连接了
    # builder.add_edge("node_main_controller", "node_subgraph")

    graph = builder.compile()

    # 执行图
    initial_state = {
        "messages": [("user", "开始任务")],
        "task_status": "init",
        "subtask_result": ""
    }
    print("初始状态:", initial_state)
    result = graph.invoke(initial_state)
    print("最终状态:", result)

if __name__ == '__main__':
    main()