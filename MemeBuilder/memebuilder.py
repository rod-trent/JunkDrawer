import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import cv2
import tempfile
import os
import base64
from dotenv import load_dotenv
import textwrap
import io

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

def add_meme_caption(img: Image.Image, caption: str, font_size: int = 60):
    # Adjustable Impact-style meme text — only at the top
    try:
        font = ImageFont.truetype("impact.ttf", font_size)
    except IOError:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
            st.warning("Impact font not found – using default font (size may look different)")

    draw = ImageDraw.Draw(img)
    lines = textwrap.wrap(caption.upper(), width=30)  # Slightly wider wrap for larger fonts

    # Dynamic line height and padding based on font size
    line_height = int(font_size * 1.2) + 10
    top_padding = max(40, font_size)  # More padding for bigger text
    total_text_height = len(lines) * line_height + top_padding * 2

    # Create new canvas with black bar only at the top
    new_img = Image.new("RGB", (img.width, img.height + total_text_height), (0, 0, 0))
    new_img.paste(img, (0, total_text_height))
    draw = ImageDraw.Draw(new_img)

    # Helper for thick black outline + white fill
    def draw_outlined_text(text, x, y):
        outline_range = max(3, font_size // 20)  # Thicker outline for larger fonts
        for adj_x in range(-outline_range, outline_range + 1):
            for adj_y in range(-outline_range, outline_range + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=(0, 0, 0))
        draw.text((x, y), text, font=font, fill=(255, 255, 255))

    # Draw centered text at the top
    y = top_padding
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (img.width - w) / 2
        draw_outlined_text(line, x, y)
        y += line_height

    return new_img

if uploaded_file is not None:
    # Detect new upload
    current_upload_key = f"{uploaded_file.name}_{uploaded_file.size}"

    if "last_upload_key" not in st.session_state or st.session_state.last_upload_key != current_upload_key:
        st.session_state.clear()
        st.session_state.last_upload_key = current_upload_key

    # Load image/video frame
    if uploaded_file.type.startswith("video/"):
        with st.spinner("Extracting key frame..."):
            img = extract_key_frame(uploaded_file.getvalue())
    else:
        img = Image.open(uploaded_file)

    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.image(img, width="stretch", caption="Original")

    with col2:
        st.write("### Choose a Viral Caption")

        if "captions" not in st.session_state:
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
                st.session_state.captions = [line.strip()[2:] for line in raw.split("\n") if line.strip().startswith("• ")]

        captions = st.session_state.captions

        selected_idx = st.radio(
            "Pick one caption:",
            options=range(len(captions)),
            format_func=lambda i: f"{i+1}. {captions[i]}",
            label_visibility="collapsed"
        )
        selected_caption = captions[selected_idx]

        # Font size slider
        font_size = st.slider(
            "Text Size",
            min_value=30,
            max_value=150,
            value=70,
            step=5,
            help="Adjust the meme text size (bigger = bolder impact!)"
        )

    # Generate meme with selected caption and font size
    meme_img = add_meme_caption(img.copy(), selected_caption, font_size)

    st.divider()
    st.image(meme_img, width="stretch", caption=f"\"{selected_caption}\" • Font size: {font_size}")

    # Download
    buffered = io.BytesIO()
    meme_img.save(buffered, format="PNG")
    st.download_button(
        label="📥 Download Meme as PNG",
        data=buffered.getvalue(),
        file_name=f"meme_font{font_size}_{selected_idx+1}.png",
        mime="image/png"
    )

    st.info(
        "💡 **Pro tip:** Try extreme sizes (30 for subtle, 120+ for absolute chaos)!\n"
        "Download and share anywhere."
    )

else:
    st.info("↑ Upload any image or video → get 10 captions → pick one → adjust text size → download your perfect meme!")

st.markdown("---")
st.caption("Meme Creator • Top-caption only • Adjustable text size • Maximum chaos control! 🔥")
