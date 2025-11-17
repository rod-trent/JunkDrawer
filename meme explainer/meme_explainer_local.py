# meme_explainer_local.py - FIXED & READY NOV 17 2025
import os
import gradio as gr
import requests
from PIL import Image
import base64
import io

# ============== CONFIG ==============
XAI_API_KEY = os.getenv("XAI_API_KEY") or "paste_your_real_key_here"

# Choose your generation backend
MODE = "local-flux"          # "local-flux" = unlimited free with ComfyUI/Forge
                             # "grok-only" = Grok-4 generates the images (if you have access)

LOCAL_FLUX_URL = "http://127.0.0.1:7860"   # ComfyUI / Forge default
# =====================================

def encode_image(img_pil):
    buf = io.BytesIO()
    img_pil.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def explain_meme(image):
    if image is None:
        return "↑ Upload a meme first!", None, None, None

    base64_img = encode_image(image)

    payload = {
        "model": "grok-beta",   # This one actually has vision right now
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": """
You are the saltiest meme professor alive.
- Exact template name (or say it's original)
- Transcribe all text perfectly
- Explain the joke + roast it
- Full cultural context and origin year
Be savage and hilarious.
"""},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
            ]
        }],
        "max_tokens": 1024,
        "temperature": 0.9
    }

    try:
        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {XAI_API_KEY}"},
            json=payload,
            timeout=60
        )
        r.raise_for_status()
        explanation = r.json()["choices"][0]["message"]["content"]
        return explanation, image, None, None
    except requests.exceptions.HTTPError as e:
        if "400" in str(e) or "vision" in str(e).lower():
            return (
                "Vision not available on your account yet (still rolling out).\n\n"
                "No problem! Just type what the meme shows below and we'll keep going:\n"
                "Example: 'Drake hotline bling: hates JavaScript, loves Python'",
                image, None, None
            )
        return f"API error: {e}", image, None, None

def generate_variation(image, explanation, user_topic):
    if not explanation or "Upload" in explanation or "Vision" in explanation:
        return None, "Explain or describe the meme first!"

    topic = user_topic.strip() or "something extremely 2025-pilled"

    prompt_gen = f"""
Original meme breakdown:
{explanation}

Make a new version of this EXACT template about: {topic}
Keep identical style, font, layout, colors. Change only the text/content.

Output ONLY the raw image-generation prompt. Nothing else.
"""

    try:
        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            json={"model": "grok-beta", "messages": [{"role": "user", "content": prompt_gen}],
                  "temperature": 0.95, "max_tokens": 350},
            headers={"Authorization": f"Bearer {XAI_API_KEY}"},
            timeout=30
        )
        r.raise_for_status()
        final_prompt = r.json()["choices"][0]["message"]["content"].strip()

        new_img = None

        if MODE == "grok-only":
            # Grok-4 image gen (when available)
            ri = requests.post(
                "https://api.x.ai/v1/images/generations",
                json={"model": "grok-beta", "prompt": final_prompt, "n": 1, "size": "1024x1024"},
                headers={"Authorization": f"Bearer {XAI_API_KEY}"}
            )
            ri.raise_for_status()
            new_img = Image.open(requests.get(ri.json()["data"][0]["url"], stream=True).raw)

        elif MODE == "local-flux":
            payload = {
                "prompt": final_prompt,
                "steps": 20,
                "cfg": 3.5,
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            }
            r_local = requests.post(f"{LOCAL_FLUX_URL}/sdapi/v1/txt2img", json=payload, timeout=180)
            r_local.raise_for_status()
            b64 = r_local.json()["images"][0]
            new_img = Image.open(io.BytesIO(base64.b64decode(b64)))

        return new_img, final_prompt

    except Exception as e:
        return None, f"Generation failed: {str(e)}"

# ============== GRADIO UI (fixed theme) ==============
with gr.Blocks() as demo:   # ← removed the broken theme line
    gr.Markdown("# 🗿 Grok Meme Explainer & Infinite Generator")
    gr.Markdown("Upload → Explain → Generate unlimited perfect clones • Works even without vision access")

    with gr.Row():
        inp = gr.Image(type="pil", label="Upload any meme", height=420)

    btn_explain = gr.Button("Explain This Meme 🧠", variant="primary", size="lg")

    explanation = gr.Textbox(label="Grok's breakdown (or type your description here if vision blocked)", lines=12)
    original = gr.Image(label="Original", height=400)

    gr.Markdown("### Generate Variations")
    with gr.Row():
        topic = gr.Textbox(label="New topic (optional)", placeholder="e.g. AI devs choosing sleep over one bug", scale=4)
        btn_gen = gr.Button("Generate 🚀", variant="secondary", size="lg")

    with gr.Row():
        output_img = gr.Image(label="New Meme", height=520)
        prompt_box = gr.Textbox(label="Prompt used", lines=3)

    btn_explain.click(explain_meme, inputs=inp, outputs=[explanation, original, output_img, prompt_box])
    btn_gen.click(generate_variation, inputs=[inp, explanation, topic], outputs=[output_img, prompt_box])

    gr.Markdown("Unlimited free memes • Nov 17 2025 • Built with Grok 🗿")

demo.launch(share=True)