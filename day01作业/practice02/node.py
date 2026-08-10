from langchain_core.runnables import RunnableConfig

from day01作业.practice02.state import State

def node_1(state: State):
    print(f"当前是节点 node_1，累计节点数为 {state['node_count']}")
    return {
        "node_count": 1
    }

def node_2(state: State):
    print(f"当前是节点 node_2，累计节点数为 {state['node_count']}")
    return {
        "node_count": 1
    }

def node_3(state: State):
    print(f"当前是节点 node_3，累计节点数为 {state['node_count']}")
    return {
        "node_count": 1
    }

def node_4(state: State):
    print(f"当前是节点 node_4，累计节点数为 {state['node_count']}")
    return {
        "node_count": 1
    }

def node_5(state: State, config: RunnableConfig):
    print(f"当前是节点 node_5，为延迟节点，累计节点数为 {state['node_count']}")
    print(f"当前超步为第 {config['metadata']['langgraph_step']} 个超步")
    return {
        "node_count": 1
    }