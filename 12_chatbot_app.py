import hashlib
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

SOURCE_PATH = "data/company_faq.txt"
STORE_PATH = "vector_store.json"
HASH_PATH = "vector_store.hash"

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


# 1. 复用第 11 步的逻辑:向量库存在且源文档没变就直接加载，否则重新构建
def load_or_build_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

    with open(SOURCE_PATH, encoding="utf-8") as f:
        raw_text = f.read()
    current_hash = hashlib.md5(raw_text.encode("utf-8")).hexdigest()

    cached_hash = None
    if os.path.exists(HASH_PATH):
        with open(HASH_PATH, encoding="utf-8") as f:
            cached_hash = f.read().strip()

    if os.path.exists(STORE_PATH) and cached_hash == current_hash:
        return InMemoryVectorStore.load(STORE_PATH, embeddings)

    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    chunks = splitter.split_text(raw_text)
    store = InMemoryVectorStore.from_texts(chunks, embeddings)
    store.dump(STORE_PATH)
    with open(HASH_PATH, "w", encoding="utf-8") as f:
        f.write(current_hash)
    return store


vector_store = load_or_build_vector_store()


# 2. 把 RAG 检索包装成一个工具，交给 Agent 自己决定什么时候查
@tool
def search_company_docs(query: str) -> str:
    """在公司规章制度文档中检索和问题相关的内容，用于回答年假、报销、远程办公、试用期等制度类问题。"""
    docs = vector_store.similarity_search(query, k=2)
    return "\n".join(doc.page_content for doc in docs)


agent = create_agent(
    llm,
    tools=[search_company_docs],
    system_prompt=(
        "你是公司内部助手。遇到规章制度类问题，先调用 search_company_docs 工具查询资料，"
        "再基于查到的资料回答；资料里没有的内容就明确说不知道，不要编造。"
    ),
)

# 3. 多轮对话：用一个消息列表串起本次会话的完整历史
messages = []
print("公司内部助手已就绪，输入 exit 退出。\n")

while True:
    user_input = input("你: ")
    if user_input.strip().lower() in {"exit", "quit"}:
        break

    messages.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": messages})
    messages = result["messages"]

    print(f"助手: {messages[-1].content}\n")
