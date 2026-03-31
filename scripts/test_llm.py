import requests
import json

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"

messages = [
    {
        "role": "system",
        "content": 'You are a medical assistant. Always respond in valid JSON using exactly this format: {"symptoms": ["...", "..."], "advice": "..."}'
    },
    {
        "role": "user",
        "content": "I have severe headache and cold for 2 days."
    }
]

payload = {
    "model": MODEL,
    "messages": messages,
    "format": "json",
    "stream": False,
    "options": {
        "temperature": 1.0
    }
}

response = requests.post(OLLAMA_URL, json=payload)

if response.status_code == 200:
    data = response.json()
    raw_content = data["message"]["content"]
    
    try:
        # Parse the JSON and pretty print it so it doesn't get messed up in the terminal
        parsed_json = json.loads(raw_content)
        print("Received valid JSON response:")
        print(json.dumps(parsed_json, indent=2))
    except json.JSONDecodeError:
        print("Model did not return valid JSON. Raw output was:")
        print(repr(raw_content))
else:
    print("Error:", response.text)