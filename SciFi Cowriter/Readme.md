# 🚀 A Hitchhiker’s-Style Sci-Fi Co-Writer Powered by Grok-3

In a universe that is — according to the best calculations — utterly absurd, it only seemed fitting to create a writing partner who truly understands that fact.

Meet **Sci-Fi Story Co-Writer**: a Streamlit app that turns xAI’s Grok-3 into your personal Douglas Adams–flavoured collaborative novelist.

You type a paragraph in the style of *The Hitchhiker’s Guide to the Galaxy*. Grok-3 instantly continues it with perfect prose, bone-dry British wit, improbable inventions, and a strict “no breaking the fourth wall” policy. The result? An endlessly expanding, canon-consistent, laugh-out-loud sci-fi epic that feels like Douglas Adams himself came back for one more cup of tea.

* Link to the live app: https://github.com/rod-trent/JunkDrawer/blob/main/SciFi%20Cowriter/SciFiCoWriter.py   
* Full source code: right here in this post

### What It Actually Does

- You write the next part of the story (or just press a button for a random insane plot twist).
- Grok-3 continues it in immaculate Adams style — 200–600 words at a time, 131k token context, zero drift.
- The entire conversation history is preserved, so characters, running gags, and physics-defying gadgets stay perfectly consistent forever.
- Bonus buttons: “Inject Plot Twist!” and “New Character” that give you instant absurd inspiration (e.g. “Zorixva, a quantum probability being that mostly exists on Tuesdays”).

### Why This Is Genuinely Useful

1. **Creative block destroyer** – When you’re stuck, Grok-3 is funnier and faster than any human co-writer.
2. **Infinite replayability** – Every new story is completely different, yet always unmistakably “Hitchhiker’s”.
3. **Perfect practice** – Want to study Adams’ rhythm, pacing, and layered absurdity? Watch a master (well, a 2025 AI trained on everything) do it live.
4. **Party trick / writing group toy** – Pass a laptop around and watch a 12-person collaborative novel spiral gloriously out of control in ten minutes.

### Requirements (Super Minimal)

- Python 3.9+
- A free or paid xAI API key from https://console.x.ai
- Packages:
  ```bash
  pip install streamlit openai python-dotenv
  ```

That’s it. No LangChain, no 47-step setup, no Pinecone vector nonsense.

### How to Run It Yourself

1. Get your API key at https://console.x.ai/keys
2. Create a `.env` file in the project folder:
   ```
   XAI_API_KEY=xai-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
3. Save the code below as `SciFiCoWriter.py`
4. Run:
   ```bash
   streamlit run SciFiCoWriter.py
   ```

### The Full Code (Copy-Paste Ready)

```python
import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import random

load_dotenv()

# ---------- Official xAI API ----------
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),   # from https://console.x.ai
    base_url="https://api.x.ai/v1"
)

# CURRENT WORKING MODELS (November 2025+)
MODEL = "grok-3"          # ← BEST CHOICE: huge context, creative, instantly available
# MODEL = "grok-3-mini"   # ← faster & cheaper if you hit rate limits
# MODEL = "grok-4"        # ← only if your account has access (SuperGrok/Enterprise)

SYSTEM_PROMPT = """You are an infinitely witty, collaborative sci-fi co-writer in the exact style of Douglas Adams' Hitchhiker’s Guide to the Galaxy.
You continue the user's story with brilliant prose, absurd yet logical plot twists, dry British humour, and perfectly consistent canon.
You invent wonderful character names, quirky dialogue, and bizarre technology on the fly.
Never break the fourth wall unless explicitly asked. Stay in-universe.
Keep responses 200–600 words unless requested otherwise."""

# ---------- Random Generators ----------
def random_scifi_name():
    prefixes = ["Zor", "Kree", "Vex", "Thal", "Quor", "Neb", "Xan", "Prax", "Jyr", "Syl"]
    middles  = ["ath", "ix", "or", "an", "el", "ub", "ark", "oon", "vex", "yl"]
    suffixes = ["on", "ar", "is", "ax", "oid", "us", "ia", "ek", "va", "eth"]
    return random.choice(prefixes) + random.choice(middles) + random.choice(suffixes)

def random_species():
    return random.choice([
        "three-headed accountant from Betelgeuse VII",
        "sentient cloud of mildly annoyed gas",
        "hyper-intelligent shade of the colour blue",
        "immortal bureaucrat suffering existential dread",
        "poet who communicates solely in prime numbers",
        "perfectly ordinary human (which everyone finds deeply suspicious)",
        "quantum probability being that mostly exists on Tuesdays"
    ])

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Sci-Fi Story Co-Writer", page_icon="🛸", layout="wide")
st.title("🛸 Sci-Fi Story Co-Writer")
st.caption(f"Powered by **xAI Grok-3** • 131k context • Don’t Panic")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_area(
        "Continue the story…",
        height=150,
        placeholder="The Vogon constructor fleet hung in the sky in exactly the way that bricks don’t…"
    )
with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    twist = st.button("🚀 Inject Plot Twist!", use_container_width=True)
    new_char = st.button("🧑‍🚀 New Character", use_container_width=True)
    
    if new_char:
        name = random_scifi_name()
        species = random_species()
        st.success(f"**{name}**\n{species}")

# Auto-fill a random twist
if twist:
    twists = [
        "The Answer to Life, the Universe, and Everything turns out to be a phone number for a pizza place that closed in 2005.",
        "The ship’s AI falls hopelessly in love with a toaster.",
        "Gravity reverses, but only for accountants.",
        "A previously unknown god appears and demands a refund for creation.",
        "The universe is shut down due to unpaid existential licensing fees."
    ]
    user_input = random.choice(twists)
    st.rerun()  # forces the text_area to update

if st.button("Continue Story →", type="primary", use_container_width=True):
    if user_input.strip():
        with st.spinner("Engaging Infinite Improbability Drive…"):
            st.session_state.messages.append({"role": "user", "content": user_input})

            stream = client.chat.completions.create(
                model=MODEL,
                messages=st.session_state.messages,
                temperature=0.92,
                max_tokens=1800,
                stream=True
            )

            response = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Full story
with st.expander("📜 Full Story So Far", expanded=True):
    story_parts = [m["content"] for m in st.session_state.messages if m["role"] != "system"]
    st.markdown("\n\n".join(story_parts))

if st.button("🗑️ Start New Story"):
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.rerun()

st.caption("Built with the real xAI API • Your towel is nearby. Probably.")
```

### Final Thoughts

In under 100 lines of code, we now have a writing partner that is:

- Funnier than most humans on their best day  
- Available 24/7  
- Never gets bored of your 47th subplot about malfunctioning tea synthesizers

So grab your towel, fire up the app, and remember: the universe is a deeply improbable place, but at least now you’ve got someone to laugh about it with.

Mostly harmless. 🛸
