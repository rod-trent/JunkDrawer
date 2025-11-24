# app.py
import streamlit as st
import os
from dotenv import load_dotenv
import requests
from PIL import Image
import base64
from io import BytesIO

# Load API key
load_dotenv()
api_key = os.getenv("XAI_API_KEY")

if not api_key:
    st.error("⚠️ Please add your XAI_API_KEY to the .env file")
    st.stop()

st.set_page_config(page_title="AI Palm Reader", page_icon="Hand")

st.title("AI Palm Reader")
st.markdown("Upload a clear photo of your palm and let Grok read your future! ✨")

# File uploader
uploaded_file = st.file_uploader(
    "Upload your palm (open hand, good lighting)",
    type=["png", "jpg", "jpeg"],
    help="Best results with your dominant hand, fingers slightly apart."
)

if uploaded_file:
    # Show the image
    image = Image.open(uploaded_file)
    st.image(
        image,
        caption="Your palm",
        use_container_width=True   # ← Fixed deprecation
    )

    # Convert image to base64
    buffered = BytesIO()
    # Convert to RGB if RGBA (transparency causes issues with some JPEG saves)
    if image.mode != "RGB":
        image = image.convert("RGB")
    image.save(buffered, format="JPEG", quality=90)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    data_url = f"data:image/jpeg;base64,{img_str}"

    if st.button("Read My Palm 🔮", type="primary"):
        with st.spinner("Grok is studying your palm lines..."):
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "grok-4",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
                            {
                                "type": "text",
                                "text": """You are a master palmist. Give a detailed, fun, and insightful palm reading based on this photo.

Analyze and describe:
• Hand shape (Earth, Air, Fire, Water)
• Life Line, Heart Line, Head Line, Fate Line (if visible)
• Mounts, finger lengths, any special markings
• Personality, love life, career tendencies, health insights

Structure your reading beautifully with emojis and clear sections.
Keep it positive, empowering, and entertaining — this is for fun!"""
                            }
                        ]
                    }
                ],
                "max_tokens": 1200,
                "temperature": 0.85
            }

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                reading = response.json()["choices"][0]["message"]["content"]

                st.success("Here’s your palm reading!")
                st.markdown(reading)

            except requests.exceptions.HTTPError as e:
                st.error(f"API error: {e.response.status_code} – {e.response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

# Sidebar instructions
with st.sidebar:
    st.header("How to use")
    st.write("""
    1. Place your hand palm-up on a plain background
    2. Good lighting, no shadows over the lines
    3. Fingers slightly apart
    4. Upload & click **Read My Palm**
    """)
    st.info("This app uses the official xAI / Grok API • Entertainment purposes only")

    st.caption(f"Streamlit + Grok-4 • {st.__version__}")