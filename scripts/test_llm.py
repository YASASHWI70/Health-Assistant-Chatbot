import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"

messages = [
    {
        "role": "system",
        "content": """You are medical assistant. 
          Always respond in JSON."""
    },
    {
        "role": "user",
        "content": "I have fever and headache for 2 days."
    }
]

payload = {
    "model": MODEL,
    "messages": messages,
    "format": "json",
    "stream": False,
    "options": {
        "temperature": 0
    }
}

response = requests.post(OLLAMA_URL, json=payload)

if response.status_code == 200:
    data = response.json()
    content = data["message"]["content"]
    import json
    try:
        parsed_json = json.loads(content)
        print("Success! The response is valid JSON:")
        print(json.dumps(parsed_json, indent=2))
    except json.JSONDecodeError:
        print("Error: The response is NOT valid JSON. Raw output:")
        print(repr(content)) # Use repr to see any hidden carriage returns causing scrambled output
else:
    print("Error:", response.text)