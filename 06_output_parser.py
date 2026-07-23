import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

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

# 1. StrOutputParser：直接拿到纯文本，而不是 AIMessage 对象
str_chain = prompt | llm | StrOutputParser()
result = str_chain.invoke({"language": "英文", "text": "今天天气真好，我们去公园散步吧。"})
print(isinstance(result, str), result)


# 2. 结构化输出：让模型按指定字段返回一个 Python 对象
class Translation(BaseModel):
    translated_text: str = Field(description="翻译后的文本")
    source_language: str = Field(description="识别出的原文语言，例如：中文")


structured_llm = llm.with_structured_output(Translation, method="function_calling")
structured_chain = prompt | structured_llm
structured_result = structured_chain.invoke(
    {"language": "英文", "text": "今天天气真好，我们去公园散步吧。"}
)
print(type(structured_result), structured_result)
