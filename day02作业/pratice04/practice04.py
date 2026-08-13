import operator
from typing import TypedDict, Annotated, Sequence, List, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

class State(TypedDict):
    scores: List[float]
    result: Annotated[List[str], operator.add]

class JudgeState(TypedDict):
    score: float

def node_input(state: State):
    print("填写成绩")
    scores = [89, 38, 68, 55, 90]
    return {
        "scores": scores
    }

def send_input_to_judge(state: State) -> Sequence[Send]:
    """ 条件边发送去 评判成绩是否合格"""
    print("执行条件边函数")
    scores = state['scores']
    send_list = [Send("node_judge", {"score": score}) for score in scores]

    return send_list

def node_judge(state: JudgeState):
    """评判成绩是否合格"""

    # send 发送过来的中间状态
    score = state['score']
    print(f"开始评估成绩: {score}")

    if score < 0 or score > 100:
        print("成绩不合法，请重新输入")
        return {
            "result": ["成绩不合法，请重新输入"]
        }
    elif score < 60:
        print("不及格")
        return {
            "result": ["不及格"]

        }
    else:
        print("及格")
        return  {
            "result": ["及格"]
        }

def create_graph():
    builder = StateGraph(State)

    builder.add_node(node_input)
    builder.add_node(node_judge)

    builder.add_edge(START, "node_input")
    builder.add_conditional_edges(
        "node_input",
        send_input_to_judge
    )
    builder.add_edge("node_judge", END)

    return builder

def main():
    builder = create_graph()

    graph = builder.compile()
    result = graph.invoke({})
    print(f"最终结果：{result}")

if __name__ == '__main__':
    main()