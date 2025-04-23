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

# Clear model cache at startup
model_cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
if os.path.exists(model_cache_dir):
    print("[Startup] Clearing Hugging Face model cache...")
    shutil.rmtree(model_cache_dir, ignore_errors=True)

import shutil
shutil.rmtree("chroma_db", ignore_errors=True)

