# query_chroma.py

from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
import os
os.environ["HF_TOKEN"] = ""
os.environ["OPENAI_API_KEY"] = ""

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# 🛠 Step 0: Setup HuggingFace Local LLM (Gemma 2B)
Settings.llm = HuggingFaceLLM(
    model_name="google/gemma-2b-it",
)
# Settings.llm = OpenAI(model="gpt-3.5-turbo")

# Step 1: Load stored Chroma index
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)

# Step 2: Create query engine
from llama_index.core.prompts import PromptTemplate

custom_prompt = PromptTemplate(
    "You are a cybersecurity expert assistant.\n"
    "Based ONLY on the context below, answer the question as clearly and completely as possible.\n"
    "If you don't know, say 'I don't know'.\n\n"
    "Context:\n{context_str}\n\n"
    "Question: {query_str}\n"
    "Answer:"
)

query_engine = index.as_query_engine(
    similarity_top_k=10,
    text_qa_template=custom_prompt,
)
# Step 3: Run Multiple Queries
sample_queries = [
    "Explain methods to bypass WAF (Web Application Firewalls).",
    "What is the process for privilege escalation in Linux systems?",
    "Common misconfigurations found during cloud penetration tests?",
    "How do attackers exploit SQL injection vulnerabilities?",
    "What are SSRF vulnerabilities and how can they be detected?",
    "Describe directory traversal attacks and how they occur.",
    "What reconnaissance tools are included in Kali Linux?",
    "Best practices for enumerating subdomains of a target domain.",
    "How does linPEAS help in privilege escalation?",
    "Explain lateral movement techniques in internal networks.",
    "Techniques for bypassing authentication mechanisms.",
    "Explain OSINT techniques used for initial reconnaissance.",
    "Top post-exploitation techniques after gaining shell access.",
    "Common security weaknesses found in AWS cloud environments.",
    "Steps to conduct a secure wireless penetration test."
]

# Step 4: Execute each query
# for i, query in enumerate(sample_queries, start=1):
#     print(f"\n==============================")
#     print(f"🔎 Query {i}: {query}")
#     print("==============================")
#     response = query_engine.query(query)
#     print(response)

for i, query in enumerate(sample_queries, start=1):
    print(f"\n🔎 Query {i}: {query}")
    print("==============================")
    
    # Manually get nodes
    nodes = index.as_retriever(similarity_top_k=10).retrieve(query)
    
    print(f"Retrieved {len(nodes)} nodes.")
    # for node in nodes:
        # print(f"Node Content (truncated): {node}")

    response = query_engine.query(query)
    print("Final Answer:", response)