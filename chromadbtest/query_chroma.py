from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Load Chroma DB
db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding_model
)

query = "How can I escalate privileges using sudo?"
results = db.similarity_search(query, k=3)

print(f"\n🔍 Top matches for: '{query}'")
for i, doc in enumerate(results):
    print(f"\n[Match {i+1}] Source: {doc.metadata.get('source', 'N/A')}")
    print("-" * 40)
    print(doc.page_content[:500])
