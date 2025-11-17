# Building a Grokipedia Search Chatbot: Python CLI and HTML Web Versions

In the world of AI-powered tools, accessing specialized knowledge bases like Grokipedia—an AI-generated encyclopedia powered by xAI's Grok technology—can be incredibly useful for researchers, students, and curious minds. Grokipedia offers detailed, dynamically generated articles on a wide range of topics, and with xAI's API, you can integrate Grok's capabilities to search and summarize its content programmatically.

In this blog post, I'll walk you through two versions of a simple chatbot that leverages the xAI API to search Grokipedia: a command-line interface (CLI) version built in Python, and a web-based version using HTML with JavaScript. Both allow you to input a topic and receive a detailed summary from Grok, but they cater to different use cases—the Python version for developers or scripted automation, and the HTML version for a quick, browser-based experience.

We'll cover prerequisites, implementation steps, and usage for each. By the end, you'll have the tools to set up your own Grokipedia searcher. Let's dive in!

## Why Build This Chatbot?
Grokipedia is hosted at grokipedia.com and uses Grok to generate encyclopedia-style entries. However, manually navigating it can be tedious for frequent queries. Using xAI's Grok API, we can automate searches, making it easier to pull summaries on topics like "AI history" or "quantum computing." Both versions here use the API to prompt Grok with a system message like: "You are Grok, a helpful AI by xAI. Use your capabilities to search and summarize content from Grokipedia." This ensures focused, relevant responses.

Note: As of November 2025, the recommended model is 'grok-3' (earlier models like 'grok-beta' have been deprecated). Always check the xAI docs for updates.

## Version 1: Python CLI Chatbot
This version runs in your terminal, making it ideal for quick scripts or integration into larger Python projects. It's lightweight and doesn't require a web server.

### Prerequisites
- **Python 3.8+**: Ensure you have Python installed (download from python.org if needed).
- **xAI API Key**: Sign up at [xAI Console](https://console.x.ai) and generate an API key. This requires an account and may involve a subscription for full access.
- **Dependencies**: Install via pip:
  ```
  pip install openai python-dotenv
  ```
- **.env File**: Create a file named `.env` in your project directory with your API key:
  ```
  XAI_API_KEY=your_api_key_here
  ```

### Implementation
Save the following code as `grokipedia_chatbot.py`. It uses the OpenAI SDK (compatible with xAI's API) to send prompts to Grok.

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

def search_grokipedia(topic):
    """
    Sends a prompt to Grok via xAI API to search Grokipedia.
    """
    response = client.chat.completions.create(
        model="grok-3",  # Use 'grok-3' or check docs for alternatives
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
```

This script initializes the API client, defines a function to query Grok, and runs a loop for user inputs. Error handling catches issues like invalid keys or deprecated models.

### How to Use
1. Run the script: `python grokipedia_chatbot.py`.
2. Enter a topic (e.g., "AI history").
3. View the summary in the terminal.
4. Type 'exit' to quit.

Pros: Easy to extend (e.g., add logging or batch processing). Cons: No graphical interface, so it's text-only.

## Version 2: HTML Web-Based Chatbot
For a more user-friendly experience, this version runs entirely in your browser—no server needed. It's a single HTML file with embedded JavaScript that makes API calls directly.

### Prerequisites
- **xAI API Key**: Same as above—you'll enter it in the browser (it stays local; no storage).
- **Modern Browser**: Chrome, Firefox, etc., with JavaScript enabled.
- No installations required! Just save the file and open it.

### Implementation
Save the following as `grokipedia_chatbot.html`. It includes CSS for styling and JavaScript for handling API requests via Fetch.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grokipedia Search Chatbot</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); width: 100%; max-width: 600px; }
        h1 { text-align: center; color: #333; }
        .input-group { display: flex; margin-bottom: 20px; }
        input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px 0 0 4px; font-size: 16px; }
        button { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 0 4px 4px 0; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #0056b3; }
        .response { background-color: #f9f9f9; padding: 15px; border: 1px solid #ddd; border-radius: 4px; white-space: pre-wrap; min-height: 100px; overflow-y: auto; }
        .error { color: red; margin-top: 10px; }
        .api-key-group { margin-bottom: 20px; }
        input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Grokipedia Search Chatbot</h1>
        <p>Powered by xAI's Grok API. Enter your API key below (it stays local in your browser).</p>
        
        <div class="api-key-group">
            <label for="api-key">xAI API Key:</label>
            <input type="password" id="api-key" placeholder="Enter your XAI_API_KEY here">
        </div>
        
        <div class="input-group">
            <input type="text" id="topic" placeholder="Enter a topic to search on Grokipedia">
            <button onclick="searchGrokipedia()">Search</button>
        </div>
        
        <div class="response" id="response"></div>
        <div class="error" id="error"></div>
    </div>

    <script>
        async function searchGrokipedia() {
            const topic = document.getElementById('topic').value.trim();
            const apiKey = document.getElementById('api-key').value.trim();
            const responseDiv = document.getElementById('response');
            const errorDiv = document.getElementById('error');

            responseDiv.innerHTML = '';
            errorDiv.innerHTML = '';

            if (!topic) {
                errorDiv.innerHTML = 'Please enter a valid topic.';
                return;
            }
            if (!apiKey) {
                errorDiv.innerHTML = 'Please enter your xAI API key.';
                return;
            }

            responseDiv.innerHTML = 'Searching...';

            try {
                const response = await fetch('https://api.x.ai/v1/chat/completions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${apiKey}`
                    },
                    body: JSON.stringify({
                        model: 'grok-3',
                        messages: [
                            {
                                role: 'system',
                                content: 'You are Grok, a helpful AI by xAI. Use your capabilities to search and summarize content from Grokipedia.'
                            },
                            {
                                role: 'user',
                                content: `Search Grokipedia for ${topic} and provide a detailed summary.`
                            }
                        ],
                        max_tokens: 1000,
                        temperature: 0.7
                    })
                });

                if (!response.ok) {
                    throw new Error(`API error: ${response.status} - ${await response.text()}`);
                }

                const data = await response.json();
                responseDiv.innerHTML = data.choices[0].message.content;
            } catch (error) {
                errorDiv.innerHTML = `Error: ${error.message}`;
                responseDiv.innerHTML = '';
            }
        }
    </script>
</body>
</html>
```

The HTML provides a clean UI with input fields for the API key and topic, a search button, and areas for responses/errors. JavaScript handles the async API call.

### How to Use
1. Open the `grokipedia_chatbot.html` file in your browser (double-click or drag into a tab).
2. Enter your xAI API key in the password field (it's not saved; re-enter if you refresh).
3. Type a topic and click "Search."
4. The summary appears in the response box. Errors (e.g., invalid key) show in red.

Pros: Intuitive interface, runs locally without setup. Cons: API calls from the browser might hit CORS issues (though xAI's API supports it); less suitable for automation.

## Comparing the Two Versions
- **Python CLI**: Great for developers who want to script or integrate (e.g., into a larger app). It's more flexible for batch queries but requires Python knowledge.
- **HTML Web**: Perfect for non-coders or quick demos. It's portable (share the file) and visual, but relies on browser security for API keys.
Both handle errors gracefully and use the same API logic. If you're extending this, consider adding features like history logging or multi-query support.

## Final Thoughts
With xAI's API, building tools like this Grokipedia searcher is straightforward and powerful. Start with the version that fits your needs, and experiment—perhaps combine them into a full web app with a Python backend. For more on xAI's offerings, check [docs.x.ai](https://docs.x.ai). If you run into issues, common fixes include updating the model or verifying your API subscription.

Happy searching! If you build on this, share your tweaks in the comments. 🚀
