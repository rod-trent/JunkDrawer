# Azure_Gork.py – FINAL WORKING VERSION (Dec 2025)

import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI, NotFoundError   # ← this line fixes the NameError
import os
import requests

load_dotenv()

# ==========================
# 1. Load config
# ==========================
API_KEY    = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT   = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not all([API_KEY, ENDPOINT, DEPLOYMENT]):
    st.error(
        "Missing values in .env file!\n\n"
        "Example:\n"
        "AZURE_OPENAI_API_KEY=1234567890abcdef...\n"
        "AZURE_OPENAI_ENDPOINT=https://myresource.openai.azure.com/\n"
        "AZURE_OPENAI_DEPLOYMENT=zorkgpt"
    )
    st.stop()

# Force exactly one trailing slash
ENDPOINT = ENDPOINT.strip().rstrip("/") + "/"

client = AzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    api_version="2024-10-21"          # Latest stable GA version
)

# ==========================
# 2. Simple live connection test (safe & reliable)
# ==========================
st.sidebar.header("Diagnostics")
try:
    # Quick 1-token test call — this proves everything works
    client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[{"role": "user", "content": "say ok"}],
        max_tokens=5,
        temperature=0
    )
    st.sidebar.success(f"Deployment '{DEPLOYMENT}' is working!")
except NotFoundError:
    st.sidebar.error(f"Deployment '{DEPLOYMENT}' not found!")
    st.sidebar.info("Go to Azure Portal → Model deployments → copy the exact Name")
    st.stop()
except Exception as e:
    st.sidebar.error("Connection failed")
    st.sidebar.code(str(e))
    st.stop()

# ==========================
# 3. Load Zork source
# ==========================
@st.cache_data(ttl=3600)
def fetch_zork_source():
    files = ["ZORK1.ZIL","DUNGEON.ZIL","PARSER.ZIL","SYNTAX.ZIL","OBJECTS.ZIL","ROOMS.ZIL"]
    sources = {}
    base = "https://raw.githubusercontent.com/historicalsource/zork1/main/"
    for f in files:
        try:
            r = requests.get(base + f, timeout=10)
            if r.status_code == 200:
                sources[f] = r.text
        except:
            pass
    return sources

full_zork_context = "\n\n".join([
    f"--- {f} ---\n{c[:12000]}" for f, c in fetch_zork_source().items()
])

# ==========================
# 4. Game start
# ==========================
st.set_page_config(page_title="Azure Gork", page_icon="Castle", layout="centered")
st.title("Castle Azure Gork")
st.markdown("**Zork I** – powered by your own Azure OpenAI deployment")

if "messages" not in st.session_state:
    system_prompt = f"""
You are narrating a completely faithful version of Zork I: The Great Underground Empire (1980 Infocom).
Use only original rooms, objects, puzzles and classic terse style.
Never mention AI, Azure, or anything modern.

Reference ZIL source excerpts:
{full_zork_context}

Begin west of the white house.
"""
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": """West of House

You are standing in an open field west of a white house, with a boarded front door.
There is a small mailbox here."""}
    ]

# Show history
for msg in st.session_state.messages[1:]:
    if msg["role"] == "assistant":
        st.markdown(f"**{msg['content']}**")
    else:
        st.markdown(f"> {msg['content']}")

# Player input
if prompt := st.chat_input("What do you do?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"> {prompt}")

    with st.spinner("..."):
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=st.session_state.messages,
            temperature=0.8,
            max_tokens=500
        )
        reply = response.choices[0].message.content.strip()
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.markdown(f"**{reply}**")

# Sidebar
with st.sidebar:
    st.code("""open mailbox
go north
take lamp
light lamp
go down""", language="text")
    if st.button("Restart Game"):
        st.session_state.clear()
        st.rerun()