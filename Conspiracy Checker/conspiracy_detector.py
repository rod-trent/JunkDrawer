import os
import requests
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load .env (for XAI_API_KEY)
load_dotenv()

# ==== CONFIG ====
XAI_API_KEY = os.getenv("XAI_API_KEY")
API_URL = "https://api.x.ai/v1/chat/completions"

GROK_MODELS = {
    "Grok 4 (smartest & most thorough)": "grok-4",
    "Grok 3 (fast & balanced)": "grok-3",
    "Grok 3 Mini (cheapest & fastest)": "grok-3-mini"
}

# ==== Helper to extract text from URL ====
def extract_text_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        # Remove scripts, styles, navigation etc.
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "advert"]):
            tag.decompose()
        text = soup.get_text(separator=' ')
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text[:20000]  # slightly larger for analysis
    except Exception as e:
        return f"[Error fetching article: {e}]"

# ==== Streamlit UI ====
st.set_page_config(page_title="🔍 Grok Disinformation & Conspiracy Detector", page_icon="🛡️", layout="centered")

st.title("🔍 Real-Time Conspiracy & Disinformation Detector")
st.caption("Powered 100% by Grok xAI API • Instantly spot red-string nonsense, fake news, and logical fallacies")

# Sidebar
with st.sidebar:
    st.header("Analysis Settings")
    
    api_key = st.text_input(
        "xAI API Key",
        value=XAI_API_KEY or "",
        type="password",
        help="Auto-loaded from .env • Get yours at https://x.ai/api"
    )
    if not api_key and XAI_API_KEY:
        st.success("✓ API key loaded from .env")

    model = st.selectbox("Grok Model", options=list(GROK_MODELS.keys()), index=0)
    model_id = GROK_MODELS[model]

    depth = st.select_slider(
        "Analysis Depth",
        options=["Quick Scan (headline-level)", "Thorough (fact-check style)", "Deep Forensic (scholarly rigor)"],
        value="Thorough (fact-check style)"
    )

    tone = st.select_slider(
        "Response Tone",
        options=["Neutral & Clinical", "Slightly Snarky", "Maximum British Sarcasm"],
        value="Slightly Snarky"
    )

# Main input
news_input = st.text_area(
    "Paste text, headline, or article URL to analyze:",
    height=140,
    placeholder="e.g. https://dodgy-news.example/5g-causes-autism\nor just paste: 'The moon landing was faked in a Hollywood basement'"
)

if st.button("🔎 Analyze for Conspiracy / Disinformation", type="primary"):
    if not api_key:
        st.error("No API key! Create a .env file with XAI_API_KEY=your_key")
        st.stop()
    if not news_input.strip():
        st.warning("Need some text or a URL to dissect!")
        st.stop()

    with st.spinner("Scanning for red flags…"):
        if news_input.strip().startswith("http"):
            with st.status("Fetching and cleaning article…"):
                article_text = extract_text_from_url(news_input)
                st.caption(f"Extracted ~{len(article_text.split())} words from the page.")
            input_for_grok = f"Full article text:\n\n{article_text}"
        else:
            input_for_grok = news_input

        depth_map = {
            "Quick Scan (headline-level)": "brief bullet-point summary of the biggest red flags only",
            "Thorough (fact-check style)": "detailed breakdown with specific claims flagged, reasoning, and suggested fact-check sources",
            "Deep Forensic (scholarly rigor)": "exhaustive academic-style rebuttal with historical context, logical fallacies named, and citations where possible"
        }

        tone_map = {
            "Neutral & Clinical": "completely neutral, professional fact-checker tone",
            "Slightly Snarky": "mild sarcasm and dry wit while remaining factual",
            "Maximum British Sarcasm": "absolutely savage, dripping sarcasm — think Private Eye meets QI"
        }

        system_prompt = f"""
You are an expert disinformation and conspiracy theory analyst powered by Grok.
Your job is to ruthlessly but fairly examine the provided text/article for:
• Classic conspiracy theory tropes and logical fallacies (name them explicitly)
• Known debunked claims or urban legends
• Cherry-picking, false dichotomies, appeal to authority, etc.
• Dog-whistles or coded extremist language
• Sources of the narrative (e.g. which forums or figures push this)
• Credible counter-evidence or mainstream consensus (with real sources when possible)

Structure your reply clearly with sections:
1. Overall Assessment (Safe / Dubious / Classic Conspiracy / Dangerous Disinformation)
2. Key Red Flags Found
3. Claim-by-Claim Breakdown (if applicable)
4. Recommended Fact-Check Sources
5. Confidence Level in your assessment

Tone: {tone_map[tone]}
Depth: {depth_map[depth]}

Never endorse the conspiracy. Stay 100% in analyst mode.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_for_grok}
        ]

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 0.7 if tone == "Neutral & Clinical" else 0.9,
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
                st.error("Invalid API key — check your .env")
            elif e.response.status_code == 429:
                st.error("Rate limited — wait a minute or upgrade plan")
            else:
                st.error(f"API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

st.caption("Built with 🛡️ by a concerned citizen • Keeping the internet slightly less insane since 2025")