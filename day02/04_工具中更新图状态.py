"""
LangGraph Command 工具内部状态更新演示

演示如何在工具内部使用 Command 对象更新图状态。
以客户支持应用程序为例，在对话开始时根据客户ID查询客户信息。
"""
import time
import random
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

class SupportState(TypedDict):
    customer_id: str
    customer_info: dict
    messages: Annotated[list, lambda x,y: x + y]
    issue_resolved: bool

# 模拟客户数据库
CUSTOMER_DATABASE = {
    "CUST001": {
            "name": "张三",
            "email": "zhangsan@example.com",
            "membership_level": "金牌会员",
            "account_status": "正常"
         },
         "CUST002": {
            "name": "李四",
            "email": "lisi@example.com",
            "membership_level": "银牌会员",
            "account_status": "正常"
        },
        "CUST003": {
            "name": "王五",
            "email": "wangwu@example.com",
            "membership_level": "普通会员",
            "account_status": "欠费"
        }
    }

# 工具函数：查询客户信息
def lookup_customer_info(customer_id: str) -> dict:
    """
        模拟查询客户信息的工具函数
        在实际应用中，这可能是一个API调用或数据库查询
    """
    print(f"正在查询客户ID: {customer_id} 的信息...")

    # 模拟网络延迟
    time.sleep(1)

    # 从数据库获取客户信息
    customer_info = CUSTOMER_DATABASE.get(customer_id, {})

    if customer_info:
        print(f"找到客户信息: {customer_info}")
    else:
        print(f"未找到客户ID: {customer_id} 的信息")
        customer_info = {"error": "客户未找到"}

    return customer_info


# 节点函数：客户信息查询工具
def node_customer_lookup_tool(state: SupportState) -> Command[Literal["node_support_agent"]]:
    """客户信息查询工具节点"""
    print("执行节点: customer_lookup_tool")

    customer_id = state["customer_id"]
    # 使用工具查询客户信息
    customer_info = lookup_customer_info(customer_id)

    # 使用Command更新状态并决定下一步
    return Command(
        update={
            "customer_info": customer_info,
            "messages":[("system", f"已查询客户 {customer_id} 的信息")]
        },
        goto="node_support_agent" # 找到跳转到客服代理节点
    )

# 节点函数：客服代理
def node_support_agent(state: SupportState) -> Command[Literal["__end__", "node_issue_resolved"]]:
    """客服代理节点"""
    print("执行节点: support_agent")

    customer_info = state["customer_info"]
    messages = state["messages"]

    # 检查是否找到客户信息
    if 'error' in customer_info:
        response = "抱歉，我们无法找到您的客户信息，请您确认提供的客户ID是否正确。"
        next_node = END
    else:
        # 根据客户等级提供个性化服务
        membership_level = customer_info.get("membership_level", "未知")
        name = customer_info.get("name", "客户xxx")

        if membership_level == "金牌会员":
            response = f"尊敬的金牌会员{name}，您好！我们非常重视您的问题，将优先为您处理。"
        elif membership_level == "银牌会员":
            response = f"{name}您好！我们会尽快为您解决问题。"
        else:
            response = f"{name}您好！感谢您的咨询。"

        # 模拟处理问题
        response += "\n\n我们已经收到您的问题，正在为您处理..."
        next_node = "node_issue_resolved"

    return Command(
        update={
            "messages": [("assistant", response)]
        },
        goto=next_node
    )

# 节点函数：问题解决器
def node_issue_resolved(state:SupportState) -> Command[SupportState]:
    """问题解决器节点"""
    print("执行节点: issue_resolver")

    # 模拟问题解决过程
    print("正在分析和解决客户问题...")
    time.sleep(1)

    # 随机决定问题是否解决（模拟）
    resolved = random.choice([True, False])

    if resolved:
        response = "您的问题已成功解决！如果还有其他需要帮助的地方，请随时告诉我们。"
        issue_status = True
    else:
        response = "我们正在进一步处理您的问题，稍后会有专员与您联系。"
        issue_status = False

    return Command(
        update={
            "messages": [("system", response)],
            "issue_resolved": issue_status
        },
        goto=END
    )

def main():
    """演示Command工具内部状态更新"""
    print("=== Command 工具内部状态更新演示 ===\n")

    builder = StateGraph(SupportState)

    builder.add_node(node_customer_lookup_tool)
    builder.add_node(node_support_agent)
    builder.add_node(node_issue_resolved)

    builder.add_edge(START, "node_customer_lookup_tool")

    graph = builder.compile()

    # 测试用例1: 金牌会员客户
    print("测试1: 金牌会员客户")
    initial_state = {
        "customer_id": "CUST001",
        "customer_info": {},
        "messages": [("user", "我需要查询我的账户信息")],
        "issue_resolved": False
    }
    print("初始状态:", initial_state)
    result = graph.invoke(initial_state)
    print("最终状态:", result)
    print("\n" + "=" * 50 + "\n")

    # 测试用例2: 不存在的客户
    print("测试2: 不存在的客户")
    initial_state = {
        "customer_id": "CUST999",
        "customer_info": {},
        "messages": [("user", "我想查询账户信息")],
        "issue_resolved": False
    }
    print("初始状态:", initial_state)
    result = graph.invoke(initial_state)
    print("最终状态:", result)
    print("\n" + "=" * 50 + "\n")

    # 测试用例3: 普通会员客户
    print("测试3: 普通会员客户")
    initial_state = {
        "customer_id": "CUST003",
        "customer_info": {},
        "messages": [("user", "账户有问题需要处理")],
        "issue_resolved": False
    }
    print("初始状态:", initial_state)
    result = graph.invoke(initial_state)
    print("最终状态:", result)

if __name__ == '__main__':
    main()