import streamlit as st
import requests
from PIL import Image
import cv2
import tempfile
import os
import base64
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Meme Builder", layout="centered", page_icon="🧠")

st.title("🧠 Meme Builder")
st.caption("Multimodal Meme Captioner • Powered by Grok-4 Vision")

GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    st.error("GROK_API_KEY not found in .env file")
    st.info("Create `.env` with:\n`GROK_API_KEY=sk-your-key-here`")
    st.stop()

API_URL = "https://api.x.ai/v1/chat/completions"

uploaded_file = st.file_uploader("Upload photo or video", type=["png","jpg","jpeg","webp","gif","mp4","mov","webm","avi"])

def image_to_base64(img: Image.Image) -> str:
    import io
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def extract_key_frame(video_bytes: bytes) -> Image.Image:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
        f.write(video_bytes)
        path = f.name
    cap = cv2.VideoCapture(path)
    ret, frame = cap.read()
    cap.release()
    os.unlink(path)
    if not ret:
        st.error("Couldn't extract frame from video")
        st.stop()
    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

if uploaded_file:
    # Force brand-new captions every time
    st.session_state.clear()  # simple, brutal, works perfectly

    if uploaded_file.type.startswith("video/"):
        with st.spinner("Extracting best frame..."):
            img = extract_key_frame(uploaded_file.read())
    else:
        img = Image.open(uploaded_file)

    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.image(img, width="stretch", caption="Your meme material")

    with col2:
        st.write("### 10 Fresh Viral Captions")

        with st.spinner("Grok is cooking brand-new chaos... 🔥"):
            b64 = image_to_base64(img)
            prompt = "Generate exactly 10 ultra-viral meme captions using only • bullets. No extra text."
            payload = {
                "model": "grok-4",
                "messages": [{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                ]}],
                "temperature": 0.95,
                "max_tokens": 800
            }
            r = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROK_API_KEY}"}, timeout=90)
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"]
            captions = [line.strip()[2:] for line in raw.split("\n") if line.strip().startswith("• ")]

        for i, caption in enumerate(captions, 1):
            st.markdown(f"**{i}.** {caption}")

else:
    st.info("↑ Upload any image or video → get 10 brand-new viral captions every time")
    st.balloons()

st.markdown("---")
st.caption("Meme Creator • Always fresh captions • Zero headaches • Enjoy!")