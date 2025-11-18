# app.py
import streamlit as st
import os
from dotenv import load_dotenv
import requests
import PyPDF2

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    st.error("⚠️ GROK_API_KEY not found in .env file")
    st.stop()

# Updated endpoint and model (November 2025)
API_URL = "https://api.x.ai/v1/chat/completions"
MODEL = "grok-3"  # ← THIS IS THE CURRENT MODEL (use "grok-3-mini" if you want cheaper/faster)

st.set_page_config(page_title="Brutally Honest Career Advisor", page_icon="🪓", layout="centered")
st.title("🪓 Brutally Honest Career Advisor")
st.markdown("Upload your résumé or LinkedIn PDF → I roast it and give you a real plan. Zero fluff.")

uploaded_file = st.file_uploader("Upload résumé or LinkedIn profile (PDF)", type="pdf")

if uploaded_file is not None:
    # Extract text
    with st.spinner("Reading PDF..."):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if len(text.strip()) < 50:
                st.error("PDF appears to be scanned/image-only. Please upload a selectable-text PDF.")
                st.stop()
        except Exception as e:
            st.error(f"PDF error: {e}")
            st.stop()

    st.success("PDF loaded!")
    st.expander("Preview (first 3000 chars)").write(text[:3000] + ("..." if len(text) > 3000 else ""))

    col1, col2 = st.columns(2)
    with col1:
        target_role = st.text_input("Target role (e.g. Senior Product Manager, Staff ML Engineer)")
    with col2:
        years_exp = st.text_input("Years of experience")

    extra = st.text_area("Anything else? (current TC, location, remote only, dream companies, etc.)", height=100)

    if st.button("🔥 Roast My Career", type="primary"):
        with st.spinner("Grok is judging you harshly..."):
            prompt = f"""
You are the most brutally honest senior executive recruiter on earth. No politeness filters.

Résumé/LinkedIn:
{text}

Years of experience: {years_exp or "unknown"}
Target role: {target_role or "not told"}
Extra context: {extra or "none"}

Respond with exactly these markdown sections:

## What’s Actually Impressive
## What Sucks (and Why It’s a Problem)
## Gaps & Blind Spots
## Realistic Next Moves (2–4 options with timeline + pros/cons)
## Salary & Negotiation Scripts
   - Realistic current market range for this profile
   - What you should actually ask for next
   - Exact scripts for salary expectations question + countering offers + equity/sign-on asks

Tone: Gordon Ramsay in a kitchen rush. Swearing allowed if it fits.
""".strip()

            headers = {
                "Authorization": f"Bearer {GROK_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": MODEL,                    # ← now correctly set to grok-3
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 4096
            }

            try:
                r = requests.post(API_URL, headers=headers, json=payload, timeout=120)
                r.raise_for_status()
                advice = r.json()["choices"][0]["message"]["content"]
                
                st.markdown(advice)
                st.code(advice, language=None)  # easy copy

            except requests.exceptions.HTTPError as e:
                error_body = r.text
                if "model_not_found" in error_body or "404" in error_body:
                    st.error("Model error – make sure you’re using **grok-3** or **grok-3-mini** (grok-beta is dead).")
                elif "insufficient_quota" in error_body:
                    st.error("API quota exceeded → top up at https://x.ai/api")
                else:
                    st.error(f"API error {r.status_code}: {error_body}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

else:
    st.info("↑ Upload your LinkedIn PDF (More → Save to PDF) or normal résumé PDF")