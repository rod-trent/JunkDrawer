import streamlit as st
import os
import requests
from github import Github, Auth
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

st.set_page_config(page_title="What Should I Build Next? Oracle", page_icon="🔮", layout="centered")

st.title("🔮 What Should I Build Next? Oracle")
st.markdown("*Grok reads your GitHub soul and reveals your next big thing*")

# Load from .env
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")

with st.sidebar:
    st.header("Config")
    github_token = st.text_input("GitHub Token", value=GITHUB_TOKEN or "", type="password",
                                 help="From .env → GITHUB_TOKEN")
    grok_api_key = st.text_input("Grok API Key", value=GROK_API_KEY or "", type="password",
                                 help="From .env → GROK_API_KEY")

    if st.button("🔥 Consult the Oracle", type="primary"):
        if not github_token.strip() or not grok_api_key.strip():
            st.error("Both tokens required!")
        else:
            st.session_state.github_token = github_token.strip()
            st.session_state.grok_api_key = grok_api_key.strip()
            st.session_state.ready = True
            st.success("Ready!")

if "ready" not in st.session_state:
    st.info("Tokens auto-loaded from `.env` → just click the button!")
    st.stop()

# === FIXED: Modern PyGithub authentication (no more deprecation warning) ===
try:
    auth = Auth.Token(st.session_state.github_token)
    g = Github(auth=auth)        # ← this is the new 2025+ way
    user = g.get_user()
    repos = list(user.get_repos())[:60]  # slightly more for better analysis
except Exception as e:
    st.error(f"GitHub connection failed: {e}")
    st.stop()

st.success(f"Connected as **{user.login}** — scanning {len(repos)} repos")

# === Profile analysis (unchanged) ===
languages = {}
topics = set()
stars_total = 0
recent_repos = []

for repo in repos:
    if repo.language:
        languages[repo.language] = languages.get(repo.language, 0) + 1
    stars_total += repo.stargazers_count or 0
    if repo.topics:
        topics.update(repo.topics)
    if repo.updated_at and (datetime.now() - repo.updated_at.replace(tzinfo=None)).days < 730:
        recent_repos.append({
            "name": repo.name,
            "desc": repo.description or "no description",
            "lang": repo.language or "Unknown",
            "stars": repo.stargazers_count,
            "url": repo.html_url
        })

top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:8]
top_languages_str = ", ".join([f"{lang} ({count})" for lang, count in top_languages])
topics_str = ", ".join(list(topics)[:25]) if topics else "none"

col1, col2, col3 = st.columns(3)
with col1: st.metric("Repos Scanned", len(repos))
with col2: st.metric("Total Stars", stars_total)
with col3: st.metric("Main Languages", len(top_languages))

st.caption(f"Top languages: {top_languages_str}")
if topics_str != "none":
    st.caption(f"Topics: {topics_str}")

# === Prompt (still elite-tier) ===
system_prompt = """
You are a world-class engineering mentor + startup founder.
Given this developer's real GitHub history, suggest exactly 5 ambitious but achievable solo projects that:
• Push them just outside their comfort zone
• Combine their strongest skills in novel ways
• Have clear 2025–2026 monetization potential
• Are genuinely underserved or perfectly timed

Format each idea exactly like this:
# Idea {n}: <Catchy Title>
**Pitch:** (one killer sentence)
**Why it levels you up:**
**Tech stack:** (your skills + 1–2 new tools)
**Money path:**
**First 10 users:**
"""

user_prompt = f"""
Username: {user.login}
Top languages: {top_languages_str}
Topics: {topics_str}
Total stars: {stars_total}
Recent projects:
{json.dumps([f"{r['name']} – {r['desc']}" for r in recent_repos[:15]], indent=2)}

Give me 5 hyper-specific, money-making, portfolio-destroying project ideas for 2025–2026.
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

with st.spinner("Grok is forging your destiny..."):
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {st.session_state.grok_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "grok-3",           # current as of Nov 2025
                "messages": messages,
                "temperature": 0.9,
                "max_tokens": 3000
            },
            timeout=90
        )
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]

        st.success("✨ The Oracle has spoken!")
        st.markdown("## 🔥 Your 5 Destiny Projects")
        st.markdown(result)
        st.session_state.last_reading = result

    except requests.exceptions.HTTPError as e:
        st.error(f"Grok API error: {response.status_code}\n{response.text}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

if "last_reading" in st.session_state:
    with st.expander("Show previous reading"):
        st.markdown(st.session_state.last_reading)

st.caption("No more warnings • Built for PyGithub 2.0+ • Nov 2025")
