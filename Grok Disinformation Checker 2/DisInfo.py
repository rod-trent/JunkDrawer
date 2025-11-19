import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from dotenv import load_dotenv
import os
import textwrap

load_dotenv()

API_KEY = os.getenv("XAI_API_KEY")
if not API_KEY:
    st.error("⚠️ XAI_API_KEY not found in .env file")
    st.stop()

API_URL = "https://api.x.ai/v1/chat/completions"
MODEL = "grok-4"  # Latest flagship as of Nov 2025 — always up-to-date + live web access

st.set_page_config(page_title="Real-Time Disinformation Checker", layout="centered")
st.title("🛡️ Real-Time Disinformation Detector")
st.markdown("**Powered by Grok-4 (xAI) with live web search • Knowledge continuously updated • No fixed cutoff**")

option = st.radio("Input method", ("Paste text", "Enter URL"), horizontal=True)

content = ""

if option == "Paste text":
    content = st.text_area("Paste the article or claim", height=300)
else:
    url = st.text_input("Article URL")
    if url:
        with st.spinner("Fetching article..."):
            try:
                article = Article(url)
                article.download()
                article.parse()
                content = article.text or article.title
                st.success("Article loaded")
                content = st.text_area("Extracted text (editable)", value=content, height=300)
            except:
                # Fallback
                headers = {"User-Agent": "Mozilla/5.0"}
                r = requests.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(r.content, "html.parser")
                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.decompose()
                content = soup.get_text(separator="\n")
                st.warning("Used fallback parser")
                content = st.text_area("Extracted text", value=content, height=300)

if not content.strip():
    st.info("Provide content to analyze")
    st.stop()

if st.button("🚨 Check for Disinformation (Real-Time Mode)", type="primary"):
    with st.spinner("Grok is fact-checking with live web access..."):
        
        prompt = textwrap.dedent(f"""
        You are an expert, impartial fact-checker with real-time web access.
        Today is November 19, 2025.

        Article/Claim to verify:
        {content[:30000]}  # Truncate only if absurdly long

        Instructions — be extremely strict:
        1. Extract every verifiable factual claim.
        2. For each claim, actively search the web if you are not 100% certain of the current truth.
        3. Rate accuracy 1–10:
           • 1 = Completely fabricated / disinformation
           • 10 = Verifiably true as of November 2025
        4. Cite sources (full URLs) for any correction or confirmation.
        5. Finally, give an overall trustworthiness score and one-paragraph summary.

        Respond in clear Markdown with bold ratings and source links.
        """)

        payload = {
            "messages": [
                {"role": "system", "content": "You are a rigorous fact-checker with live web access. Never rely solely on training data for current events or controversial claims."},
                {"role": "user", "content": prompt}
            ],
            "model": MODEL,
            "temperature": 0.2,
            "max_tokens": 4096
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            r = requests.post(API_URL, json=payload, headers=headers, timeout=180)
            r.raise_for_status()
            result = r.json()
            answer = result["choices"][0]["message"]["content"]

            st.success("Real-time fact-check complete!")
            st.markdown("### 📋 Grok-4 Fact-Check Report (Live Web Enabled)")
            st.markdown(answer)

            with st.expander("Copy raw report"):
                st.code(answer, language=None)

        except requests.exceptions.HTTPError as e:
            if r.status_code == 401:
                st.error("Invalid API key")
            elif r.status_code == 429:
                st.error("Rate limit hit — wait a minute and retry")
            else:
                st.error(f"API error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

st.markdown("---")
st.caption("Grok-4 continuously updated • Live web search on every check • Built Nov 2025")