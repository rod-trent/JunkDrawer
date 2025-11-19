# Build Instant Viral Memes with Grok-4 Vision – Introducing Meme Builder

Tired of staring at a funny picture trying to come up with the perfect caption?  
I just pushed a ridiculously simple (and ridiculously fun) Streamlit app that does it for you — powered by **Grok-4 Vision**.

Upload any image or video → get **10 brand-new, ultra-viral meme captions** instantly.  
Every single time you upload, it generates completely fresh captions. No repeats, no caching, pure chaos.

Live demo & source (forever free & open-source):  
https://github.com/rod-trent/JunkDrawer/tree/main/MemeBuilder

## What It Is

Meme Builder is a one-page Streamlit app that:

1. Accepts images (png, jpg, webp, gif) **or videos** (mp4, mov, webm, avi).
2. If you upload a video, it automatically extracts a key frame (the first readable frame – works great for short clips).
3. Sends that frame to **Grok-4 Vision** (xAI’s latest multimodal model).
4. Asks Grok-4 to generate exactly 10 bullet-point viral meme captions.
5. Displays your image + the 10 captions side-by-side.

Because we clear the session state on every new upload, you literally get brand-new captions every single time — even if you upload the exact same file twice.

## Why It’s Addictive

- Grok-4 Vision actually understands what’s happening in the photo/video (objects, emotions, context, absurdity level).
- Temperature 0.95 + zero system prompt = maximum unhinged creativity.
- Zero login on your end (you just need your own Grok API key).
- Works perfectly with reaction videos, pet clips, screenshots, anything.

## Requirements

You need exactly two things:

1. **Python 3.9+**
2. **A Grok API key** from https://console.x.ai (the same key you use for Grok-4 on grok.com or the apps)

That’s it.

## How to Run It Locally

```bash
# 1. Clone the repo (or just grab the single file)
git clone https://github.com/rod-trent/JunkDrawer.git
cd JunkDrawer/MemeBuilder

# 2. Create virtual env (optional but recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install streamlit requests pillow opencv-python python-dotenv

# 4. Create a .env file in the same folder with your key
echo "GROK_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" > .env

# 5. Run it
streamlit run memebuilder.py
```

Open your browser to http://localhost:8501 and start memeing.

## Deploy It Yourself (Free Options)

- Streamlit Community Cloud (connect the GitHub repo → auto-deploys)
- Hugging Face Spaces
- Railway, Render, Fly.io, etc.

Just make sure your Grok API key is stored as a secret in the platform.

## Example Captions Grok-4 Just Gave Me

Uploaded the classic “Distracted Boyfriend” stock photo → here’s a sample of what it spat out in 4 seconds:

- When you see the new Grok-4 update but remember you still haven’t finished your taxes  
- Me walking past the salad bar straight to the pizza station  
- Developers seeing yet another JS framework drop  
- My salary looking at my rent prices  
- Elon changing his profile picture again

Pure gold.

## Go Make Something Dumb

Grab the code, throw in your API key, and go ruin your group chat with perfectly tailored memes.

Permanent home:  
https://github.com/rod-trent/JunkDrawer/tree/main/MemeBuilder

Enjoy the chaos. 🧠💥

P.S. Yes, it works with GIFs and short TikTok/Instagram Reels clips too. Try uploading your dog staring at nothing for 15 seconds — the captions are unhinged.
