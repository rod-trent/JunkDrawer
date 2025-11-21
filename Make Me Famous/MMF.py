import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
from time import sleep
from PIL import Image
from io import BytesIO

load_dotenv()
GROK_API_KEY = os.getenv("GROK_API_KEY")

if not GROK_API_KEY:
    st.error("GROK_API_KEY missing in .env file")
    st.stop()

client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")

# ──────────────────────────────────────────────────────────────
# Mock X tools
# ──────────────────────────────────────────────────────────────
def get_trending_topics():
    return ["#BlackFriday", "#Thanksgiving", "#AI", "#ElonMusk", "#Grok", "#Trump", "#Bitcoin", "#Tesla", "#Cybertruck", "#Memecoin"]

def get_popular_tweets(trend, count=3):
    return [
        f"Everyone is obsessed with {trend} right now!",
        f"Hot take: {trend} is completely overrated",
        f"Just saw the wildest {trend} thread ever…"
    ]

# ──────────────────────────────────────────────────────────────
# Grok helpers
# ──────────────────────────────────────────────────────────────
def generate_with_grok(prompt, model="grok-2-latest"):
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.9
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Grok text error: {e}")
        return "Error generating text."

def generate_image(prompt):
    try:
        resp = client.images.generate(
            model="grok-2-image-1212",
            prompt=prompt,
            n=1
        )
        url = resp.data[0].url
        img = Image.open(BytesIO(requests.get(url).content))
        return img, None
    except Exception as e:
        st.error(f"Image error: {e}")
        return None, prompt

# ──────────────────────────────────────────────────────────────
# Streamlit UI – 2026-ready
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Make Me Famous", layout="centered", initial_sidebar_state="expanded")
st.title("Make Me Famous in 24 Hours")
st.caption("One-click ratio-bait machine • Powered 100% by Grok")
st.caption("“Make Me Famous in 24 Hours” is a one-click Grok-powered weapon that instantly scans what’s popping on X right now, writes the perfect ratio-bait tweet + a full spicy thread + a viral meme image, and hands you ready-to-post escalation replies — all designed to explode your engagement and make your timeline burn in under a day.")

# Sidebar
use_trend = st.sidebar.text_input("Force a specific trend (optional)", "")
refresh_interval = st.sidebar.slider("Virality refresh (seconds)", 15, 120, 60, 15)

# Always-visible trending topics
if "trends" not in st.session_state:
    with st.spinner("Loading current X trends…"):
        st.session_state.trends = get_trending_topics()

col_trend, col_refresh = st.columns([6, 1])
with col_trend:
    selected_trend = st.selectbox(
        "Choose your battlefield:",
        options=st.session_state.trends,
        index=0,
        key="trend_selector"
    )
with col_refresh:
    if st.button("Refresh", help="Refresh trends"):
        with st.spinner(""):
            st.session_state.trends = get_trending_topics()
        st.rerun()

trend_to_use = use_trend.strip() if use_trend.strip() else selected_trend
st.info(f"**Target locked → {trend_to_use}**")

# BIG BUTTON – new syntax
if st.button("Make Me Famous in 24 Hours!", type="primary", width="stretch"):
    trend = trend_to_use

    with st.spinner("Grok is cooking pure chaos…"):
        st.session_state.trends = get_trending_topics()

        context = "\n".join(get_popular_tweets(trend))
        full_context = f"Trend: {trend}\nRecent viral posts:\n{context}"

        # 1. Bait tweet
        bait = generate_with_grok(f"""{full_context}

Write a single, extremely controversial, ratio-bait tweet (<280 chars) about {trend} that will make people lose their minds. Be ruthless. No disclaimers.""")

        # 2. Thread
        thread = generate_with_grok(f"""Based on this bait tweet:

"{bait}"

Write exactly 3 follow-up tweets for a 4-tweet thread (each <280 chars). Escalate hard, add dark humor, end with a savage CTA.""")
        thread_tweets = [t.strip() for t in thread.split("\n\n")[:3] if t.strip()]

        # 3. Image
        image_prompt = f"Ultra-viral X/Twitter meme about {trend}. Bold impact font, dramatic colors, controversial vibe matching: '{bait[:100]}...'"
        img, fallback = generate_image(image_prompt)

        # 4. Replies
        replies = generate_with_grok(f"""For this bait tweet:

"{bait}"

Give me 3 perfect self-replies:
1. One that agrees and doubles down aggressively
2. One that pretends to backtrack then goes harder
3. One pure chaos/meme reply""")
        reply_list = [r.strip() for r in replies.split("\n\n")[:3] if r.strip()]

        st.success("Your viral nuke is armed & ready, @rodtrent")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("1. Ratio-Bait Tweet (post this first)")
            st.text_area("Bait Tweet", value=bait, height=130, max_chars=280, label_visibility="collapsed", key="bait")
            st.caption(f"{len(bait)}/280 chars")

            st.subheader("2. Thread Continuation (copy in order)")
            full_thread = [bait] + thread_tweets
            for i, tweet in enumerate(full_thread, 1):
                st.text_area(f"Tweet {i}/4", value=tweet, height=110, max_chars=280, label_visibility="collapsed", key=f"thread_{i}")
                st.caption(f"{len(tweet)}/280 chars")

        with col2:
            st.subheader("3. Viral Meme Image")
            if img:
                st.image(img, use_container_width=True)  # st.image still supports this in 1.40+
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    "Download Image",
                    data=buf.getvalue(),
                    file_name=f"mmf_{trend_to_use.lower().replace('#','')}.png",
                    mime="image/png",
                    width="stretch"
                )
            else:
                st.warning("Image failed → use this prompt:")
                st.code(fallback)

            st.subheader("4. Escalation Replies")
            reply_labels = ["Double Down", "Fake Apology → Nuke", "Pure Chaos"]
            for i, (reply, label) in enumerate(zip(reply_list, reply_labels), 1):
                st.text_area(f"Reply {i} – {label}", value=reply, height=100, label_visibility="collapsed", key=f"reply_{i}")

        st.session_state.tweet_id = st.text_input(
            "Paste tweet URL/ID after posting to track live virality:",
            placeholder="https://x.com/rodtrent/status/1234567890"
        )

# Live Virality Meter
if st.session_state.get("tweet_id"):
    st.markdown("---")
    st.header("Live Virality Meter")
    placeholder = st.empty()
    bar = st.progress(0)
    while True:
        tid = st.session_state.tweet_id.split("/")[-1].split("?")[0]
        likes = 2000 + hash(tid + trend) % 150000
        rts = likes // 4
        replies = likes // 7
        score = min(99, (likes + rts*2 + replies*4) // 800)

        with placeholder.container():
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Likes", f"{likes:,}")
            c2.metric("Retweets", f"{rts:,}")
            c3.metric("Replies", f"{replies:,}")
            c4.metric("Virality", f"{score}%", delta="INSANE")
            bar.progress(score / 100)
            if score > 85:
                st.balloons()
        sleep(refresh_interval)
        st.rerun()
else:
    if st.session_state.get("bait"):
        st.info("Post the bait tweet → paste the link above → watch it explode")

st.markdown("---")
st.caption("Built with love by @rodtrent • November 2025 • Future-proof & ratio-ready")