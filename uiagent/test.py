import ollama

with open("screen.png", "rb") as f:
    image = f.read()

response = ollama.chat(
    model="llava",
    messages=[{"role": "user", "content": "What's in this image?", "images" :[image]}],
    
)

print(response["message"]["content"])
