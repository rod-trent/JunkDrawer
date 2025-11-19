import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from dotenv import load_dotenv
import os
import textwrap

load_dotenv()

# === Config ===
API_KEY = os.getenv("XAI_API_KEY")
if not API_KEY:
    st.error("⚠️ XAI_API_KEY not found in .env file")
    st.stop()

API_URL = "https://api.x.ai/v1/chat/completions"
MODEL = "grok-4"  # or "grok-3" if you prefer

# === Page config ===
st.set_page_config(page_title="Disinformation Checker (powered by Grok)", layout="centered")
st.title("📰 Disinformation & Fact-Check Detector")
st.markdown("Powered by **Grok-4** from xAI")

# === Input method ===
option = st.radio("How do you want to provide content?", ("Paste text", "Enter URL"), horizontal=True)

content = ""

if option == "Paste text":
    content = st.text_area("Paste the article/text here", height=300)
else:
    url = st.text_input("Enter article URL")
    if url:
        with st.spinner("Fetching and parsing article..."):
            try:
                article = Article(url)
                article.download()
                article.parse()
                content = article.text
                st.success("Article loaded successfully!")
                st.text_area("Extracted text (you can edit if needed)", value=content, height=300)
                content = st.text_area("Extracted text", value=content, height=300, key="url_content")
            except Exception as e:
                st.error(f"Could not fetch article: {e}")
                # Fallback to requests + bs4
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    resp = requests.get(url, headers=headers, timeout=15)
                    soup = BeautifulSoup(resp.content, "html.parser")
                    # Remove scripts/styles
                    for script in soup(["script", "style", "nav", "footer", "aside"]):
                        script.decompose()
                    content = soup.get_text(separator="\n")
                    st.warning("Fallback parsing used (less clean)")
                    content = st.text_area("Extracted text", value=content, height=300, key="fallback")
                except Exception as e2:
                    st.error(f"Failed to load URL: {e2}")

if not content.strip():
    st.info("Please provide content to analyze.")
    st.stop()

# === Analyze button ===
if st.button("🔍 Check for Disinformation", type="primary"):
    with st.spinner("Sending to Grok for analysis..."):
        
        prompt = textwrap.dedent(f"""
        You are an expert fact-checker. Analyze the following article/text for disinformation, misleading claims, or factual inaccuracies.

        Article:
        {content}

        Instructions:
        1. Identify every specific factual claim that could be verified.
        2. For each claim, rate its accuracy on a scale of 1–10 where:
           - 1 = Completely false / pure disinformation
           - 10 = Completely true and well-sourced
        3. Provide a short explanation and, when possible, the correct fact or source of truth.
        4. At the end, give an overall trustworthiness score (1–10) for the entire piece and a one-paragraph summary.

        Respond in clear Markdown with headings, bullet points, and bold ratings.
        """)

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [
                {"role": "system", "content": "You are a rigorous, impartial fact-checker."},
                {"role": "user", "content": prompt}
            ],
            "model": MODEL,
            "temperature": 0.3,
            "max_tokens": 4096
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            result = response.json()
            grok_response = result["choices"][0]["message"]["content"]
            
            st.success("Analysis complete!")
            st.markdown("### 📊 Grok Fact-Check Report")
            st.markdown(grok_response)
            
            # Optional: copy button
            st.code(grok_response, language=None)
            
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                st.error("Invalid API key. Check your XAI_API_KEY in .env")
            elif response.status_code == 429:
                st.error("Rate limit exceeded. Try again later.")
            else:
                st.error(f"API error {response.status_code}: {http_err}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

# === Footer ===
st.markdown("---")
st.caption("Built with ❤️ using Streamlit + xAI Grok API | Not affiliated with any fact-checking organization")