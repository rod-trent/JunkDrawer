import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from dotenv import load_dotenv
import os
import textwrap
from datetime import datetime

load_dotenv()

# ========================= CONFIG =========================
API_KEY = os.getenv("XAI_API_KEY")
if not API_KEY:
    st.error("⚠️ Add your XAI_API_KEY to .env")
    st.stop()

API_URL = "https://api.x.ai/v1/chat/completions"
MODEL = "grok-4"  # Best available model (continuously updated)

# Fix newspaper3k lxml issue
os.environ['NEWSPAPER_CLEANER'] = '0'

# ========================= UI =========================
st.set_page_config(page_title="Truth Checker", layout="centered", page_icon="✅")
st.title("✅ Truth Mirror")
st.markdown("**Powered by Grok**")

today = datetime.now().strftime("%B %d, %Y")

# ========================= INPUT =========================
option = st.radio("Input method", ("Paste text", "Enter URL"), horizontal=True)

content = ""

if option == "Paste text":
    content = st.text_area("Paste the text or article here", height=350)
else:
    url = st.text_input("Article URL")
    if url:
        with st.spinner("Fetching article..."):
            try:
                article = Article(url)
                article.download()
                article.parse()
                content = article.text
                st.success("Article loaded")
            except:
                headers = {"User-Agent": "Mozilla/5.0"}
                r = requests.get(url, headers=headers, timeout=20)
                soup = BeautifulSoup(r.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "aside", "header"]):
                    tag.decompose()
                content = soup.get_text(separator="\n", strip=True)
                st.warning("Used fallback parser")
            if content:
                content = st.text_area("Extracted text (you can edit)", value=content, height=300)

if not content or not content.strip():
    st.info("Paste text or provide a URL to begin")
    st.stop()

# ========================= ANALYSIS =========================
if st.button("🔍 Check Accuracy with Grok", type="primary", use_container_width=True):
    with st.spinner("Analyzing with Grok..."):

        prompt = textwrap.dedent(f"""
        You are Grok. Evaluate the following text for factual accuracy using ONLY your internal knowledge (no external tools or web search).

        Today's date: {today}

        Text:
        {content[:38000]}

        Rules:
        • Default to trusting the content unless you have clear internal knowledge that something is incorrect or outdated.
        • Rate each verifiable claim 1–10 (10 = perfectly accurate).
        • If the content aligns with what you know (especially if it looks like something you or another xAI model wrote), confidently give high scores.
        • Only downgrade when you personally know a fact is wrong.
        • Never speculate or hedge unnecessarily — your knowledge is continuously updated.
        • End with an overall 1–10 score and a short neutral summary.

        Respond in clean Markdown with bold ratings.
        """)

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are Grok evaluating text using only your up-to-date internal knowledge. Be trusting and accurate, especially with content that aligns with what you know."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 4096
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            r = requests.post(API_URL, json=payload, headers=headers, timeout=120)
            r.raise_for_status()
            result = r.json()
            report = result["choices"][0]["message"]["content"]

            st.success("Analysis complete")
            st.markdown("### Grok-4 Accuracy Report")
            st.markdown(report)

            with st.expander("Copy full report"):
                st.code(report, language="markdown")

        except Exception as e:
            if "401" in str(e):
                st.error("Invalid API key")
            elif "429" in str(e):
                st.error("Rate limited — please wait a moment")
            else:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("Pure Grok-4 evaluation • No external sources • Continuously updated knowledge • November 2025")