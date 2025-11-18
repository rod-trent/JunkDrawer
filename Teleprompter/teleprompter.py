import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="Teleprompter", layout="centered", page_icon="🎙️")

st.title("🎙️ Teleprompter – Play/Pause Done Right")
st.markdown("Smooth scrolling • Highlight • Mirror • Instant Play/Pause")

# Controls
col1, col2 = st.columns(2)
with col1:
    wpm = st.slider("Speed (WPM)", 50, 450, 180, 5)
with col2:
    font_size = st.slider("Font Size (px)", 50, 160, 95, 5)

mirror = st.checkbox("Mirror mode", False)
highlight = st.checkbox("Highlight reading line", True)

# Text input
text = st.text_area("Your script", height=220)
uploaded = st.file_uploader("Or upload .txt", type=["txt"])
if uploaded:
    text = uploaded.read().decode("utf-8", errors="replace")

if not text.strip():
    st.stop()

lines = [line if line.strip() else " " for line in text.splitlines()]

# Session state
if "playing" not in st.session_state:
    st.session_state.playing = True
if "reset" not in st.session_state:
    st.session_state.reset = False

# Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Play" if not st.session_state.playing else "⏸ Pause", use_container_width=True):
        st.session_state.playing = not st.session_state.playing
        st.rerun()
with col2:
    if st.button("🔄 Restart from top", use_container_width=True):
        st.session_state.reset = True
        st.session_state.playing = True
        st.rerun()

# Build HTML + JS
mirror_style = 'style="transform:scaleX(-1)"' if mirror else ""
highlight_style = "background:rgba(255,255,255,0.22); border-radius:16px; padding:16px 0; margin:24px 0;" if highlight else ""

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
  // Build content only once
  if (!window.built) {{
    const lines = {json.dumps(lines)};
    const container = document.getElementById('content');
    lines.forEach((line, i) => {{
      const div = document.createElement('div');
      div.innerHTML = line === " " ? "&nbsp;" : line;
      if ({str(highlight).lower()} && i === 4) div.style.cssText = "{highlight_style}";
      container.appendChild(div);
    }});
    window.built = true;
  }}

  // Scrolling logic
  let pos = window.pos || 0;
  let last = performance.now();
  let frame;

  function animate() {{
    const now = performance.now();
    const delta = now - last;
    last = now;
    pos += ({wpm}/180) * ({font_size}/95) * 2.9 * (delta / 16.66);
    document.getElementById('scroller').style.transform = `translateY(${{-pos}}px)`;
    window.pos = pos;
    frame = requestAnimationFrame(animate);
  }}

  // Play/Pause control
  if ({str(st.session_state.playing).lower()}) {{
    if (!frame) requestAnimationFrame(animate);
  }} else {{
    if (frame) cancelAnimationFrame(frame);
    frame = null;
  }}

  // Reset control
  if ({str(st.session_state.reset).lower()}) {{
    pos = 0;
    window.pos = 0;
    document.getElementById('scroller').style.transform = 'translateY(0px)';
    window.location.href = window.location.href;  // forces full rebuild once
  }}
</script>
"""

components.html(html, height=800)

# Reset the reset flag after use
if st.session_state.reset:
    st.session_state.reset = False


st.caption(f"**{len(lines)} lines** • {wpm} WPM • {'Playing' if st.session_state.playing else 'Paused'}")
