import os
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv  # Requires: pip install python-dotenv

# Load environment variables from .env file
load_dotenv()

# Note: To use this tool, you need an xAI API key in your .env file as XAI_API_KEY="your_key_here"
# Visit https://x.ai/api for details on how to obtain one.

# Initialize the client with xAI API base URL
client = OpenAI(
    base_url="https://api.x.ai/v1",
    api_key=os.getenv("XAI_API_KEY")
)

def query_grok_for_cybersecurity_news():
    # Calculate the time 24 hours ago
    now = datetime.utcnow()
    past_24_hours = now - timedelta(hours=24)
    prompt = f"Search for and summarize the latest cybersecurity news from the past 24 hours, starting from {past_24_hours.strftime('%Y-%m-%d %H:%M:%S')} UTC up to now. Provide a detailed summary based on current sources."

    try:
        response = client.chat.completions.create(
            model="grok-4-0709",  # Updated to a valid model name; check https://docs.x.ai/docs/models for latest
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides up-to-date news summaries using real-time search."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error querying Grok API: {str(e)}"

# Example usage
if __name__ == "__main__":
    news_summary = query_grok_for_cybersecurity_news()
    print(news_summary)
