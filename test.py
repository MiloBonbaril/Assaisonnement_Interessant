import requests

ollama_url = "http://localhost:11434"

# create a request to download the model
response = requests.post(
    f"{ollama_url}/api/download",
    json={"model": "llama3.1"},
    timeout=30
)