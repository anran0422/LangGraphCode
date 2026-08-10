from day01作业.practice02_拓展.state import State

def node_1(state: State):
    print("当前执行节点 node_1")
    return {
        "step": ["当前执行节点 node_1"]
    }

def node_2(state: State):
    print("当前执行节点 node_2")
    return {
        "step": ["当前执行节点 node_2"]
    }

def node_3(state: State):
    print("当前执行节点 node_3")
    return {
        "step": ["当前执行节点 node_3"]
    }

def node_4(state: State):
    print("当前执行节点 node_4")
    return {
        "step": ["当前执行节点 node_4"]
    }

def node_5(state: State):
    print("当前执行第一个延迟节点： node_5")
    return {
        "step": ["当前执行节点 node_5"]
    }

def node_6(state: State):
    print("当前执行第二个延迟节点： node_6")
    return {
        "step": ["当前执行节点 node_6"]
    }