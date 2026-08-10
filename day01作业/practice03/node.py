from day01作业.practice03.state import State

# 偶数处理
def node_even_process(state: State):
    print("当前输入状态为偶数")

# 奇数处理
def node_odd_process(state: State):
    print("当前输入状态为奇数")


# 双倍处理
def node_double_process(state: State):
    return {
        "x": state['x'] * 2
    }

# 双倍处理
def node_plus1_process(state: State):
    return {
        "x": state['x'] + 1
    }