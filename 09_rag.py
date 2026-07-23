import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

# 1. 加载文档（一份虚构的公司制度问答，DeepSeek 训练数据里不可能见过）
with open("data/company_faq.txt", encoding="utf-8") as f:
    raw_text = f.read()

# 2. 切分文档：一份长文档要拆成一小段一小段，才方便逐段做向量检索
splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
chunks = splitter.split_text(raw_text)
print(f"=== 文档被切分成 {len(chunks)} 段 ===")
for i, chunk in enumerate(chunks):
    print(f"[{i}] {chunk}")

# 3. 用本地 embedding 模型把每一段文字转成向量，存进内存向量库
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vector_store = InMemoryVectorStore.from_texts(chunks, embeddings)

# 4. 检索：把问题也转成向量，找出最相似的几段原文
question = "星尘科技的年假政策是怎样的？"
retrieved_docs = vector_store.similarity_search(question, k=2)
print(f"\n=== 针对问题「{question}」检索到的相关片段 ===")
for doc in retrieved_docs:
    print("-", doc.page_content)

# 5. 把检索到的片段作为“已知资料”塞进 prompt，再让 LLM 基于资料回答
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是公司内部助手，只根据下面提供的资料回答问题，资料中没有的内容就明确说不知道，不要编造。\n\n资料：\n{context}",
        ),
        ("human", "{question}"),
    ]
)

context = "\n".join(doc.page_content for doc in retrieved_docs)
chain = prompt | llm
response = chain.invoke({"context": context, "question": question})
print("\n=== 最终回答 ===")
print(response.content)
