"""
    这段代码可以给 AI 去更改一下末尾的输出，输出格式会好一点
"""

from typing import TypedDict
from langgraph.graph import StateGraph,START,END
from langchain.chat_models import init_chat_model

# 这是我自己的代码
model = init_chat_model(
    model="qwen3.8-max",
    model_provider="openai",
    api_key="sk-dc0d7cbe527941fe8975a095009b1c83",
    base_url="https://dashscope.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1",
    # 明确告诉 ChatOpenAI 使用 Responses API
    use_responses_api=True,
)

class State(TypedDict):
    query: str
    answer: str

def node_llm(state:State):
    print("开始调用 LLM")
    llm_result = model.invoke(
        [("user", state["query"])]
    )
    print("调用 LLM 结束")
    return {
        "answer": llm_result
    }

def main():
    graph = (
        StateGraph(
            state_schema=State
        )
        .add_node(node_llm)
        .add_edge(START, "node_llm")
        .compile()
    )
    inputs = {"query": "帮我生成一个300字的小学生作文，主题为我的一天"}
    for chunk, meta_data in graph.stream(inputs, stream_mode="messages"):
        print(chunk.content, end="")

if __name__ == '__main__':
    main()