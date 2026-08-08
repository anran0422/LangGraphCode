"""
LangGraph Reducer函数演示 - 自定义Reducer函数
"""

from typing import Annotated, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


# 9. 自定义 Reducer 函数
def custom_reducer(current_value: Dict[str, Any], new_value: Dict[str, Any]) -> Dict[str, Any]:
    """合并两个字典，新值会覆盖旧值，但保留旧值中不存在的键"""
    result = current_value.copy()
    result.update(new_value)
    return result

class CustomReducerState(TypedDict):
    metadata:Annotated[Dict[str, Any], custom_reducer]

def update_metadata(graph: StateGraph) ->dict:
    return {
        "metadata": {
            "timestamp": "2026-08-08",
            "version": "1.0.0"
        }
    }

def run_demo():
    print("9. 自定义Reducer演示:")
    builder = StateGraph(CustomReducerState)
    builder.add_node(update_metadata)
    builder.add_edge(START, "update_metadata")
    builder.add_edge("update_metadata", END)

    graph = builder.compile()
    result = graph.invoke({
        "metadata": {
            "user_id": "123456",
            "session_id": "abcdefg"
        }
    })
    print(f"初始结果:{
    {
        "metadata": {
            "user_id": "123456",
            "session_id": "abcdefg"
        }
    }
    }")
    print(f"执行结果：{result}")

if __name__ == '__main__':
    run_demo()