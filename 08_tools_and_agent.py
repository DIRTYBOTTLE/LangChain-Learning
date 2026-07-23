import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


@tool
def get_weather(city: str) -> str:
    """查询指定城市当前的天气情况。"""
    fake_weather_db = {"北京": "晴，25°C", "上海": "多云，28°C"}
    return fake_weather_db.get(city, f"暂无 {city} 的天气数据")


@tool
def add(a: float, b: float) -> float:
    """计算两个数字相加的结果。"""
    return a + b


tools = [get_weather, add]
tools_by_name = {t.name: t for t in tools}

# 1. 手动实现一遍“工具调用循环”，看清背后的机制
print("=== 手动工具调用 ===")
llm_with_tools = llm.bind_tools(tools)

messages = [HumanMessage(content="北京今天天气怎么样？")]
ai_message = llm_with_tools.invoke(messages)
print("模型决定调用的工具：", ai_message.tool_calls)

messages.append(ai_message)
for tool_call in ai_message.tool_calls:
    selected_tool = tools_by_name[tool_call["name"]]
    tool_message = selected_tool.invoke(tool_call)
    messages.append(tool_message)

final_response = llm_with_tools.invoke(messages)
print("最终回答：", final_response.content)


# 2. 用官方 create_agent 封装同样的能力
print("\n=== create_agent 封装 ===")
from langchain.agents import create_agent  # noqa: E402

agent = create_agent(llm, tools=tools)
result = agent.invoke(
    {
        "messages": [
            HumanMessage(content="上海天气怎么样？另外，3.5 加 2.7 等于多少？")
        ]
    }
)
for m in result["messages"]:
    m.pretty_print()
