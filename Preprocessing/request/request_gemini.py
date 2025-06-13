#@Noah Meißner 15.05.2025
import requests
from dotenv import load_dotenv
import os

def request(input):
    load_dotenv()
    API_KEY = os.getenv('GEMINI')
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": input}
                ]
            }
        ]
    }
    try: 
        response = requests.post(API_URL, headers=headers, json=data)
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"API Error: {{ {e} }}")
