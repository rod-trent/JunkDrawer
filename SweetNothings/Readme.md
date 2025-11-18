# ❤️ The “Husband’s Sweet Nothings Generator” – A Tiny Streamlit App That Helps Men Love Their Wives Better

(Yes, even the strong, silent types sometimes need a little help saying the right thing.)

I built a dead-simple web app that uses Grok (from xAI) to generate short, masculine, heartfelt messages that actually sound like a real husband texting his wife – not a Hallmark card on steroids.

It takes 30 seconds to set up, costs pennies per month, and has already saved countless marriages from the dreaded “k” reply.

Link to the code (copy-paste ready): https://github.com/rod-trent/JunkDrawer/blob/main/SweetNothings/SweetNothings.py (or just copy the script below)

### What it is

A Streamlit app called **Husband’s Sweet Nothings Generator** ❤️

You click one big shiny button → Grok instantly writes 1–3 sentences of warm, confident, slightly playful love that makes her feel seen, safe, and beautiful.

Examples of what it spits out:

> “Rough day, huh? Come here, let me hold you until all of it fades away. You’re still the most gorgeous woman I’ve ever laid eyes on.”

> “Just walked past the bedroom and saw you reading… damn, babe. How did I get this lucky? 😘”

> “Goodnight, beautiful. I’m the guy who still gets butterflies when you walk in the room. Sleep tight.”

No flowery nonsense. No “my queen” unless that’s actually your vibe. Just real-man energy with genuine heart.

### Why I built it

My wife sent me the classic trap question one night:  
“Do I look good in this?”

My brain went full Windows loading screen.

I managed a weak “Of course, babe” and immediately realized how weak of an answer that was.

Now whenever I’m stuck, I rev up whit app, hit the button, tweak one word if needed, hit copy, and send. She lights up. Marriage saved. Ego restored.

### How it works (under the hood)

- Streamlit frontend (one file, zero HTML/CSS pain)
- Calls the official xAI/Grok API (`https://api.x.ai/v1/chat/completions`)
- Uses the very reliable `grok-2-1212` model (as of November 2025 – this is the one that actually works consistently)
- Carefully crafted system prompt that forces masculine, grounded, loving tone
- Optional context: her current mood, what she just texted, occasion (good morning, after work, anniversary, etc.)
- Copies straight to clipboard with one click
- Keeps the last 12 messages in history so you never repeat yourself

### Requirements

1. Python 3.9+
2. A free or paid xAI API key → https://console.x.ai
3. About 5 minutes of your time

### How to install and run it (step-by-step)

1. Save the code below as `SweetNothings.py`
2. Create a `.env` file in the same folder with your key:

   ```
   GROK_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

3. Install the dependencies:

   ```bash
   pip install streamlit requests python-dotenv pyperclip
   ```

4. Run it:

   ```bash
   streamlit run SweetNothings.py
   ```

That’s it. It will open in your browser automatically.

### How to use it (the wife-approved workflow)

1. (Optional) Fill the sidebar:
   - How is she feeling? → “stressed”, “insecure”, “glowing”, etc.
   - What did she just text? → paste it verbatim
   - Occasion → Good morning, After a long day, etc.

2. Smash the big ✨ Generate Sweet Nothing ✨ button

3. Read it. If it’s 98% perfect (it usually is), hit Copy → paste into iMessage/Whatsapp.

   If you want it a tiny bit different, just hit the button again – it will give you a fresh one.

Pro tip: Generate 2–3, pick the best, maybe swap one emoji or add her nickname. Takes 10 seconds and feels 100% authentic.

### The full code (copy-paste ready)

```python
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

        except Exception as e:
            st.error(f"Error: {e}")
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
```

Deploy it on Streamlit Community Cloud, Railway, or just run locally – your choice.

Go be the husband she brags about to her friends.

You’re welcome 😉❤️
