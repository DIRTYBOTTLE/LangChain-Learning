import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

# 1. 最基础的流式调用：llm.stream()
print("=== llm.stream() ===")
for chunk in llm.stream("用 100 字左右描述一下秋天的景色。"):
    print(chunk.content, end="", flush=True)
print()

# 2. 整条链也能流式输出：prompt | llm | StrOutputParser()
print("\n=== chain.stream()（prompt | llm | StrOutputParser）===")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个专业翻译，把用户输入的内容翻译成{language}，只输出翻译结果，不要多余解释。"),
        ("human", "{text}"),
    ]
)
chain = prompt | llm | StrOutputParser()
for chunk in chain.stream({"language": "英文", "text": "秋天到了，树叶渐渐变黄，风也凉了。"}):
    print(chunk, end="", flush=True)
print()
