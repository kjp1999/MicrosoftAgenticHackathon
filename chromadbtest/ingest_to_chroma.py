# ingest_to_chroma.py

import chromadb
import requests
from bs4 import BeautifulSoup

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.schema import Document   # <-- FIXED HERE
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from chromadb import PersistentClient

# -------------------------
# STEP 1: Setup LlamaIndex Global Settings
# -------------------------
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
Settings.text_splitter = TokenTextSplitter(
    separator="\n\n", chunk_size=512, chunk_overlap=100
)

# -------------------------
# STEP 2: Webpage Reader with Cleaner
# -------------------------
def clean_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style", "header", "footer", "nav", "noscript"]):
        tag.extract()
    text = soup.get_text(separator="\n")
    return text.strip()

class CleanedWebPageReader:
    def load_data(self, urls):
        docs = []
        for url in urls:
            print(f"📥 Fetching {url}")
            try:
                raw_html = requests.get(url, timeout=10).text
                cleaned_text = clean_html(raw_html)
                docs.append(Document(text=cleaned_text, metadata={"source": url}))
            except Exception as e:
                print(f"❗ Error fetching {url}: {str(e)}")
        return docs

# -------------------------
# STEP 3: URLs to Load
# -------------------------
urls = [
    "https://owasp.org/www-project-web-security-testing-guide/",
    "https://book.hacktricks.xyz/network-services-pentesting/recon-ng",
    "https://www.kali.org/tools/",
    "https://www.w3.org/Security/Faq/",
    "https://cheatsheetseries.owasp.org/",
    "https://www.cisa.gov/resources-tools/resources/cybersecurity-best-practices",
    "https://learn.microsoft.com/en-us/security/compass/cloud-security-benchmarks",
    "https://book.hacktricks.xyz/cloud-security/",
    "https://www.pentesterlab.com/",
    "https://attack.mitre.org/",
    "https://portswigger.net/web-security",
]

# -------------------------
# STEP 4: Load and Clean Documents
# -------------------------
loader = CleanedWebPageReader()
documents = loader.load_data(urls)

# -------------------------
# STEP 5: Initialize Chroma Vector Store
# -------------------------
chroma_client = PersistentClient(path="./chroma_index")

vector_store = ChromaVectorStore(
    chroma_collection=chroma_client.get_or_create_collection("pentest_docs"),
    persist_path="./chroma_index"
)

# -------------------------
# STEP 6: Index and Persist
# -------------------------
index = VectorStoreIndex.from_documents(
    documents,
    vector_store=vector_store,
)

index.storage_context.persist()

print("✅ Successfully ingested cleaned documents into Chroma DB.")
