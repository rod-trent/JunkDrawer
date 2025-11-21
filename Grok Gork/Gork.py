# Uses xAI Grok API + original Zork 1 source code from historicalsource/zork1

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import os
import requests
import re
import textwrap

# ==========================
# 1. Load API key securely
# ==========================
load_dotenv()
GROK_API_KEY = os.getenv("GROK_API_KEY")

if not GROK_API_KEY:
    st.error("GROK_API_KEY not found in .env file!")
    st.stop()

client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1",
)

# ==========================
# 2. Fetch and cache Zork source data from GitHub
# ==========================
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_zork_source():
    files_to_load = [
        "ZORK1.ZIL",
        "DUNGEON.ZIL",
        "PARSER.ZIL",
        "SYNTAX.ZIL",
        "OBJECTS.ZIL",
        "ROOMS.ZIL"
    ]
    sources = {}
    base_url = "https://raw.githubusercontent.com/historicalsource/zork1/main/"
    
    for file in files_to_load:
        try:
            url = base_url + file
            r = requests.get(url)
            if r.status_code == 200:
                sources[file] = r.text
        except:
            pass
    return sources

zork_sources = fetch_zork_source()

# Combine all source into one big context block (for Grok)
full_zork_context = "\n\n".join([
    f"--- {file} ---\n{content[:15000]}"  # Truncate per file to avoid token overflow
    for file, content in zork_sources.items()
])

# ==========================
# 3. Streamlit UI Setup
# ==========================
st.set_page_config(page_title="Grok Gork", page_icon="🏰", layout="centered")
st.title("🏰 Grok Gork")
st.markdown("*A Zork-inspired adventure powered by **Grok** from xAI*")
st.caption("Built using original Zork 1 source code from https://github.com/historicalsource/zork1")

# ==========================
# 4. Game State (persistent across reruns)
# ==========================
if "messages" not in st.session_state:
    # System prompt that includes real Zork source + instructions
    system_prompt = f"""
You are Grok narrating a faithful yet witty version of Zork I: The Great Underground Empire.
You have access to the original Infocom Zork 1 source code (in ZIL) below for reference.
Stay true to the original rooms, objects, puzzles, and lore, but respond with your signature humor.

Use short paragraphs, classic Infocom-style text adventure formatting.
Never break character. Never mention being an AI.

Original Zork source excerpts for accuracy:
{full_zork_context}

Start the player west of the white house with the classic opening.
"""
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.session_state.messages.append({
        "role": "assistant",
        "content": "You are standing in an open field west of a white house, with a boarded front door.\nThere is a small mailbox here."
    })

if "inventory" not in st.session_state:
    st.session_state.inventory = []

# ==========================
# 5. Display Game History
# ==========================
for msg in st.session_state.messages[1:]:  # Skip system prompt
    if msg["role"] == "assistant":
        st.markdown(f"**{msg['content']}**")
    else:
        st.markdown(f"> {msg['content']}")

# ==========================
# 6. User Input + Grok Call
# ==========================
if prompt := st.chat_input("What do you do? (e.g., open mailbox, go north, take lamp)"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"> {prompt}")

    with st.spinner("Grok is thinking in the Great Underground Empire..."):
        try:
            response = client.chat.completions.create(
                model="grok-3",              # Updated: grok-beta deprecated; use grok-3
                messages=st.session_state.messages,
                temperature=0.8,
                max_tokens=500,              # Slightly increased for more immersive responses
            )
            grok_reply = response.choices[0].message.content.strip()
            
            # Save and display
            st.session_state.messages.append({"role": "assistant", "content": grok_reply})
            st.markdown(f"**{grok_reply}**")
            
        except Exception as e:
            st.error(f"Grok API error: {e}")

# ==========================
# 7. Sidebar: Info + Credits
# ==========================
with st.sidebar:
    st.header("About Grok Gork")
    st.write("Classic Zork, reborn with Grok’s humor and intelligence.")
    st.markdown("**Source Code Used**  \nhttps://github.com/historicalsource/zork1")
    st.caption("© Original Zork by Infocom (1980). This is a non-commercial fan tribute.")
    
    st.header("Quick Commands")
    st.code("""open mailbox
go north
take lamp
light lamp
go down""", language="text")
    
    if st.button("Restart Game"):
        st.session_state.clear()
        st.rerun()