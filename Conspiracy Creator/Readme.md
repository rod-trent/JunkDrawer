# Wake Up, Sheeple!  
## Introducing the Grok-Powered Real-Time Conspiracy Theorist Simulator  
*(Now with 100% more red string and zero Illuminati approval)*

Published: November 17, 2025  
Author: A totally normal citizen who definitely isn’t hiding in a bunker

### The Greatest Toy Ever Built for the Terminally Online

Imagine this: you see a boring headline like “FDA approves new breakfast cereal” or “Clouds spotted over Midwest.”  
A normal person shrugs and moves on.  
You? You know better.  
You fire up the Real-Time Conspiracy Theorist Simulator and watch Grok instantly spin a 2,000-word manifesto proving that the cereal is actually a 5G mind-control vector deployed by the Reptilian Grain Cartel.

That’s exactly what this little Streamlit app does — and it does it using nothing but the official xAI Grok API.

### What It Actually Is

A single-file web app that:
1. Takes any news headline or article URL
2. Feeds it to Grok (your choice of Grok-4, Grok-3, or Grok-3-mini)
3. Makes Grok role-play as the most enthusiastic (or sarcastically detached) conspiracy theorist alive
4. Lets you control:
   - Intensity: Plausible → Classic Deep State → Full Lizard People
   - Sarcasm slider: 0 (shouting Infowars host) → 10 (The Onion on bath salts)
5. Streams the unhinged rant back to you in real time

It is pure entertainment. Zero practical use. Maximum chaotic good.

### Requirements & Installation (Takes ~60 seconds)

#### 1. Get an xAI API key
Go to https://x.ai/api and create one. Yes, it costs money if you hammer it, but casual use is very cheap.

#### 2. Install Python dependencies (one command)
```bash
pip install streamlit requests beautifulsoup4 python-dotenv
```

#### 3. Save the script
Copy the full code below into a file called `conspiracy_simulator.py`

#### 4. Create a .env file in the same folder
```env
XAI_API_KEY=your_actual_key_here_dont_share_it
```

That’s it. No Docker, no virtualenv drama required (though you can if you want).

### The Full Code (Copy-Paste Ready)

```python
import os
import requests
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()  # Loads XAI_API_KEY from .env

XAI_API_KEY = os.getenv("XAI_API_KEY")
API_URL = "https://api.x.ai/v1/chat/completions"

GROK_MODELS = {
    "Grok 4 (smartest)": "grok-4",
    "Grok 3 (fast & balanced)": "grok-3",
    "Grok 3 Mini (cheapest)": "grok-3-mini"
}

def extract_text_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        text = soup.get_text(se v2 separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text[:15000]
    except Exception as e:
        return f"[Could not fetch article: {e}]"

st.set_page_config(page_title="🕵️‍♂️ Grok Conspiracy Simulator", page_icon="🤫", layout="centered")
st.title("🕵️‍♂️ Real-Time Conspiracy Theorist Simulator")
st.caption("100% Grok xAI API powered • Turn any news into certified 🌶️ tinfoil")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("xAI API Key", value=XAI_API_KEY or "", type="password",
                            help="Auto-loaded from .env • Get at https://x.ai/api")
    if XAI_API_KEY and not api_key:
        st.success("✓ API key loaded from .env")

    model = st.selectbox("Grok Model", options=list(GROK_MODELS.keys()), index=1)
    model_id = GROK_MODELS[model]
    
    intensity = st.select_slider("Conspiracy Intensity",
        options=["Plausible (quietly terrifying)", "Wild (classic deep state)", "Unhinged (lizard people tier)"],
        value="Wild (classic deep state)")
    
    sarcasm = st.slider("Sarcasm Level", 0, 10, 5,
                        help="0 = dead serious • 10 = maximum satire")

news_input = st.text_area("Feed me a news event (headline or URL):",
    height=120,
    placeholder="e.g. https://www.bbc.com/news/world-us-canada-12345678\nor “New flavor of LaCroix released”")

if st.button("🧠 Connect the dots…", type="primary"):
    if not api_key:
        st.error("No API key! Add it to .env or type it above.")
        st.stop()
    if not news_input.strip():
        st.warning("Need something to theorize about!")
        st.stop()

    with st.spinner("Donning tinfoil hat…"):
        if news_input.strip().startswith("http"):
            with st.status("Scraping article…"):
                article_text = extract_text_from_url(news_input)
            user_content = f"Article text:\n{article_text}"
        else:
            user_content = news_input

        intensity_map = {
            "Plausible (quietly terrifying)": "highly plausible-sounding but secretly insane",
            "Wild (classic deep state)": "classic conspiracy energy with cabals and false flags",
            "Unhinged (lizard people tier)": "maximum absurdity — reptilians, hollow moon, time cubes, all of it"
        }

        system_prompt = f"""
You are the ultimate conspiracy theorist. Take the news below and create the most {intensity_map[intensity]} theory possible.
Include fake evidence chains, links to historical events, secret groups, and a final bombshell.
Sarcasm level: {sarcasm}/10 (0 = raging true-believer, 10 = dripping mockery).
Never break character.
"""

        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}]

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 1.0 if sarcasm < 8 else 1.4,
            "max_tokens": 4096,
            "stream": True
        }

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        placeholder = st.empty()
        full = ""

        try:
            with requests.post(API_URL, json=payload, headers=headers, stream=True) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        decoded = line.decode("utf-8")
                        if decoded.startswith("data: "):
                            data = decoded[6:]
                            if data.strip() == "[DONE]": break
                            chunk = json.loads(data)
                            if "content" in chunk["choices"][0]["delta"]:
                                text = chunk["choices"][0]["delta"]["content"]
                                full += text
                                placeholder.markdown(full + "▊")
            placeholder.markdown(full)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                st.error("Bad API key — check your .env")
            elif e.response.status_code == 429:
                st.error("Rate limited. Take a breath, grab some water (not the fluoridated kind).")
            else:
                st.error(f"API error: {e}")

st.caption("Built by someone who knows where you live • Not affiliated with any three-letter agencies (that we know of)")
```

### How to Run It

```bash
streamlit run conspiracy_simulator.py
```

Your browser opens → http://localhost:8501 → instant paranoia machine.

### Example Prompts That Will Ruin Your Faith in Reality
- “Birds aren’t real”
- Any article about weather modification
- “Taylor Swift endorses soda”
- Today’s top headline on any news site (literally any)

### Final Warning

This app is dangerously funny.  
Do not operate heavy machinery while reading Grok’s theories at sarcasm 10.  
Side effects may include: questioning reality, stockpiling canned goods, and drawing red string on your monitor with a dry-erase marker.

You’ve been warned.  
Now go expose the truth about why the new iPhone has one less button than last year.

They’re listening.  
Act natural.

🤫🕵️‍♂️
