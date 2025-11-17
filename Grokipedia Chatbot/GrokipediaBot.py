import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (expects XAI_API_KEY in .env file)
load_dotenv()

# Initialize the OpenAI-compatible client for xAI API
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

def search_grokipedia(topic):
    """
    Sends a prompt to Grok via xAI API to search Grokipedia for the given topic.
    """
    response = client.chat.completions.create(
        model="grok-3",  # Updated to 'grok-3'; check xAI docs for latest models if issues persist
        messages=[
            {"role": "system", "content": "You are Grok, a helpful AI by xAI. Use your capabilities to search and summarize content from Grokipedia."},
            {"role": "user", "content": f"Search Grokipedia for {topic} and provide a detailed summary."}
        ],
        max_tokens=1000,
        temperature=0.7,
    )
    return response.choices[0].message.content

def main():
    print("Welcome to the Grokipedia Search Chatbot powered by xAI's Grok API!")
    print("Enter a topic to search on Grokipedia (or type 'exit' to quit).")
    
    while True:
        topic = input("\nTopic: ").strip()
        if topic.lower() == 'exit':
            print("Goodbye!")
            break
        if not topic:
            print("Please enter a valid topic.")
            continue
        
        try:
            result = search_grokipedia(topic)
            print("\nGrok's Response:")
            print(result)
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Make sure your XAI_API_KEY is set correctly and you have access to the API. Check https://docs.x.ai for updates.")

if __name__ == "__main__":
    main()