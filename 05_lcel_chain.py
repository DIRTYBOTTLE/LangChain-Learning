import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个专业翻译，把用户输入的内容翻译成{language}，只输出翻译结果，不要多余解释。"),
        ("human", "{text}"),
    ]
)

chain = prompt | llm

response = chain.invoke({"language": "英文", "text": "今天天气真好，我们去公园散步吧。"})
print(response.content)
