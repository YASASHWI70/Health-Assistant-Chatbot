import requests
import json

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"

messages = [
    {
        "role": "system",
        "content": """
        Return STRICT JSON.

        Format:
        {
            "symptoms": [
                {
                    "name": "symptom",
                    "severity": "mild/moderate/severe/unknown",
                    "duration": "duration/unknown"
                }
            ],
            "advice": "text"
        }

        Rules:
        - Extract ALL symptoms mentioned
        - symptoms must be a JSON array of objects
        - severity must be one of: mild, moderate, severe, unknown
        - duration must be extracted if present, else "unknown"
        - No extra text outside JSON
        """
    },
    {
        "role": "user",
        "content": "I have mild fever from 2 days."
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
    raw_content = data["message"]["content"]
    
    try:
        parsed_json = json.loads(raw_content)
        
        print(json.dumps(parsed_json, indent=2))
        
        with open("output.json", "w") as f:
            json.dump(parsed_json, f, indent=2)
            
    except json.JSONDecodeError:
        print("Invalid JSON from model:")
        print(repr(raw_content))
else:
    print("Error:", response.text)