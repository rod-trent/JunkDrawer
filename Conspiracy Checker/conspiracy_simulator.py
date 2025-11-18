import os
import requests
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv  # ← NEW

# Load .env file from the same directory (or parent directories)
load_dotenv()  # ← NEW: automatically loads XAI_API_KEY from .env

# ==== CONFIG ====
XAI_API_KEY = os.getenv("XAI_API_KEY")  # Now comes from .env
API_URL = "https://api.x.ai/v1/chat/completions"

GROK_MODELS = {
    "Grok 4 (smartest)": "grok-4",
    "Grok 3 (fast & balanced)": "grok-3",
    "Grok 3 Mini (cheapest)": "grok-3-mini"
}

# ==== Helper to extract text from URL ====
def extract_text_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text[:15000]
    except Exception as e:
        return f"[Could not fetch article: {e}]"

# ==== Streamlit UI ====
st.set_page_config(page_title="🕵️‍♂️ Grok Conspiracy Simulator", page_icon="🤫", layout="centered")

st.title("🕵️‍♂️ Real-Time Conspiracy Theorist Simulator")
st.caption("Powered 100% by Grok xAI API • Turn any news into pure red-string madness")

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    # Auto-load from .env, but allow manual override if needed
    api_key = st.text_input(
        "xAI API Key", 
        value=XAI_API_KEY or "", 
        type="password",
        help="Loaded automatically from .env file • Get yours at https://x.ai/api"
    )
    
    if not api_key and XAI_API_KEY:
        st.success("✓ API key loaded from .env")
    
    model = st.selectbox("Grok Model", options=list(GROK_MODELS.keys()), index=1)
    model_id = GROK_MODELS[model]
    
    intensity = st.select_slider(
        "Conspiracy Intensity",
        options=["Plausible (quietly terrifying)", "Wild (classic deep state)", "Unhinged (lizard people tier)"],
        value="Wild (classic deep state)"
    )
    
    sarcasm = st.slider("Sarcasm Level", 0, 10, 5, help="0 = dead serious, 10 = maximum mockery")

# Main input
news_input = st.text_area(
    "Feed me a news event (headline or full article URL):",
    height=120,
    placeholder="e.g. https://www.reuters.com/world/something-weird-happened-today\nor just paste: 'Birds aren’t real'"
)

if st.button("🧠 Connect the dots…", type="primary"):
    if not api_key:
        st.error("No API key found! Create a .env file with XAI_API_KEY=your_key_here")
        st.stop()
    if not news_input.strip():
        st.warning("I need something to conspiracize about!")
        st.stop()

    with st.spinner("Waking up the shadow government…"):
        if news_input.strip().startswith("http"):
            with st.status("Extracting article…"):
                article_text = extract_text_from_url(news_input)
            user_content = f"Article text:\n{article_text}"
        else:
            user_content = news_input

        intensity_map = {
            "Plausible (quietly terrifying)": "highly plausible-sounding but secretly insane, with subtle connections and 'credible' sources",
            "Wild (classic deep state)": "classic conspiracy energy with shadowy cabals, false flags, and red-string connections",
            "Unhinged (lizard people tier)": "maximum absurdity — interdimensional beings, flat earth cameos, time-traveling elites, ancient aliens, the works"
        }

        system_prompt = f"""
You are the ultimate conspiracy theorist powered by Grok.
Take the given news and spin the most {intensity_map[intensity]} conspiracy theory possible.
Include:
• Dramatic "revelations"
• Chains of completely made-up but convincing-sounding "evidence"
• Links to at least 3 historical events or other conspiracies
• Secret groups or masterminds
• A final "what they DON'T want you to know" bombshell

Sarcasm/delivery tone: {sarcasm}/10 (0 = raging Infowars host, 10 = dripping satirical chaos).
Stay in character 100%. Never admit it's fake.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 1.0 if sarcasm < 8 else 1.4,
            "max_tokens": 4096,
            "stream": True
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response_placeholder = st.empty()
        full_response = ""

        try:
            with requests.post(API_URL, json=payload, headers=headers, stream=True) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        decoded = line.decode("utf-8")
                        if decoded.startswith("data: "):
                            data = decoded[6:]
                            if data.strip() == "[DONE]":
                                break
                            import json
                            chunk = json.loads(data)
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta:
                                content = delta["content"]
                                full_response += content
                                response_placeholder.markdown(full_response + "▊")
            response_placeholder.markdown(full_response)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                st.error("Invalid API key — double-check your .env file")
            elif e.response.status_code == 429:
                st.error("Rate limited. Chill for a minute or upgrade your plan.")
            else:
                st.error(f"API error {e.response.status_code}: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

st.caption("Built with 💊 by someone who definitely doesn’t work for them • 100% Grok-powered paranoia")