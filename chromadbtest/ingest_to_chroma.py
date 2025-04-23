# ingest_to_chroma.py

from langchain_community.document_loaders import TextLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 🔹 Use BGE embeddings (local, no API needed)
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={"normalize_embeddings": True}
)

# 1. Load from file
file_loader = TextLoader("sample.txt")
file_docs = file_loader.load()

# 2. Load from web
urls = [
    "https://book.hacktricks.xyz/linux-hardening/privilege-escalation",
    "https://owasp.org/www-project-web-security-testing-guide/"
]
web_loader = WebBaseLoader(urls)
web_docs = web_loader.load()

# 3. Chunk content
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split_documents(file_docs + web_docs)

# 4. Store in Chroma
db = Chroma.from_documents(
    chunks,
    embedding=embedding_model,
    persist_directory="chroma_db"
)

print("✅ Ingested file + web content into Chroma using BGE embeddings.")
