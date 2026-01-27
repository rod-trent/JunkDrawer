"""
Test xAI API Connection
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('XAI_API_KEY')

if not api_key:
    print("❌ XAI_API_KEY not found in .env file")
    exit(1)

print(f"✓ API Key loaded: {api_key[:15]}...")

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

data = {
    'messages': [
        {
            'role': 'system',
            'content': 'You are a helpful assistant.'
        },
        {
            'role': 'user',
            'content': 'Say "Hello from NancyBot test!" in exactly those words.'
        }
    ],
    'model': 'grok-4',
    'stream': False,
    'temperature': 0
}

print("\nTesting xAI API connection...")
print(f"Endpoint: https://api.x.ai/v1/chat/completions")
print(f"Model: grok-4\n")

try:
    response = requests.post(
        'https://api.x.ai/v1/chat/completions',
        headers=headers,
        json=data,
        timeout=3600
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! API is working correctly.\n")
        result = response.json()
        print("Response:")
        print(result['choices'][0]['message']['content'])
        print("\n✓ NancyBot should work correctly now!")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
    if hasattr(e, 'response') and e.response:
        print(f"Response: {e.response.text}")