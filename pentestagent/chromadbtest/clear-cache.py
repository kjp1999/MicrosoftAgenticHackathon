# ==============================
# Imports and Dependencies
# ==============================
import socket
import requests
import subprocess
from bs4 import BeautifulSoup
from typing import TypedDict, List, Dict, Union
from concurrent.futures import ThreadPoolExecutor
import shutil
import os
from pathlib import Path

# HuggingFace cache directory
hf_cache_dir = Path.home() / ".cache" / "huggingface" / "hub"

# Clear HuggingFace model cache
def clear_huggingface_cache():
    if hf_cache_dir.exists():
        print(f"🧹 Clearing HuggingFace model cache at: {hf_cache_dir}")
        shutil.rmtree(hf_cache_dir)
        print("✅ HuggingFace cache cleared successfully.")
    else:
        print("⚡ HuggingFace cache directory does not exist. Nothing to clear.")

if __name__ == "__main__":
    clear_huggingface_cache()

# import shutil
# shutil.rmtree("chroma_db", ignore_errors=True)

