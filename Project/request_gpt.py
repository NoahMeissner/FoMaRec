import requests
from dotenv import load_dotenv
import os

def chat_with_openai(prompt, model="gpt-4o-mini", temperature=0.7):
    load_dotenv()
    API_KEY = os.getenv('OPENAI')
    API_URL = "https://api.openai.com/v1/chat/completions"

    if not API_KEY:
        raise ValueError("OPENAI_API_KEY nicht gefunden. Bitte API-Key in der .env-Datei setzen.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status() 
        result = response.json()
        if 'choices' in result and result['choices']:
            return result['choices'][0]['message']['content']
        else:
            return f"API-Antwort unerwartet: {result}"
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP-Fehler: {http_err} - {response.text}"
    except Exception as e:
        return f"Allgemeiner Fehler: {e}"

