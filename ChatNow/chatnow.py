# app.py — FINAL + DYNAMIC PAGE TITLE (December 2025)
import streamlit as st
import os
import json
import shutil
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# xAI SDK
from xai_sdk import Client
from xai_sdk.chat import user, system, assistant
from xai_sdk.tools import web_search, x_search, code_execution

# File parsing
import pdfplumber
from docx import Document

# LangChain (2025+)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# --- Auto-detect SDK version and fix tools ---
def get_tools_list(name: str):
    tool_map = {
        "Web Search": web_search,
        "X Search": x_search,
        "Code Execution": code_execution,
    }
    tool = tool_map.get(name)
    if tool is None:
        return []
    try:
        if hasattr(tool, "name"):  # New SDK: already a Tool object
            return [tool]
        else:                      # Old SDK: it's a function
            return [tool()]
    except:
        return [tool() if callable(tool) else tool]

TOOLS = {
    "None": [],
    "Web Search": get_tools_list("Web Search"),
    "X Search": get_tools_list("X Search"),
    "Code Execution": get_tools_list("Code Execution"),
    "Local File (RAG)": [],
}

# --- Constants ---
FAISS_INDEX_PATH = "faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RETRIEVE_K = 4

# --- Cached Resources ---
@st.cache_resource(show_spinner=False)
def get_client():
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        st.error("Please add XAI_API_KEY to .env file")
        st.stop()
    return Client(api_key=api_key, timeout=3600)

@st.cache_resource(show_spinner="Loading embedding model...")
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

client = get_client()
embeddings = get_embeddings()
splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

# --- Prompts ---
PRESET_PROMPTS = {
    "General Assistant": "You are a helpful, witty AI assistant.",
    "Coding Helper": "You are an expert programmer. Provide clean, working code.",
    "Creative Writer": "You are a talented creative writer.",
    "Math & Science": "You are a precise expert in math and science. Show steps.",
}

MODELS = {key: "grok-4" for key in PRESET_PROMPTS}
MODELS["Coding Helper"] = "grok-code-fast-1"
MODELS["Custom"] = "grok-4"

# --- Extract text ---
def extract_text(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix.lower()
    text = ""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / uploaded_file.name
        file_path.write_bytes(uploaded_file.getvalue())
        try:
            if suffix == ".txt":
                text = file_path.read_text(encoding="utf-8")
            elif suffix == ".json":
                text = json.dumps(json.loads(file_path.read_text()), indent=2)
            elif suffix == ".pdf":
                with pdfplumber.open(file_path) as pdf:
                    text = "\n\n".join(p.extract_text() or "" for p in pdf.pages)
            elif suffix in [".docx", ".doc"]:
                doc = Document(file_path)
                text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            st.error(f"Error reading file: {e}")
    return text.strip()

def get_vectorstore(text: str):
    if os.path.exists(FAISS_INDEX_PATH):
        return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    if not text:
        return None
    chunks = splitter.split_text(text)
    vs = FAISS.from_texts(chunks, embeddings)
    vs.save_local(FAISS_INDEX_PATH)
    return vs

# --- Sidebar ---
with st.sidebar:
    st.header("Status")
    if st.session_state.get("vector_store"):
        st.success("RAG Active")
    if st.session_state.get("bot_type"):
        st.caption(f"Role: {st.session_state.bot_type}")
        st.caption(f"Source: {st.session_state.data_source}")

# === DYNAMIC PAGE TITLE + CONFIG ===
if not st.session_state.get("initialized"):
    st.title("Custom Chatbot Creator")
else:
    # DYNAMIC PAGE TITLE
    if st.session_state.bot_type == "Custom" and st.session_state.custom_prompt:
        short = st.session_state.custom_prompt.strip().split("\n")[0][:40]
        page_title = f"Custom: {short}..." if len(short) >= 40 else f"Custom: {short}"
    else:
        page_title = st.session_state.bot_type

    st.set_page_config(page_title=page_title, page_icon="robot", layout="centered")
    # One-time rerun to apply title
    if not st.session_state.get("_title_applied", False):
        st.session_state._title_applied = True
        st.rerun()

st.subheader("Configure your custom chatbot below" if not st.session_state.get("initialized") else page_title)
st.caption("Powered by xAI • Local RAG • Web & Code Tools")

# === Configuration ===
if not st.session_state.get("initialized"):
    st.subheader("Configure Your New Assistant")
    col1, col2 = st.columns(2)
    with col1:
        bot_type = st.selectbox("Role", options=list(PRESET_PROMPTS.keys()) + ["Custom"])
        custom_prompt = None
        if bot_type == "Custom":
            custom_prompt = st.text_area("Custom System Prompt", height=140)

    with col2:
        data_source = st.selectbox("Knowledge Source", options=list(TOOLS.keys()))

    if st.button("Launch Assistant", type="primary", use_container_width=True):
        if bot_type == "Custom" and (not custom_prompt or custom_prompt.strip() == ""):
            st.error("Please enter a custom prompt")
        else:
            st.session_state.initialized = True
            st.session_state.bot_type = bot_type
            st.session_state.custom_prompt = custom_prompt
            st.session_state.data_source = data_source
            st.session_state.messages = []
            st.session_state.vector_store = None
            st.session_state._title_applied = False  # Allow title update on next load
            st.success("Assistant ready!")
            st.rerun()
else:
    # === Chat Mode ===
    bot_type = st.session_state.bot_type
    system_prompt = st.session_state.custom_prompt if bot_type == "Custom" else PRESET_PROMPTS.get(bot_type, PRESET_PROMPTS["General Assistant"])
    model = MODELS.get(bot_type, "grok-4")

    # RAG Upload
    if st.session_state.data_source == "Local File (RAG)" and not st.session_state.get("vector_store"):
        uploaded = st.file_uploader("Upload PDF, DOCX, TXT, or JSON", type=["pdf", "docx", "txt", "json"])
        if uploaded:
            with st.spinner("Indexing document..."):
                text = extract_text(uploaded)
                if len(text) < 50:
                    st.error("Document is empty")
                else:
                    st.session_state.vector_store = get_vectorstore(text)
                    st.success(f"Ready! Ask anything about {uploaded.name}")
                    st.rerun()

    # Chat History
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # RAG Context
        context_prompt = ""
        if st.session_state.data_source == "Local File (RAG)" and st.session_state.vector_store:
            docs = st.session_state.vector_store.similarity_search(prompt, k=RETRIEVE_K)
            context = "\n\n".join(doc.page_content for doc in docs)
            context_prompt = f"Use this information from the document:\n{context}\n\nIf not relevant, say you don't know."

        full_prompt = f"{system_prompt}\n\n{context_prompt}".strip()

        # Call Grok
        with st.chat_message("assistant"):
            placeholder = st.empty()
            response = ""
            chat = client.chat.create(
                model=model,
                tools=TOOLS[st.session_state.data_source]
            )
            chat.append(system(full_prompt))
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    chat.append(user(msg["content"]))
                else:
                    chat.append(assistant(msg["content"]))

            for _, chunk in chat.stream():
                if chunk.content:
                    response += chunk.content
                    placeholder.markdown(response + "▌")
            placeholder.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button("New Assistant"):
        st.session_state.clear()
        if os.path.exists(FAISS_INDEX_PATH):
            shutil.rmtree(FAISS_INDEX_PATH)
        st.rerun()