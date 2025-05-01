# ingest_to_chroma.py

import chromadb
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from urllib.parse import urljoin, urlparse

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.schema import Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from chromadb import PersistentClient

from playwright.sync_api import sync_playwright  # ✅ added to handle JS rendering
import warnings

# -------------------------
# STEP 1: Setup LlamaIndex Global Settings
# -------------------------
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
Settings.text_splitter = TokenTextSplitter(
    separator="\n\n", chunk_size=512, chunk_overlap=100
)

# -------------------------
# STEP 2: Webpage Reader with Cleaner
# -------------------------
def clean_html(raw_html: str) -> str:
    # Check if the document starts like XML
    if raw_html.strip().startswith("<?xml") or "<rss" in raw_html.lower() or "<feed" in raw_html.lower():
        parser = "lxml-xml"  # XML parser
    else:
        parser = "html.parser"  # Default HTML parser

    soup = BeautifulSoup(raw_html, parser)

    # Remove unwanted tags (works for both HTML and XML parsing)
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
# STEP 3: Extract Kali Linux Website Links
# -------------------------
def extract_all_kali_links(base_url="https://www.kali.org/"):
    print(f"🌐 Scraping links from {base_url}")
    links = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(base_url, timeout=60000)
        page.wait_for_load_state('load')

        anchors = page.query_selector_all("a[href]")
        for anchor in anchors:
            href = anchor.get_attribute("href")
            if href:
                parsed = urlparse(href)
                if parsed.netloc == "" or parsed.netloc == urlparse(base_url).netloc:
                    full_url = urljoin(base_url, href)
                    links.add(full_url)

        browser.close()

    print(f"✅ Found {len(links)} internal pages.")
    return list(links)

# -------------------------
# STEP 4: URLs to Load
# -------------------------
# Static important cybersecurity URLs
static_urls = [
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

# Dynamically scrape all Kali Linux documentation URLs
kali_links = extract_all_kali_links()

# Combine both
urls = static_urls + kali_links

print(f"📦 Total URLs to ingest: {len(urls)}")

# -------------------------
# STEP 5: Load and Clean Documents
# -------------------------
loader = CleanedWebPageReader()
documents = loader.load_data(urls)

# -------------------------
# STEP 6: Initialize Chroma Vector Store
# -------------------------
chroma_client = PersistentClient(path="./chroma_index")

vector_store = ChromaVectorStore(
    chroma_collection=chroma_client.get_or_create_collection("pentest_docs"),
    persist_path="./chroma_index"
)

# -------------------------
# STEP 7: Index and Persist
# -------------------------
index = VectorStoreIndex.from_documents(
    documents,
    vector_store=vector_store,
)

index.storage_context.persist()

print("✅ Successfully ingested cleaned documents into Chroma DB.")
