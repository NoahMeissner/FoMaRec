# Noah Meissner 

import requests
import json

# Jetzt kannst du localhost:8888 verwenden, als wäre es der Remote-Server
url = "http://localhost:8888/api/generate"

payload = {
    "model": "llama3.1:8b-instruct-q4_K_M",
    "prompt": "Erkläre mir Python in einem Satz.",
    "stream": False
}

response = requests.post(url, json=payload)
result = response.json()
print(result['response'])
print(result)
