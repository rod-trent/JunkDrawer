import streamlit as st
import os
import requests
from github import Github
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

st.set_page_config(page_title="What Should I Build Next? Oracle", page_icon="🔮", layout="centered")

st.title("🔮 What Should I Build Next? Oracle")
st.markdown("*Grok reads your GitHub soul and tells you exactly what to build next*")

# Auto-load from .env
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")

with st.sidebar:
    st.header("Configuration")
    github_token = st.text_input("GitHub Token", value=GITHUB_TOKEN or "", type="password",
                                 help="Loaded from .env (GITHUB_TOKEN)")
    grok_api_key = st.text_input("Grok API Key", value=GROK_API_KEY or "", type="password",
                                 help="Loaded from .env (GROK_API_KEY)")

    if st.button("🔥 Connect & Consult the Oracle", type="primary"):
        if not github_token or not grok_api_key:
            st.error("Need both tokens!")
        else:
            st.session_state.github_token = github_token
            st.session_state.grok_api_key = grok_api_key
            st.session_state.ready = True
            st.success("Connected!")

if "ready" not in st.session_state:
    st.info("Tokens auto-loaded from `.env` → just click the button!")
    st.stop()

# GitHub connection & analysis (unchanged)
try:
    g = Github(st.session_state.github_token)
    user = g.get_user()
    repos = list(user.get_repos())[:50]
except Exception as e:
    st.error(f"GitHub error: {e}")
    st.stop()

st.success(f"Analyzing **{user.login}** – {len(repos)} repos found")

# === Same analysis code (languages, topics, etc.) ===
languages = {}
topics = set()
stars_total = 0
recent_repos = []

for repo in repos:
    if repo.language:
        languages[repo.language] = languages.get(repo.language, 0) + 1
    if repo.stargazers_count:
        stars_total += repo.stargazers_count
    if repo.topics:
        topics.update(repo.topics)
    if repo.updated_at and (datetime.now() - repo.updated_at.replace(tzinfo=None)).days < 730:
        recent_repos.append({
            "name": repo.name,
            "description": repo.description or "",
            "language": repo.language or "Unknown",
            "stars": repo.stargazers_count,
            "url": repo.html_url
        })

top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:8]
top_languages_str = ", ".join([f"{lang} ({count})" for lang, count in top_languages])
topics_str = ", ".join(list(topics)[:20]) if topics else "none detected"

col1, col2, col3 = st.columns(3)
with col1: st.metric("Repos", len(repos))
with col2: st.metric("Total Stars", stars_total)
with col3: st.metric("Top Languages", len(top_languages))
st.caption(f"Top languages: {top_languages_str}")
if topics_str != "none detected":
    st.caption(f"Topics: {topics_str}")

# === PROMPT (unchanged) ===
system_prompt = """
You are an elite startup mentor and senior engineer combined. 
Suggest exactly 5 project ideas that push the developer slightly outside their comfort zone, 
leverage their strongest skills in new ways, have real monetization potential in 2025–2026, 
and are genuinely exciting/underserved.

Format for each idea:
# Idea {n}: <Catchy Title>
**One-sentence pitch:** 
**Why it levels you up:** 
**Tech stack suggestion:** (use existing skills + 1–2 new tools)
**Monetization path:** 
**Validation idea:** (first 10 users)
"""

user_prompt = f"""
GitHub: {user.login}
Top languages: {top_languages_str}
Topics: {topics_str}
Total stars: {stars_total}
Recent projects (last ~2 years):
{json.dumps([f"{r['name']} – {r['description'] or 'no desc'}" for r in recent_repos[:15]], indent=2)}

Give me 5 hyper-specific, monetizable, portfolio-exploding project ideas.
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

# === FIXED: Use the current model (November 2025+) ===
GROK_MODEL = "grok-3"          # ← this is the important fix
# Fallback list in case xAI releases grok-4 soon
# GROK_MODEL = "grok-4" if you have access, otherwise grok-3 is free-tier friendly

with st.spinner("Grok is manifesting your future..."):
    headers = {
        "Authorization": f"Bearer {st.session_state.grok_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROK_MODEL,
        "messages": messages,
        "temperature": 0.88,
        "max_tokens": 2800
    }

    try:
        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]

        st.success("✨ The Oracle has spoken!")
        st.markdown("## 🔥 Your 5 Next Big Projects")
        st.markdown(result)
        st.session_state.last_reading = result

    except requests.exceptions.HTTPError as err:
        error_body = response.text
        if "not found" in error_body.lower() or "deprecated" in error_body.lower():
            st.error(f"Model issue → please use **grok-3** (or grok-4 if you have access). Current error:\n{error_body}")
        else:
            st.error(f"API error {response.status_code}: {error_body}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

if "last_reading" in st.session_state:
    with st.expander("Previous reading"):
        st.markdown(st.session_state.last_reading)

st.caption("Built with Streamlit + Grok xAI API • Nov 2025 edition")