import os
import time
from datetime import datetime
from typing import List, Dict

from google import genai
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    HttpOptions,
    Tool,
    GoogleSearchRetrieval
)

# Set Gemini API Key in the environment
os.environ["GOOGLE_API_KEY"] = ""  

class GeminiSearchEngine:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment variables.")

        self.models = [
            "gemini-2.0-flash",
            "gemini-2.5-flash-preview-04-17",
        ]
        self.current_model_index = 0
        self.daily_usage = {model: 0 for model in self.models}
        self.usage_reset_date = datetime.now().date()
        self.max_free_grounding_requests = 500  # Adjust if needed

        self.client = genai.Client()

    def _rotate_model(self):
        self.current_model_index += 1
        if self.current_model_index >= len(self.models):
            raise RuntimeError("❌ All available models exhausted for today.")

    def _check_reset_daily_usage(self):
        if datetime.now().date() != self.usage_reset_date:
            print("🔄 Resetting daily usage counts...")
            self.daily_usage = {model: 0 for model in self.models}
            self.usage_reset_date = datetime.now().date()

    def search(self, query: str, max_tokens: int = 512) -> str:
        self._check_reset_daily_usage()

        while True:
            model_name = self.models[self.current_model_index]
            if self.daily_usage[model_name] >= self.max_free_grounding_requests:
                print(f"⚠️ {model_name} has reached daily limit. Switching models...")
                self._rotate_model()
                continue

            try:
                start_time = time.time()

                # Correct way: use GoogleSearchRetrieval inside Tool
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=query,
                    config=GenerateContentConfig(
                        temperature=0.1,
                        top_p=0.2,
                        top_k=5,
                        max_output_tokens=max_tokens,
                        tools=[Tool(google_search=GoogleSearch())]
                    )
                )

                elapsed_time = time.time() - start_time
                print(f"✅ Gemini search completed in {elapsed_time:.2f} seconds")

                self.daily_usage[model_name] += 1

                # Handle citations (optional based on model response)
                citations = []
                if hasattr(response, "citations"):
                    for citation in response.citations:
                        citations.append(f"- {citation.url} ({citation.title})")

                citation_text = "\n".join(citations) if citations else "No citations available"

                print(f"📝 Gemini Response: {response.text}")
                return f"{response.text}\n\nSources:\n{citation_text}\n\n"

            except Exception as e:
                error_str = str(e)
                print(f"⚠️ Gemini API error: {error_str}")

                if "429" in error_str or "quota" in error_str.lower():
                    print("🚨 Quota or rate limit hit. Switching models...")
                    self._rotate_model()
                    continue
                else:
                    return f"Error retrieving response from Gemini API: {error_str}"

# ------------------ TEST ------------------

if __name__ == "__main__":
    search_engine = GeminiSearchEngine()

    query = "What are the top open-source tools for cloud penetration testing in 2024?"
    result = search_engine.search(query)

    print("\n🔵 Final Result:")
    print(result)
