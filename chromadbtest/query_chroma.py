# query_chroma.py

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 🔹 Use BGE embeddings again
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={"normalize_embeddings": True}
)

# 1. Load from Chroma DB
db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding_model
)

# 2. Prefix query (as recommended for BGE)
query = "Represent this sentence for retrieval: how to escalate privileges using sudo"
results = db.similarity_search(query, k=3)


# 3. Show results
print(f"\n🔍 Top matches for: '{query}'")
for i, doc in enumerate(results):
    print(f"\n[Match {i+1}] Source: {doc.metadata.get('source', 'N/A')}")
    print("-" * 40)
    print(doc.page_content[:500])
