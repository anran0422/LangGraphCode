
from day01作业.practice01.state import *

def node_calc(state: State) -> CalOutput:
    print("这是计算节点")
    return {
        "private_data": state['res'] * state['res']
    }

def node_output(state: NodeOutputInput) -> State:
    print("这是展示结果节点")
    print(f"计算结果为: {state['private_data']}")
    return {
        'res': state['private_data']
    }