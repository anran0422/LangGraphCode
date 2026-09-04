"""
LangGraph 高级时间旅行演示

该演示展示了更复杂的时间旅行功能，包括：
1. 运行图并生成多个状态
2. 查看历史状态
3. 从不同历史点恢复执行
4. 比较不同执行路径的结果
"""

import uuid
from typing import TypedDict, NotRequired
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class StoryState(TypedDict):
    character: NotRequired[str]
    setting: NotRequired[str]
    plot: NotRequired[str]
    ending: NotRequired[str]

def node_create_character(_state: StoryState):
    print("执行节点 node_create_character")

    # 模拟LLM 调用
    mock_character = "会说话的猫"
    print(f"创建角色：: {mock_character}")
    return {"character": mock_character}

def node_set_setting(_state: StoryState):
    print("执行节点 node_set_setting")

    # 模拟LLM 调用
    mock_setting = "在图书馆里"
    print(f"创建场景：: {mock_setting}")
    return {"setting": mock_setting}

def node_set_plot(state: StoryState):
    print("执行节点 node_set_plot")

    # 模拟LLM 调用
    character = state.get("character", "未知人物")
    setting = state.get("setting", "未知场景")
    mock_plot = f"{character}在{setting}发现一本会发光的书"
    print(f"发展的剧情：: {mock_plot}")
    return {"plot": mock_plot}

def node_set_ending(state: StoryState):
    print("执行节点 node_set_ending")

    # 模拟LLM 调用
    plot = state.get("plot", "未知剧情")
    mock_ending = f"当{plot}时，整个图书馆被魔法光芒照亮了。"
    print(f"最终的结局：: {mock_ending}")
    return {"ending": mock_ending}

def create_graph():
    builder = StateGraph(StoryState)

    builder.add_node(node_create_character)
    builder.add_node(node_set_setting)
    builder.add_node(node_set_plot)
    builder.add_node(node_set_ending)

    builder.add_edge(START, "node_create_character")
    builder.add_edge("node_create_character", "node_set_setting")
    builder.add_edge("node_set_setting", "node_set_plot")
    builder.add_edge("node_set_plot", "node_set_ending")
    builder.add_edge("node_set_ending", END)

    return builder

def main():

    memory = MemorySaver()

    builder = create_graph()
    graph = builder.compile(checkpointer=memory)

    # 1. 运行图表生成第一个故事
    print("1. 生成第一个故事...")
    config1 = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
        }
    }

    story1 = graph.invoke({}, config1)
    print(f"角色: {story1['character']}")
    print(f"背景: {story1['setting']}")
    print(f"剧情: {story1['plot']}")
    print(f"结局: {story1['ending']}")
    print()

    # 2. 查看历史状态
    print("2. 查看第一个故事的历史状态...")
    states1 = list(graph.get_state_history(config1))

    print("历史状态:")
    for i, state in enumerate(states1):
        print(f" {i}. 下一步节点: {state.next}")
        print(f" 检查点ID: {state.config['configurable']['checkpoint_id']}")
        if state.values:
            print(f" 状态值: {state.values}")
    print()

    # 3. 从中间状态恢复执行，创建第二个故事
    # 时间旅行，选中要修改的状态，然后去更新即可
    print("3. 从中间状态恢复执行，创建第二个故事...")

    # 选择create_character执行后的状态
    character_state = states1[2] # 0（开始节点） 1 2
    print(f"选中的状态: {character_state.next}")
    print(f"选中的状态值: {character_state.values}")

    # 更新状态，改变角色
    new_config = graph.update_state(
        character_state.config,
        values= {"character": "会喷火的狗狗"}
    )
    print(f"新配置: {new_config}")
    print()

    # 4. 从新检查点恢复执行
    print("4. 从新检查点恢复执行，生成第二个故事...")
    story2 = graph.invoke(None, new_config)
    print(f"新角色: {story2['character']}")
    print(f"背景: {story2['setting']}")
    print(f"剧情: {story2['plot']}")
    print(f"结局: {story2['ending']}")
    print()

    # 5. 比较两个故事
    print("5. 比较两个故事:")
    print(" 故事1:")
    print(f" 角色: {story1['character']}")
    print(f" 背景: {story1['setting']}")
    print(f" 剧情: {story1['plot']}")
    print(f" 结局: {story1['ending']}")
    print()

    print(" 故事2:")
    print(f" 角色: {story2['character']}")
    print(f" 背景: {story2['setting']}")
    print(f" 剧情: {story2['plot']}")
    print(f" 结局: {story2['ending']}")
    print()

    print("=== 演示完成 ===")


if __name__ == '__main__':
    main()