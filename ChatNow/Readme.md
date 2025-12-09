# Building a Custom Chatbot on-the-fly with Streamlit and xAI: Introducing ChatNow

In the rapidly evolving world of AI, creating personalized chatbots has become more accessible than ever. Today, I'm excited to dive into **ChatNow**, a Streamlit-based application that lets you build custom AI assistants powered by xAI's Grok models. This app, as of December 2025, combines simplicity with powerful features like tool integrations, local Retrieval-Augmented Generation (RAG), and dynamic configurations. Whether you're a developer, writer, or hobbyist, ChatNow makes it easy to spin up a tailored chatbot without writing mountains of code.

The app's source code is permanently hosted on GitHub at [https://github.com/rod-trent/JunkDrawer/tree/main/ChatNow](https://github.com/rod-trent/JunkDrawer/tree/main/ChatNow). In this blog post, I'll cover everything you need to know: what ChatNow is, the problem it solves, why it's valuable, its key features, requirements, implementation steps, and how to use it. Let's get started!

## What is ChatNow?

ChatNow is a Python application built with Streamlit that serves as a "Custom Chatbot Creator." It leverages xAI's SDK to interact with advanced language models like Grok-4, allowing users to configure and launch AI assistants on the fly. The app supports various roles (e.g., general helper, coding expert) and integrates tools for web searching, X (formerly Twitter) searching, code execution, or even processing local documents via RAG.

At its core, ChatNow is a chat interface where you configure the bot's personality and capabilities upfront, then engage in conversations. It handles chat history, streams responses in real-time, and even updates the page title dynamically based on your configuration. The code is modular, using modern libraries for file parsing, embeddings, and vector storage to enable intelligent document querying.

## The Problem It Solves

Building a chatbot from scratch often involves juggling multiple components: API integrations, prompt engineering, tool handling, and knowledge base management. For non-experts, this can be overwhelming—requiring knowledge of APIs like xAI's, handling state in web apps, and implementing features like RAG for private data.

ChatNow solves this by providing a ready-to-use framework. It abstracts away the complexities of:
- Integrating with xAI's SDK (including auto-detecting SDK versions for tool compatibility).
- Managing chat sessions and history in a Streamlit app.
- Implementing RAG for local files without needing a full-scale vector database setup.
- Handling dynamic tools like web searches or code execution safely.
- Ensuring a user-friendly UI for configuration and interaction.

In essence, it bridges the gap between powerful AI backends and simple, deployable frontends, making AI assistants accessible for personal projects, prototyping, or even small-scale production use.

## Why It's Valuable

ChatNow's value lies in its flexibility and efficiency. Here's why it's a game-changer:
- **Customization Without Complexity**: Quickly prototype bots for specific tasks, like code debugging or creative writing, without rebuilding the app each time.
- **Privacy-Focused RAG**: Process sensitive documents locally (e.g., PDFs or Word files) without uploading them to external services, enhancing data security.
- **Tool Integrations**: Extend the bot's capabilities with real-world tools, turning a simple chat into a powerful assistant for research, coding, or analysis.
- **Cost-Effective**: Runs locally or on free platforms like Streamlit Sharing, with minimal dependencies. It uses open-source embeddings from Hugging Face, avoiding pricey cloud services.
- **Educational Tool**: Great for learning about AI integrations, as the code is clean and well-commented.
- **Future-Proof**: Designed with 2025+ libraries in mind, including LangChain updates and xAI SDK compatibility.

In a world where AI is everywhere, ChatNow empowers users to create value-added bots tailored to niche needs, saving time and reducing development overhead.

## Key Features

ChatNow packs a lot into a single script. Here's a breakdown of its features:

### Preset Roles and Custom Prompts
- Choose from predefined roles with tailored system prompts and models:
  - **General Assistant**: "You are a helpful, witty AI assistant." (Uses Grok-4)
  - **Coding Helper**: "You are an expert programmer. Provide clean, working code." (Uses Grok-Code-Fast-1 for efficiency)
  - **Creative Writer**: "You are a talented creative writer." (Grok-4)
  - **Math & Science**: "You are a precise expert in math and science. Show steps." (Grok-4)
  - **Custom**: Enter your own system prompt for full flexibility (Grok-4).
- This allows the bot to adapt its tone and expertise instantly.

### Knowledge Sources and Tools
- Select from multiple "Knowledge Sources" to enhance the bot:
  - **None**: Basic chat without extras.
  - **Web Search**: Integrates xAI's web_search tool for internet queries.
  - **X Search**: Uses x_search for searching posts on X (Twitter).
  - **Code Execution**: Enables code_execution tool for running Python code in a safe, stateful REPL environment.
  - **Local File (RAG)**: Upload a file and query it intelligently (more below).
- Tools are auto-detected and adapted for xAI SDK versions, ensuring compatibility.

### Local RAG Support
- Upload PDF, DOCX, TXT, or JSON files.
- Extracts text using libraries like pdfplumber and python-docx.
- Splits text into chunks (size 1000, overlap 200) with LangChain's RecursiveCharacterTextSplitter.
- Builds a local FAISS vector store with Hugging Face embeddings ("sentence-transformers/all-MiniLM-L6-v2").
- Retrieves top-K (4) relevant chunks for context in queries, appending them to the system prompt.
- Handles errors gracefully and caches resources for performance.

### Chat Interface
- Real-time streaming responses with a typing cursor ("▌").
- Persists chat history in session state.
- Dynamic page title based on the bot's role (e.g., "Coding Helper" or a snippet of your custom prompt).
- Sidebar status indicators for RAG activation and bot details.
- "New Assistant" button to reset and reconfigure.

### Other Technical Features
- Environment variable loading (.env) for XAI_API_KEY.
- Temporary file handling for uploads.
- Caching for client and embeddings to optimize performance.
- Error handling for file parsing and API calls.
- Powered by xAI's chat API with a 3600-second timeout.

## Requirements

To run ChatNow, you'll need:
- **Python**: 3.10+ (tested with 3.12 implicitly via dependencies).
- **Libraries** (install via pip):
  - streamlit
  - xai_sdk (xAI's official SDK)
  - python-dotenv
  - pdfplumber (for PDFs)
  - python-docx (for DOCX)
  - langchain-text-splitters
  - langchain-community (for FAISS)
  - langchain-huggingface (for embeddings)
  - faiss-cpu (implicit via langchain-community)
  - Other implicit deps: json, shutil, tempfile, pathlib.
- **API Key**: An XAI_API_KEY from xAI (add to a .env file).
- **Hardware**: Basic CPU for embeddings; no GPU required, but FAISS can benefit from one for larger docs.
- **No Internet for RAG**: Local processing only, but tools like web_search need connectivity.

Note: The app doesn't install extra packages at runtime—ensure they're in your environment.

## How to Implement It

Implementing ChatNow is straightforward. Follow these steps:

1. **Clone or Download the Code**:
   - Grab it from GitHub: `git clone https://github.com/rod-trent/JunkDrawer.git`
   - Navigate to `JunkDrawer/ChatNow` for the `chatnow.py` file (or copy the code provided earlier).

2. **Set Up Your Environment**:
   - Create a virtual environment: `python -m venv venv` and activate it.
   - Install dependencies: `pip install streamlit xai-sdk python-dotenv pdfplumber python-docx langchain-text-splitters langchain-community langchain-huggingface`.
   - (Optional) For FAISS: `pip install faiss-cpu`.

3. **Configure .env**:
   - Create a `.env` file in the project root.
   - Add: `XAI_API_KEY=your_key_here` (get from xAI's dashboard).

4. **Run the App**:
   - Execute: `streamlit run chatnow.py`
   - Open the local URL (usually http://localhost:8501) in your browser.

5. **Customization (Optional)**:
   - Edit `PRESET_PROMPTS` or `TOOLS` in the code to add more roles or tools.
   - Adjust constants like `CHUNK_SIZE` for RAG tuning.
   - Deploy to Streamlit Cloud or similar for sharing.

If you encounter issues, check the console for errors—common ones include missing API keys or incompatible SDK versions.

## How to Use It

Using ChatNow is intuitive:

1. **Launch and Configure**:
   - On first load, you'll see "Configure Your New Assistant."
   - Select a Role (e.g., "Coding Helper") from the dropdown.
   - If "Custom," enter a system prompt like "You are a history expert."
   - Choose a Knowledge Source (e.g., "Web Search" for internet access).
   - Click "Launch Assistant." The page reloads with a dynamic title.

2. **Add Knowledge (If RAG)**:
   - If you selected "Local File (RAG)," upload your document.
   - The app indexes it automatically—status shows "RAG Active."

3. **Chat Away**:
   - Type your query in the chat input (e.g., "Explain quantum entanglement" for Math & Science role).
   - The bot responds with streaming text, using tools or RAG as needed.
   - History builds up—scroll to review.

4. **Reset**:
   - Click "New Assistant" to start over and reconfigure.

Pro Tip: For RAG, ask specific questions about the document's content. If irrelevant, the bot is prompted to say "I don't know."

## Conclusion

ChatNow is a fantastic example of how Streamlit and xAI can democratize AI development. It solves real-world problems in chatbot creation, offers immense value through its features, and is easy to set up and use. Whether you're building a personal assistant or experimenting with RAG, give it a try—head over to the [GitHub repo](https://github.com/rod-trent/JunkDrawer/tree/main/ChatNow) and start chatting!

If you have feedback or improvements, fork the repo and contribute. Happy building! 🚀
