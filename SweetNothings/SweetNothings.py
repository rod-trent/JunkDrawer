import streamlit as st
import requests
import os
from dotenv import load_dotenv
import pyperclip
from datetime import datetime

# Load API key
load_dotenv()
GROK_API_KEY = os.getenv("GROK_API_KEY")

if not GROK_API_KEY:
    st.error("⚠️ Please add your GROK_API_KEY to the .env file")
    st.stop()

# === CURRENT WORKING xAI SETTINGS (November 2025) ===
API_URL = "https://api.x.ai/v1/chat/completions"
WORKING_MODEL = "grok-2-1212"   # This is the reliable one right now
# Fallback models if you want (rarely needed)
FALLBACK_MODELS = ["grok-2-latest", "grok-beta"]

st.set_page_config(
    page_title="❤️ Husband's Sweet Nothings Generator",
    page_icon="❤️",
    layout="centered"
)

st.title("❤️ Husband's Sweet Nothings Generator")
st.caption("For the masculine husband who wants to make his wife feel like the only woman in the world")

# Sidebar for context
with st.sidebar:
    st.header("🛠 Optional Context")
    mood = st.text_input("How is she feeling?", placeholder="tired, beautiful, stressed, happy, insecure...")
    recent_text = st.text_area("What did she just say/text?", placeholder="e.g. \"Rough day\" or \"Do you still find me pretty?\"")
    occasion = st.selectbox("Occasion", [
        "Just because",
        "Good morning ☀️",
        "Good night 🌙",
        "After a long day",
        "She's feeling down",
        "Date night",
        "Anniversary vibes",
        "Random compliment",
        "She's glowing today"
    ])

# History
if "history" not in st.session_state:
    st.session_state.history = []

def generate_sweet_nothing():
    with st.spinner("Grok is writing something that’ll make her heart skip..."):
        system_prompt = (
            "You are a strong, confident, deeply devoted husband. "
            "You speak with quiet strength, warmth, and playful charm. "
            "Your words make your wife feel beautiful, safe, and wildly loved. "
            "Never cheesy or over-the-top. 1–3 sentences max. Use emojis sparingly and naturally."
        )

        user_prompt = "Write a loving, masculine sweet nothing"

        if occasion != "Just because":
            user_prompt += f" for {occasion.lower()}"

        if mood.strip():
            user_prompt += f". She's feeling {mood.lower()}"

        if recent_text.strip():
            user_prompt += f". She just said: \"{recent_text}\""

        user_prompt += ". Make it sound like a real husband texting his wife."

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "model": WORKING_MODEL,
            "temperature": 0.85,
            "max_tokens": 150
        }

        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 404:
                st.error("Model not found. Trying fallback...")
                payload["model"] = FALLBACK_MODELS[0]
                response = requests.post(API_URL, json=payload, headers=headers, timeout=30)

            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"].strip()

            # Save to history
            entry = {
                "text": result,
                "time": datetime.now().strftime("%H:%M:%S"),
                "context": occasion + (f" • {mood}" if mood else "")
            }
            st.session_state.history.insert(0, entry)
            return result

        except requests.exceptions.HTTPError as e:
            st.error(f"API Error: {response.status_code} – {e}")
            if response.text:
                st.code(response.text)
            return None
        except Exception as e:
            st.error(f"Connection error: {e}")
            return None

# Main generate button
if st.button("✨ Generate Sweet Nothing ✨", type="primary", use_container_width=True):
    sweet_nothing = generate_sweet_nothing()
    if sweet_nothing:
        st.success("Here you go, king 👑")
        st.markdown(f"### {sweet_nothing}")

        col1, col2 = st.columns([4, 1])
        with col1:
            st.code(sweet_nothing, language=None)
        with col2:
            if st.button("📋 Copy", key="copy_main"):
                pyperclip.copy(sweet_nothing)
                st.toast("Copied to clipboard ❤️", icon="❤️")

# History section
if st.session_state.history:
    st.markdown("---")
    st.subheader("🕛 Recent Sweet Nothings")
    for i, entry in enumerate(st.session_state.history[:12]):
        with st.expander(f"{entry['time']} • {entry['context'] or 'Just because'}"):
            st.write(entry["text"])
            if st.button("Copy again", key=f"copy_{i}"):
                pyperclip.copy(entry["text"])
                st.toast("Copied ❤️")

st.markdown("---")
st.caption("Made with ❤️ for husbands who love deeply but aren’t always great with words")