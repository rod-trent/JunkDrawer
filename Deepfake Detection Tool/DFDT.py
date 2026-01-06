import streamlit as st
import os
from dotenv import load_dotenv
import openai
import base64
import requests
from io import BytesIO
from PIL import Image
import moviepy as mp  # Updated for MoviePy v2+
from moviepy.video.io.VideoFileClip import VideoFileClip
import tempfile

# Load environment variables
load_dotenv()
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    st.error("XAI_API_KEY not found in .env file. Please add it and restart the app.")
    st.stop()

# Initialize xAI client (OpenAI-compatible)
client = openai.OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1"
)

# Current vision-capable model as of January 2026
# Use the model available to your API tier. Common vision models: grok-4, grok-4-fast-reasoning
MODEL = "grok-4"  # Try "grok-4-fast-reasoning" if you get access errors

# Function to convert PIL Image to base64
def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode()

# Function to extract key frames from video
def extract_frames(video_path: str, num_frames: int = 10) -> list:
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        if duration == 0:
            st.warning("Video has zero duration.")
            clip.close()
            return []
        
        step = max(1.0, duration / (num_frames + 1))
        frames = []
        times = [i * step for i in range(1, num_frames + 1)]
        
        for t in times:
            if t > duration:
                break
            frame = clip.get_frame(t)
            img = Image.fromarray(frame)
            frames.append(image_to_base64(img))
        
        clip.close()
        return frames
    except Exception as e:
        st.error(f"Error extracting frames: {e}")
        return []

# Function to analyze media using Grok Vision
@st.cache_data(ttl=3600)  # Cache results for 1 hour
def analyze_media(content_list: list) -> str:
    prompt = """
You are an expert deepfake detection analyst. Analyze the provided image(s) or video frames for signs of deepfake manipulation.

Look carefully for:
- Inconsistent lighting, shadows, or reflections
- Unnatural facial proportions, asymmetries, or skin textures
- Artifacts around eyes, mouth, teeth, hair, or edges
- Mismatched eye gaze or blink irregularities
- Blending issues with background
- Temporal inconsistencies (flickering, warping) across frames if multiple images are provided
- Any other unnatural or synthetic indicators

Provide your response in this exact structure:
1. Confidence Score: X/100 (where 100 = definitely deepfake, 0 = definitely authentic)
2. Verdict: Real | Likely Real | Uncertain | Likely Deepfake | Deepfake
3. Detailed Reasoning: Bullet-point list of observations supporting your verdict

Be critical and evidence-based.
"""

    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}] + content_list
        }
    ]

    try:
        with st.spinner("Sending to Grok Vision for analysis..."):
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"API Error: {str(e)}"

# Main App UI
st.set_page_config(page_title="Deepfake Detector", layout="centered")
st.title("🕵️ Deepfake Detection Tool")
st.markdown("""
Upload an image or video, or paste a direct media URL.  
This tool uses **Grok Vision** (via xAI API) to detect potential deepfake manipulation.
""")

st.info("Note: Detection is AI-assisted and not 100% accurate. Always cross-verify with multiple sources.")

# Input method
input_type = st.radio("Input Method", ["Upload File", "Direct URL"])

content_list = []
media_type = None

if input_type == "Upload File":
    uploaded_file = st.file_uploader(
        "Choose an image (JPG/PNG/WEBP) or video (MP4/MOV/AVI)",
        type=["jpg", "jpeg", "png", "webp", "mp4", "mov", "avi"]
    )
    
    if uploaded_file:
        file_mime = uploaded_file.type
        if file_mime.startswith("image/"):
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Image", width="stretch")
            b64 = image_to_base64(image)
            content_list = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]
            media_type = "image"
        
        elif file_mime.startswith("video/"):
            st.video(uploaded_file)
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name
            
            frames_b64 = extract_frames(tmp_path)
            os.unlink(tmp_path)
            
            if frames_b64:
                st.success(f"Extracted {len(frames_b64)} key frames for analysis.")
                content_list = [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}}
                    for frame in frames_b64
                ]
                media_type = "video"
            else:
                st.error("Failed to extract frames from video.")
        
        else:
            st.error("Unsupported file type.")

elif input_type == "Direct URL":
    url = st.text_input("Enter direct URL to image or video (e.g., ending in .jpg, .mp4)")
    
    if url and st.button("Load Media"):
        try:
            head = requests.head(url, allow_redirects=True, timeout=10)
            content_type = head.headers.get("content-type", "").lower()

            if "image" in content_type or url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                image = Image.open(BytesIO(resp.content)).convert("RGB")
                st.image(image, caption="Loaded from URL", width="stretch")
                b64 = image_to_base64(image)
                content_list = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]
                media_type = "image"

            elif "video" in content_type or url.lower().endswith((".mp4", ".mov", ".avi")):
                resp = requests.get(url, stream=True, timeout=15)
                resp.raise_for_status()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                    for chunk in resp.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
                    tmp_path = tmp_file.name
                
                st.video(url)
                frames_b64 = extract_frames(tmp_path)
                os.unlink(tmp_path)
                
                if frames_b64:
                    st.success(f"Extracted {len(frames_b64)} key frames.")
                    content_list = [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}}
                        for frame in frames_b64
                    ]
                    media_type = "video"
                else:
                    st.error("Could not process video from URL.")
            else:
                st.error("URL does not appear to be a direct image or video link.")
        
        except Exception as e:
            st.error(f"Error loading URL: {e}")

# Analysis Section
if content_list and st.button("🔍 Analyze for Deepfake", type="primary"):
    with st.spinner("Grok Vision is analyzing the media... This may take 10-30 seconds."):
        result = analyze_media(content_list)
    
    st.subheader("Deepfake Analysis Result")
    st.markdown(result)

    if media_type == "video":
        st.caption("Analysis based on multiple extracted frames for temporal consistency.")

# Sidebar Info
st.sidebar.header("About")
st.sidebar.markdown("""
- Powered by **Grok Vision** (xAI API)
- Supports images and videos
- Best for face-focused media
- Not foolproof — deepfakes are evolving rapidly
""")

st.sidebar.header("Tips for Better Results")
st.sidebar.markdown("""
- Use high-quality, well-lit media
- Videos yield better results than single images
- Focus on faces when possible
""")

st.sidebar.header("Model Note")
st.sidebar.markdown("""
If you get a model not found error, check available models in the xAI Console and update `MODEL` accordingly (e.g., `grok-4-fast-reasoning`).
""")