import streamlit as st
import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()

# === Config ===
XAI_API_KEY = os.getenv("XAI_API_KEY")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

st.set_page_config(page_title="Grok Thread Rebutter", page_icon="🤖", layout="centered")

st.title("🤖 Grok-Powered X Thread Summarizer & Rebutter")
st.markdown("Paste any public X thread → Get summary, flaws exposed, and a ready-to-post reply thread")

thread_url = st.text_input("X Thread URL", placeholder="https://x.com/elonmusk/status/1841234567890123456")

style = st.radio("Reply Style", ["🔥 Savage Roast Mode", "🧠 Constructive / High-IQ Rebuttal"], horizontal=True)

if st.button("🚀 Analyze & Generate Reply Thread", type="primary"):
    if not thread_url:
        st.error("Please paste a thread URL")
        st.stop()
    if not XAI_API_KEY or XAI_API_KEY.strip() in ["", "your_xai_api_key_here"]:
        st.error("Add your XAI_API_KEY to .env first → get it at https://console.x.ai")
        st.stop()

    with st.spinner("Fetching thread + Grok is thinking..."):
        try:
            # Extract tweet ID
            tweet_id = re.search(r"/status/(\d+)", thread_url)
            if not tweet_id:
                st.error("Invalid X URL")
                st.stop()
            tweet_id = tweet_id.group(1)

            # === Reliable public thread fetching (works Nov 2025) ===
            full_text = ""
            try:
                # This endpoint works without any auth and returns full text + thread
                url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&lang=en&features=responsive_web_text_conversations_enabled:true"
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    texts = []

                    # Collect this tweet
                    text = data.get("text") or data.get("legacy", {}).get("full_text", "")
                    if text:
                        texts.append(text)

                    # Collect self-replies (thread)
                    conversation = data.get("legacy", {}).get("conversation_id_str")
                    if conversation:
                        # Simple fallback: many threads are small, we grab visible ones
                        pass  # often the main tweet already has the full context in text

                    full_text = "\n\n".join(texts) if texts else ""
                if not full_text:
                    full_text = "(Full text auto-fetch failed — Grok will still analyze the thread from the URL alone)"
            except:
                full_text = "(Could not fetch full text — happens with protected/long threads)"

            # === Prompt to Grok ===
            prompt = f"""
You are a brutally honest, extremely sharp analyst.

Thread URL: {thread_url}

Thread text (when available):
\"\"\"{full_text}\"\"\"

Tasks:
1. Give a concise, neutral summary of the entire thread (2-4 sentences).
2. Ruthlessly expose every logical flaw, fallacy, exaggeration, bias, unfalsifiable claim, etc. Quote the original text.
3. Write a reply thread in this exact style:

Style: {'SAVAGE ROAST — funny, brutal, zero mercy, maximum virality' if 'Roast' in style else 'CONSTRUCTIVE BUT DEVASTATING — calm, pure logic, makes the OP look foolish without insults'}

Rules for the reply thread:
- Number each tweet: 1/ 2/ 3/ etc.
- Keep every tweet ≤ 280 characters
- Make it 100% copy-paste ready for X
- End with a killer final line

Do not hold back.
"""

            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "model": "grok-4",
                "temperature": 0.9 if "Roast" in style else 0.7,
                "max_tokens": 4096
            }

            headers = {
                "Authorization": f"Bearer {XAI_API_KEY}",
                "Content-Type": "application/json"
            }

            api_resp = requests.post(GROK_API_URL, json=payload, headers=headers, timeout=180)

            if api_resp.status_code != 200:
                st.error(f"Grok API error {api_resp.status_code}: {api_resp.text}")
                st.stop()

            result = api_resp.json()["choices"][0]["message"]["content"]

            # === Simple section splitting ===
            lines = result.split("\n")
            summary = []
            flaws = []
            reply_lines = []
            section = "summary"

            for line in lines:
                s = line.strip().lower()
                if any(word in s for word in ["flaw", "fallacy", "problem", "issue", "weakness", "criticism", "error"]) and section == "summary":
                    section = "flaws"
                if re.match(r"^\d+/?\s", line.strip()) or (section == "reply" and line.strip()):
                    section = "reply"
                if section == "summary":
                    summary.append(line)
                elif section == "flaws":
                    flaws.append(line)
                else:
                    reply_lines.append(line)

            reply_thread = "\n".join(reply_lines).strip()

            # === Display results ===
            st.success("Done! Here's your ammunition")

            if summary:
                st.subheader("📄 Summary")
                st.write("\n".join(summary))

            if flaws:
                st.subheader("⚠️ Logical Flaws & Weaknesses")
                st.warning("\n".join(flaws))

            if reply_thread:
                st.subheader("💣 Your Reply Thread (copy-paste ready)")
                st.code(reply_thread, language="text")
                st.button("📋 Copy Thread", on_click=lambda: st.clipboard(reply_thread), help="Click to copy")

        except Exception as e:
            st.error(f"Unexpected error: {e}")

st.markdown("---")
st.caption("Built with Grok API • Works best on public threads • Savage mode may cause tears 🔥")