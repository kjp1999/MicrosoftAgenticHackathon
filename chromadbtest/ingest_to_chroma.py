from langchain_community.document_loaders import TextLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# Local embedding model from Hugging Face
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 1. Load local file
file_loader = TextLoader("sample.txt")
file_docs = file_loader.load()

# 2. Load web content
urls = [
    "https://book.hacktricks.xyz/linux-hardening/privilege-escalation",
    "https://owasp.org/www-project-web-security-testing-guide/"
]
web_loader = WebBaseLoader(urls)
web_docs = web_loader.load()

# 3. Combine docs
all_docs = file_docs + web_docs

# 4. Chunk the text
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split_documents(all_docs)

# 5. Embed and store in Chroma
db = Chroma.from_documents(
    chunks,
    embedding=embedding_model,
    persist_directory="chroma_db"
)
db.persist()

print("✅ Ingested file + web content into Chroma.")
