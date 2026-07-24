import hashlib
import os

from dotenv import load_dotenv
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

SOURCE_PATH = "data/company_faq.txt"
STORE_PATH = "vector_store.json"
HASH_PATH = "vector_store.hash"

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

with open(SOURCE_PATH, encoding="utf-8") as f:
    raw_text = f.read()
current_hash = hashlib.md5(raw_text.encode("utf-8")).hexdigest()

cached_hash = None
if os.path.exists(HASH_PATH):
    with open(HASH_PATH, encoding="utf-8") as f:
        cached_hash = f.read().strip()

if os.path.exists(STORE_PATH) and cached_hash == current_hash:
    print(f"=== 源文档未变化，直接加载 {STORE_PATH}，不重新计算 embedding ===")
    vector_store = InMemoryVectorStore.load(STORE_PATH, embeddings)
else:
    print(f"=== 源文档是新的或已发生变化，重新构建向量库 ===")
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    chunks = splitter.split_text(raw_text)

    vector_store = InMemoryVectorStore.from_texts(chunks, embeddings)
    vector_store.dump(STORE_PATH)
    with open(HASH_PATH, "w", encoding="utf-8") as f:
        f.write(current_hash)
    print(f"已保存到 {STORE_PATH}")

question = "员工报销有什么时间限制？"
docs = vector_store.similarity_search(question, k=2)
print(f"\n针对问题「{question}」检索到：")
for doc in docs:
    print("-", doc.page_content)
