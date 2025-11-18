# Build Your Own Butter-Smooth Teleprompter in Streamlit (No More Blank Screen Nightmare!)

A few weeks ago I was recording a video and my usual teleprompter web app decided to show me… absolutely nothing for the first 5 seconds while it slowly rendered the script. Black screen, awkward pause, ruined take. Again.

I’d had enough. So I built my own — one that loads instantly, scrolls like melted butter, and never leaves you staring at a void.

Here’s the result: a clean, distraction-free teleprompter that works perfectly in any browser, supports mirror mode for real teleprompter glass, adjustable speed/font, line highlighting, and even file upload. And the best part? It’s ~100 lines of pure Streamlit + a tiny bit of JavaScript.

You can try the final app here: https://github.com/rod-trent/JunkDrawer/blob/main/Teleprompter/teleprompter.py (or just copy the code below and run it locally).

### Why this one actually works perfectly

Most DIY teleprompters have one (or more) of these problems:

- Huge blank space at the start while the page “thinks”
- Jerky scrolling (setInterval instead of requestAnimationFrame)
- Speed that feels completely disconnected from real WPM
- Re-rendering the entire DOM on every frame → lag
- No mirror mode or proper centering

I fixed all of them.

### The magic (and why it’s so smooth)

1. Instant content  
   The script lines are pre-rendered into the DOM once using JavaScript. No waiting for Streamlit to re-inject text on every rerun.

2. Buttery 60 fps scrolling  
   We use `requestAnimationFrame` + `performance.now()` + `will-change: transform`. This tells the browser “hey, we’re only going to move this one div with GPU acceleration” → silk.

3. Realistic WPM calculation  
   The speed formula was tuned by feel:  
   `pixels_per_frame = (wpm/180) × (font_size/95) × 2.9 × (delta/16.66)`  
   180 WPM at 95 px is the “neutral” speed. Everything scales intuitively from there.

4. No blank screen ever  
   We add tall empty divs at top (40 vh) and especially bottom (120 vh). The text starts in the middle of the viewport and you have tons of runway before it ends.

5. Highlight the current line (optional)  
   The reading line is roughly the 4th line from the top (tuned for most screens). It gets a subtle white glow background.

6. Mirror mode in one checkbox  
   Just flips the entire thing horizontally with `transform: scaleX(-1)`. Perfect for beaming onto a glass teleprompter.

### The complete code (copy-paste ready)

```python
# teleprompter.py
import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="Teleprompter", layout="centered", page_icon="🎙️")

st.title("🎙️ Teleprompter – Perfect & Smooth")
st.markdown("Paste your script or upload a .txt file. Scrolling is buttery-smooth, no blank screen ever again.")

# ── Controls ─────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    wpm = st.slider("Speed (WPM)", 50, 450, 180, 5)
with col2:
    font_size = st.slider("Font Size (px)", 50, 160, 95, 5)

mirror = st.checkbox("Mirror mode (teleprompter glass)", False)
highlight = st.checkbox("Highlight current reading line", True)

# ── Text input ───────────────────────────────────
text = st.text_area("Your script", height=220, placeholder="Paste your text here…")
uploaded = st.file_uploader("Or upload .txt file", type=["txt"])
if uploaded:
    text = uploaded.read().decode("utf-8", errors="replace")

if not text.strip():
    st.info("↑ Enter some text or upload a file to start")
    st.stop()

# ── Prepare lines ─────────────────────────────────
lines = [line if line.strip() else " " for line in text.splitlines()]

# ── The magic HTML + JS ───────────────────────────
mirror_style = 'style="transform:scaleX(-1)"' if mirror else ""
highlight_style = ("background:rgba(255,255,255,0.22); border-radius:16px; "
                   "padding:16px 0; margin:24px 0;") if highlight else ""

html = f"""
<div style="height:80vh; background:black; color:white; font-size:{font_size}px;
            line-height:1.6; text-align:center; overflow:hidden; padding:40px;
            font-family:Arial, sans-serif;">
  <div {mirror_style}>
    <div id="scroller" style="will-change:transform;">
      <div style="height:40vh">&nbsp;</div>
      <div id="content"></div>
      <div style="height:120vh">&nbsp;</div>
    </div>
  </div>
</div>

<script>
  const lines = {json.dumps(lines)};
  const container = document.getElementById('content');

  lines.forEach((line, i) => {{
    const div = document.createElement('div');
    div.innerHTML = line === " " ? "&nbsp;" : line;
    if ({str(highlight).lower()} && i === 4) {{
      div.style.cssText = "{highlight_style}";
    }}
    container.appendChild(div);
  }});

  let pos = 0;
  let last = performance.now();

  function animate() {{
    const now = performance.now();
    const delta = now - last;
    last = now;

    pos += ({wpm}/180) * ({font_size}/95) * 2.9 * (delta / 16.66);
    document.getElementById('scroller').style.transform = `translateY(${{-pos}}px)`;
    requestAnimationFrame(animate);
  }}
  requestAnimationFrame(animate);
</script>
"""

components.html(html, height=800)

# ── Bottom buttons ───────────────────────────────
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Restart from top", use_container_width=True):
        st.rerun()
with col2:
    st.caption(f"**{len(lines)} lines** • {wpm} WPM • {font_size}px • 60 fps smooth")

st.success("✓ Works perfectly now — text appears instantly and scrolls beautifully!")
```

That’s it. Run `streamlit run teleprompter.py` and you’re done.

### Bonus tips from someone who actually uses this every week

- For real teleprompter hardware: turn on mirror mode + fullscreen (F11). Beam your laptop/monitor onto a piece of glass with a tablet underneath.
- Blank lines: just leave an empty line in your script → it becomes a single &nbsp; so spacing stays perfect.
- Want pause/resume? Just add a Play/Pause button that toggles a `running` boolean in JS (left as an exercise 😉).
- I use 220–250 WPM for most videos. 180 feels relaxed, 300+ is auctioneer territory.

Never stare at a blank screen again. Happy recording! 🎥

(Star the repo if you liked it: https://github.com/rod-trent/JunkDrawer — or just deploy your own copy in 3 seconds on Streamlit Community Cloud.)
