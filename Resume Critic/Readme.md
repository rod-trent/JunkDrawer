# I Built a “Brutally Honest Career Advisor” App That Roasts Your Résumé With Grok-3 (And It Will Hurt Your Feelings)

In 2025, the job market is more savage than ever. Recruiters spend 7.4 seconds on your résumé. AI screeners reject 75% of applicants before a human even blinks. Everyone is “passionate,” “results-oriented,” and apparently saved their last company 4000% in costs.

Enough.

I got tired of the LinkedIn echo chamber of endless positivity and built something that actually tells you the truth.

Meet **Brutally Honest Career Advisor** — a dead-simple Streamlit app that lets you upload your résumé (or LinkedIn PDF), hit a button, and get absolutely eviscerated by Grok-3 in the style of Gordon Ramsay judging risotto.

No “great start!”  
No “everyone’s journey is valid.”  
Just cold, surgical, useful truth.

### What it actually does
1. You upload a PDF (LinkedIn “Save to PDF” works perfectly).
2. It extracts the text.
3. Sends everything to Grok-3 with the prompt: “Be the most brutally honest recruiter alive.”
4. You get back a structured roast with:
   - What’s Actually Impressive (usually 2–3 bullets, if you’re lucky)
   - What Sucks (and Why It’s a Problem)
   - Gaps & Blind Spots
   - Realistic Next Moves (with timelines)
   - Exact salary negotiation scripts

I’ve tested it on senior directors, fresh grads, and serial job-hoppers. The results are consistently hilarious and horrifying.

Example real output snippet (anonymized):

> ## What Sucks (and Why It’s a Problem)
> - “Led cross-functional teams” — you say this six times but never once mention team size, budget, or actual outcome. This is corporate word salad.
> - Your last role is listed as “Senior Manager” for 4 years with zero promotion. That screams plateaued.
> - Bullet points longer than tweets. Nobody reads walls of text in 2025.

It will also give you the exact script to counter a low-ball offer and how to ask for 30% more without sounding delusional.

### Why this exists
Because the current career-advice ecosystem is broken:
- Most coaches are incentivized to keep you hopeful (and paying).
- Reddit is 50% cope, 50% humblebrag.
- Your friends lie to be nice.

Sometimes you just need an AI that doesn’t care about your feelings to tell you that listing “Microsoft Office” in 2025 makes you look like a time traveler from 1998.

### The tech is stupidly simple
- Streamlit (because who has time for React in 2025)
- PyPDF2 for text extraction
- xAI’s Grok-3 API (the real star)
- One .env file with your key

Full code is 150 lines. You can have it running locally in under two minutes.

Here’s the whole thing (copy-paste ready):

```python
# app.py — Brutally Honest Career Advisor (2025 edition)
import streamlit as st
import os
from dotenv import load_dotenv
import requests
import PyPDF2

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    st.error("Missing GROK_API_KEY in .env")
    st.stop()

API_URL = "https://api.x.ai/v1/chat/completions"
MODEL = "grok-3"  # or "grok-3-mini" for cheaper

st.set_page_config(page_title="Brutally Honest Career Advisor", page_icon="🪓")
st.title("🪓 Brutally Honest Career Advisor")
st.markdown("Upload your résumé. Prepare your ego for demolition.")

uploaded_file = st.file_uploader("Résumé or LinkedIn PDF", type="pdf")

if uploaded_file:
    # Extract text
    text = ""
    for page in PyPDF2.PdfReader(uploaded_file).pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    col1, col2 = st.columns(2)
    with col1:
        target = st.text_input("Target role")
    with col2:
        years = st.text_input("Years experience")

    extra = st.text_area("Anything else? (current TC, location, etc.)")

    if st.button("🔥 Roast Me", type="primary"):
        with st.spinner("Grok is sharpening the knife..."):
            prompt = f"""
You are the most brutally honest executive recruiter alive. Zero filter.

Résumé:\n{text}\n
Years exp: {years}\nTarget role: {target}\nExtra: {extra}

Structure your response exactly like this:

## What’s Actually Impressive
## What Sucks (and Why It’s a Problem)
## Gaps & Blind Spots
## Realistic Next Moves
## Salary & Negotiation Scripts

Tone: Gordon Ramsay meets a venture capitalist who’s late for his flight.
            """.strip()

            payload = {
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 4096
            }

            r = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROK_API_KEY}"})
            r.raise_for_status()
            advice = r.json()["choices"][0]["message"]["content"]
            st.markdown(advice)
            st.code(advice, language=None)
```

Run it with:
```bash
pip install streamlit python-dotenv PyPDF2 requests
streamlit run app.py
```

Get your API key at https://x.ai/api

### Final warning
This app has made grown adults close their laptops and stare into the void.

It has also helped people negotiate +$80k, fix terrible résumés, and finally admit they’ve been “Head of Operations” at a 6-person startup for five years.

Use it. Cry a little. Then go fix your career.

You’re welcome.  
(And yes, I ran my own résumé through it first. It hurt. A lot.)

🔗 GitHub repo coming soon — star this post if you want me to open-source the polished version with dark mode and one-click LinkedIn export.
