import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个友好的助手，会记住之前聊过的内容。"),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ]
)

chain = prompt | llm

history = []


def chat(user_input):
    response = chain.invoke({"history": history, "input": user_input})
    history.append(HumanMessage(content=user_input))
    history.append(response)
    print(f"用户: {user_input}")
    print(f"助手: {response.content}\n")


chat("我叫小明，最喜欢的水果是芒果。")
chat("你还记得我的名字和喜欢的水果吗？")
