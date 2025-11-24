import streamlit as st
from dotenv import load_dotenv
import os
import httpx
import re
from utils.social_scraper import get_instagram_posts

load_dotenv()
GROK_API_KEY = os.getenv("GROK_API_KEY")

st.set_page_config(page_title="Gift Genius", page_icon="gift", layout="centered")
st.title("Gift Genius")
st.caption("Public X or Instagram username → Perfect gift ideas powered by Grok")

platform = st.radio("Platform", ["X (Twitter)", "Instagram"], horizontal=True)
username = st.text_input(f"Enter public @{platform} username (no @)", placeholder="elonmusk or natgeo")

def fetch_x_posts_via_grok(username: str, limit: int = 20) -> list[str]:
    if not GROK_API_KEY:
        return ["Grok API key missing."]

    prompt = f"""Use x_user_search to confirm @{username} exists.
Then use x_keyword_search with query='from:{username}' limit={limit} mode='Latest'.
Return ONLY a Python list of the post texts (no metadata). Example: ['text1', 'text2']
If user not found → respond exactly: USER_NOT_FOUND"""

    try:
        resp = httpx.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"},
            json={"model": "grok-3", "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.1, "max_tokens": 2000},
            timeout=60
        )
        resp.raise_for_status()
        result = resp.json()["choices"][0]["message"]["content"].strip()

        if "USER_NOT_FOUND" in result.upper():
            return ["X user not found or private."]

        # Try eval first
        try:
            posts = eval(result)
            if isinstance(posts, list):
                return [p.strip() for p in posts if p.strip()]
        except:
            pass

        # Fallback regex
        matches = re.findall(r"['\"](.+?)['\"]", result)
        return matches[:limit] if matches else ["No posts parsed."]

    except Exception as e:
        return [f"Grok error: {str(e)}"]

if st.button("Analyze & Recommend Gifts", type="primary"):
    if not username.strip():
        st.error("Enter a username.")
    elif not GROK_API_KEY:
        st.error("Add GROK_API_KEY to .env")
    else:
        with st.spinner(f"Fetching @{username} on {platform}..."):
            posts = (fetch_x_posts_via_grok(username)
                     if platform == "X (Twitter)"
                     else get_instagram_posts(username))

        if not posts or any("error" in str(p).lower() or "not found" in str(p).lower() for p in posts):
            st.error(posts[0] if posts else "No data")
            st.info("Try public profiles (examples): @elonmusk (X) or @natgeo (Instagram)")
        else:
            st.success(f"Found {len(posts)} posts!")
            with st.expander("Sample posts"):
                for i, p in enumerate(posts[:8], 1):
                    st.write(f"**{i}.** {p[:280]}{'...' if len(p)>280 else ''}")

            posts_text = "\n\n".join(posts[:25])

            prompt = f"""You are a world-class gift curator.
Analyze these posts from @{username} on {platform} and recommend 5 thoughtful, specific gifts they’d love.

For each:
- Gift name
- Price range
- Why it fits (reference posts)
- Where to buy

Posts:
{'─'*60}
{posts_text}
{'─'*60}

Markdown + emojis. Warm & creative."""

            with st.spinner("Grok is thinking..."):
                resp = httpx.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROK_API_KEY}"},
                    json={"model": "grok-3", "messages": [{"role": "user", "content": prompt}],
                          "temperature": 0.85, "max_tokens": 1400},
                    timeout=90
                )
                resp.raise_for_status()
                reply = resp.json()["choices"][0]["message"]["content"]

                st.success("Perfect gifts found!")
                st.markdown(reply)
                st.download_button("Download List", reply, f"gifts_@{username}.md", "text/markdown")


st.caption("Reliable in 2025: X via Grok • Instagram via Instaloader")
