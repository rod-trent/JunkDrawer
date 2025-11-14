import os
import argparse
from xai_sdk import Client
from xai_sdk.chat import user, system
from xai_sdk.tools import x_search  # Import the X search tool
from dotenv import load_dotenv

def get_threads(client, topic, num_threads=5, lang='en'):
    """
    Uses Grok API with agentic tool calling to fetch latest X threads on a topic.
    
    :param client: xai_sdk.Client instance
    :param topic: The topic to search for
    :param num_threads: Number of threads to aim for (default: 5)
    :param lang: Language filter (default: 'en')
    :return: The response from Grok containing the threads
    """
    chat = client.chat.create(
        model="grok-4-fast",  # Use a reasoning model
        tools=[x_search()],   # Enable X search tool
    )
    
    # System prompt to guide Grok on what to do
    chat.append(system(
        "You are a helpful assistant that fetches the latest X (Twitter) threads on a given topic. "
        "Use the x_search tool to find recent posts that start threads (non-replies). "
        "Look for conversations with multiple self-replies from the same author. "
        "Fetch full thread content using available tools if needed. "
        "Return up to {num_threads} threads, each as a list of tweet texts in order. "
        "Format the output clearly, e.g., Thread 1: Tweet 1: ..., Tweet 2: ..., etc. "
        "Filter for language: {lang}.".format(num_threads=num_threads, lang=lang)
    ))
    
    # User query
    chat.append(user("Pull the latest threads on the topic: {topic}".format(topic=topic)))
    
    # Get the response (non-streaming for simplicity)
    response = chat.sample()
    
    return response.content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pull latest X threads using Grok API")
    parser.add_argument("topic", type=str, help="The topic to search for")
    parser.add_argument("--num_threads", type=int, default=5, help="Number of threads to return (default: 5)")
    parser.add_argument("--lang", type=str, default="en", help="Language filter (default: en)")
    parser.add_argument("--api_key", type=str, required=False, help="Your xAI API key (overrides .env)")
    
    args = parser.parse_args()
    
    # Load .env from the current working directory
    load_dotenv()
    
    api_key = args.api_key or os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("xAI API key is required. Set XAI_API_KEY in .env file or use --api_key.")
    
    client = Client(api_key=api_key)
    
    threads_content = get_threads(client, args.topic, args.num_threads, args.lang)
    
    print(threads_content)
