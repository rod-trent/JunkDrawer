import os
import requests
from dotenv import load_dotenv

load_dotenv()

def query_grok(messages, model="grok-3", temperature=0.7, max_tokens=1500):  # ← CHANGED TO grok-3
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        return "[ERROR] GROK_API_KEY not found in .env file!"

    url = "https://api.x.ai/v1/chat/completions"  # ← Correct URL

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=90)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        return f"[HTTP ERROR] {e} – {response.text if 'response' in locals() else 'No response'}"
    except Exception as e:
        return f"[API ERROR] {str(e)}"