"""
LangGraph 高级表单验证演示

该演示展示了如何验证来自人类的多个输入字段，
如果输入无效，就再次询问。通过在循环中多次调用 interrupt 来实现这一点。
"""

import sqlite3
from typing import TypedDict
from langgraph.graph import START,StateGraph,END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt

class AdvancedState(TypedDict):
    """高级表单状态定义"""
    name: str | None
    age: int | None
    email: str | None

def node_get_name(state: AdvancedState):
    print("执行节点 node_get_name")

    prompt = "请输入您的名称："
    while True:
        answer = interrupt(prompt)
        print(f"收到用户输入: {answer}")

        if isinstance(answer, str) and len(answer.strip()) > 0:
            name = answer.strip()
            print(f"姓名验证通过: {name}")

            return {"name": name}

        prompt = "姓名不能为空，请重新输出："

def node_get_age(state: AdvancedState):
    print("执行节点 node_get_age")

    prompt = f"您好 {state['name']}, 请输入您的年龄："
    while True:
        answer = interrupt(prompt)
        print(f"收到用户输入: {answer}")

        if isinstance(answer, int) and answer > 0:
            print(f"年龄验证通过: {answer}")
            return {"age": answer}

        # 尝试转化字符串为证书
        if isinstance(answer, str):
            try:
                age_int = int(answer)
                if age_int > 0:
                    print(f"年龄验证通过: {age_int}")
                    return {"age": age_int}
            except ValueError:
                pass

        prompt = f"年龄 '{answer}' 无效，请输入一个正整数："

def node_get_email(state: AdvancedState):
    print("执行节点 node_get_email")

    prompt = f"您好 {state['name']}（{state['age']}岁）, 请输入您的邮箱地址："
    while True:
        answer = interrupt(prompt)
        print(f"收到用户输入: {answer}")

        # 简单验证一下邮箱的格式
        if isinstance(answer, str) and "@" in answer and "." in answer:
            email = answer.split()
            print(f"邮箱验证通过: {email}")
            return {"email": email}

        prompt = f" '{answer}' 是一个无效的邮箱地址，请输入正确的邮箱格式（example@domain.com）:"


def create_graph():
    builder = StateGraph(AdvancedState)

    builder.add_node(node_get_name)
    builder.add_node(node_get_age)
    builder.add_node(node_get_email)

    builder.add_edge(START, "node_get_name")
    builder.add_edge("node_get_name", "node_get_age")
    builder.add_edge("node_get_age", "node_get_email")
    builder.add_edge("node_get_email", END)

    return builder

def main():

    # 内存保存为检查点
    memory = MemorySaver()

    builder = create_graph()
    graph = builder.compile(checkpointer=memory)

    # 执行时候的配置
    config = {
        "configurable": {
            "thread_id": "advanced-01"
        }
    }

    # 初始化状态并执行图
    print("1. 启动高级表单收集工作流...")
    try:
        # 收集姓名
        state_after_name = graph.invoke({"name": None, "age": None, "email": None}, config=config)
        print(f"工作流中断信息: {state_after_name['__interrupt__']}\n")
        # 输入有效姓名
        print("2. 输入有效姓名...")
        state_after_name = graph.invoke(Command(resume="张三"), config=config)
        print(f"工作流中断信息: {state_after_name['__interrupt__']}\n")

        # 输入无效年龄
        print("3. 输入无效年龄...")
        state_after_invalid_age = graph.invoke(Command(resume="二十"), config=config)
        print(f"工作流中断信息: {state_after_invalid_age['__interrupt__']}\n")

        # 输入有效年龄
        print("4. 输入有效年龄...")
        state_after_age = graph.invoke(Command(resume=25), config=config)
        print(f"工作流中断信息: {state_after_age['__interrupt__']}\n")

        # 输入无效邮箱
        print("5. 输入无效邮箱...")
        state_after_invalid_email = graph.invoke(Command(resume="zhangsan"), config=config)
        print(f"工作流中断信息: {state_after_invalid_email['__interrupt__']}\n")

         # 输入有效邮箱
        print("6. 输入有效邮箱...")
        final_state = graph.invoke(Command(resume="zhangsan@example.com"), config=config)
        print(f"最终状态: {final_state}")
        print(f"姓名: {final_state['name']}")
        print(f"年龄: {final_state['age']}")
        print(f"邮箱: {final_state['email']}")
        print("\n=== 演示完成 ===")

    except Exception as e:
        print(f"执行过程中出现错误: {e}")
        print("\n=== 演示结束 ===")

if __name__ == '__main__':
    main()