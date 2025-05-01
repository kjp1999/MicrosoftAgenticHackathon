from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.prompts import PromptTemplate
import os

# If you need Ollama to connect to another host, update this URL
OLLAMA_SERVER_URL = "http://localhost:11434"

# Step 0: Setup Embedding Model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Step 1: Setup Ollama LLM
Settings.llm = Ollama(
    model="artifish/llama3.2-uncensored",
    base_url=OLLAMA_SERVER_URL,
    request_timeout=120  # Timeout in seconds (optional)
)

# Step 2: Load stored Chroma index
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)

# Step 3: Create custom query prompt
custom_prompt = PromptTemplate(
    "You are a cybersecurity expert assistant.\n"
    "Based ONLY on the context below, answer the question as clearly and completely as possible.\n"
    "If you don't know, say 'I don't know'.\n\n"
    "Context:\n{context_str}\n\n"
    "Question: {query_str}\n"
    "Answer:"
)

# Step 4: Create query engine
query_engine = index.as_query_engine(
    similarity_top_k=10,
    text_qa_template=custom_prompt,
)

# Step 5: List of queries
# sample_queries = [
#     "Explain methods to bypass WAF (Web Application Firewalls).",
#     "What is the process for privilege escalation in Linux systems?",
#     "Common misconfigurations found during cloud penetration tests?",
#     "How do attackers exploit SQL injection vulnerabilities?",
#     "What are SSRF vulnerabilities and how can they be detected?",
#     "Describe directory traversal attacks and how they occur.",
#     "What reconnaissance tools are included in Kali Linux?",
#     "Best practices for enumerating subdomains of a target domain.",
#     "How does linPEAS help in privilege escalation?",
#     "Explain lateral movement techniques in internal networks.",
#     "Techniques for bypassing authentication mechanisms.",
#     "Explain OSINT techniques used for initial reconnaissance.",
#     "Top post-exploitation techniques after gaining shell access.",
#     "Common security weaknesses found in AWS cloud environments.",
#     "Steps to conduct a secure wireless penetration test."
# ]

# Step 5: List of queries (updated for Kali Linux topics)
# sample_queries = [
#     "What is Kali Linux and what is it used for?",
#     "Explain the steps to install Kali Linux on a virtual machine.",
#     "What are the default tools included in Kali Linux?",
#     "How do you update and upgrade packages in Kali Linux?",
#     "What is the Kali Undercover Mode and when would you use it?",
#     "How can you create a custom Kali Linux ISO using live-build?",
#     "Explain how Kali Linux can be installed on a mobile device.",
#     "What are the best practices for securing a Kali Linux installation?",
#     "How does the Kali NetHunter platform differ from standard Kali Linux?",
#     "Explain the role of Metapackages in Kali Linux.",
#     "What penetration testing tools are pre-installed in Kali Linux?",
#     "Describe how to use Win-KeX in Kali Linux on WSL2.",
#     "Explain the process of running Kali Linux in a container.",
#     "How can you contribute to the Kali Linux community?",
#     "Explain the difference between Kali Linux bare-metal install and live boot."
# ]

# Step 5 (Advanced Kali Linux Query List)
sample_queries = [
    "How can you perform wireless network attacks using Kali Linux tools like aircrack-ng?",
    "Explain how to conduct a full web application assessment using Burp Suite in Kali Linux.",
    "What is the workflow for exploiting a system using Metasploit Framework in Kali Linux?",
    "Describe how to use SQLMap for detecting and exploiting SQL injection vulnerabilities.",
    "Explain the purpose and usage of Responder tool in Kali Linux for LLMNR poisoning.",
    "How do you configure and use Hydra for password cracking in Kali Linux?",
    "What steps are involved in setting up a reverse shell in Kali Linux during a pentest?",
    "How can you automate OSINT gathering with tools like Maltego in Kali Linux?",
    "What techniques does ffuf provide for web fuzzing and how is it used in Kali Linux?",
    "Explain how to scan a network and enumerate services using Nmap in Kali Linux.",
    "Describe setting up a rogue Wi-Fi access point using Kali Linux.",
    "How can you leverage Kali Linux tools for privilege escalation in Linux and Windows systems?",
    "What are the techniques for evading antivirus detection when using Kali Linux payloads?",
    "How can you customize Kali Linux builds for specific engagement needs?",
    "Describe forensic investigation capabilities available in Kali Linux (e.g., Autopsy, Sleuth Kit)."
]


# Step 6: Execute each query
for i, query in enumerate(sample_queries, start=1):
    print(f"\n🔎 Query {i}: {query}")
    print("==============================")
    
    # Manually get nodes (retrieved chunks)
    nodes = index.as_retriever(similarity_top_k=10).retrieve(query)
    print(f"Retrieved {len(nodes)} nodes.")

    response = query_engine.query(query)
    print("Final Answer:", response)
