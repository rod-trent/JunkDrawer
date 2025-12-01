# utils/grok_client.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

def grok_chat(messages, tools=None):
    kwargs = {
        "model": "grok-4",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 8192,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    
    response = client.chat.completions.create(**kwargs)
    return response