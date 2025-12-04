# PurviewQuest_Local.py – 100% LOCAL, NO API KEYS, NO INTERNET
import streamlit as st
import os
import re
import random
import requests
import json

# ------------------------------------------------------------------
# CONFIG: Change this to match your local LLM endpoint
# ------------------------------------------------------------------
# Default: Ollama running locally[](http://localhost:11434)
LOCAL_LLM_URL = "http://localhost:11434/v1/chat/completions"
LOCAL_MODEL = "llama3.2:latest"  # or "grok:beta", "mistral", "phi3", etc.

# Test if Ollama is running
def check_llm():
    try:
        requests.post(LOCAL_LLM_URL, json={"model": LOCAL_MODEL, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1}, timeout=3)
        return True
    except:
        return False

if not check_llm():
    st.error(
        "Local LLM not detected!\n\n"
        "Please make sure Ollama is running with a model pulled:\n"
        "→ Open terminal and run: `ollama run llama3.2` (or your preferred model)\n"
        "Then restart this app."
    )
    st.stop()

# ------------------------------------------------------------------
# Page config & CSS (same beautiful style)
# ------------------------------------------------------------------
st.set_page_config(page_title="Microsoft Purview Quest", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .logo-container {display: flex; justify-content: center; align-items: center; margin: 40px 0 20px 0;}
    .big-title {font-size: 3.8rem !important; font-weight: bold; text-align: center;
                background: linear-gradient(90deg, #00d4ff, #0068ff);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 10px 0 20px 0;}
    .subtitle {text-align: center; font-size: 1.4rem; color: #bbb; margin-bottom: 30px;}
    .scene-box {background: rgba(10, 25, 50, 0.9); padding: 2rem; border-radius: 15px;
                border: 2px solid #00d4ff; box-shadow: 0 0 25px #00d4ff50; font-size: 1.1rem; line-height: 1.6; margin-bottom: 30px;}
    .day-badge {background: linear-gradient(90deg, #00d4ff, #0068ff); color: white; padding: 0.6rem 1.2rem;
                border-radius: 30px; font-size: 1.6rem; font-weight: bold;}
    .stButton>button {height: 90px; font-size: 1.1rem; border: 2px solid #00d4ff; background: rgba(0,212,255,0.1);}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Session state
# ------------------------------------------------------------------
if "compliance_score" not in st.session_state:
    st.session_state.compliance_score = 40
    st.session_state.risk = 80
    st.session_state.steps = 0
    st.session_state.history = []
    st.session_state.game_over = False

# ------------------------------------------------------------------
# Logo & Header
# ------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    # Embedded small base64 Purview logo (fallback if file missing)
    try:
        st.image("Microsoft_Purview_Logo.svg.png", width=200)
    except:
        st.image("https://upload.wikimedia.org/wikipedia/commons/9/94/Microsoft_Purview_Logo.png", width=200)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<h1 class='big-title'>Microsoft Purview Quest</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>30 days until audit • Can you save Zava from total compliance disaster?</p>", unsafe_allow_html=True)
st.divider()

# ------------------------------------------------------------------
# Metrics
# ------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    color = "#00ff9d" if st.session_state.compliance_score >= 70 else "#ff2d55"
    st.markdown(f"**Compliance**<br><span style='color:{color};font-size:1.8rem;font-weight:bold'>{st.session_state.compliance_score}/100</span>", unsafe_allow_html=True)
with c2:
    color = "#00ff9d" if st.session_state.risk <= 40 else "#ff2d55"
    st.markdown(f"**Risk Level**<br><span style='color:{color};font-size:1.8rem;font-weight:bold'>{st.session_state.risk}/100</span>", unsafe_allow_html=True)
with c3:
    day = max(1, 30 - st.session_state.steps * 6)
    st.markdown(f"<div class='day-badge'>Day {day}</div>", unsafe_allow_html=True)
with c4:
    st.progress(st.session_state.steps / 5.0)

# ------------------------------------------------------------------
# Local LLM call (cached)
# ------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def ask_local_llm(prompt: str) -> str:
    with st.spinner("Local AI is thinking..."):
        try:
            response = requests.post(
                LOCAL_LLM_URL,
                json={
                    "model": LOCAL_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.9
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[Local LLM error: {e}]"

# ------------------------------------------------------------------
# Game Over Screen
# ------------------------------------------------------------------
if st.session_state.steps >= 5:
    st.session_state.game_over = True
    st.balloons()
    st.confetti()

    if st.session_state.compliance_score >= 80 and st.session_state.risk < 30:
        st.success("🎉 CISO PROMOTION AT ZAVA! 🎉")
    elif st.session_state.compliance_score >= 50:
        st.warning("🦸 Zava Compliant Hero — You saved the day!")
    else:
        st.error("💀 FIRED FROM ZAVA.")

    ending_prompt = f"""
    Write a dramatic, funny, corporate ending (150–250 words) for "Microsoft Purview Quest" at Zava Corp.
    Final score: {st.session_state.compliance_score}/100 compliance, Risk: {st.session_state.risk}/100.
    Player path: {' → '.join([h.split('(+')[0].strip() for h in st.session_state.history])}
    End with one real actionable Microsoft Purview tip.
    """
    ending = ask_local_llm(ending_prompt)

    st.markdown(f"<div class='scene-box'>{ending}</div>", unsafe_allow_html=True)

    if st.button("New Quest", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.stop()

# ------------------------------------------------------------------
# Generate Scene using Local LLM
# ------------------------------------------------------------------
n = 3 if st.session_state.steps == 0 else 2
choice_format = "\n".join([f"{i+1}. [choice]" for i in range(n)])

scene_prompt = f"""
You are writing a Microsoft Purview choose-your-own-adventure game set at fictional company "Zava".
Current day: {max(1, 30 - st.session_state.steps * 6)}. Audit in {max(1, 30 - st.session_state.steps * 6)} days.

Write ONLY in this exact format:

**Scene:**
[2–3 immersive, dramatic, slightly funny paragraphs about compliance chaos at Zava]

**Choices:**
{choice_format}

Each choice must involve a real Microsoft Purview feature (sensitivity labels, DLP, retention policies, audit logs, eDiscovery, data classification, communication compliance, insider risk, etc.)
Make choices tempting but with different risk/reward.
"""

story = ask_local_llm(scene_prompt)

# Parse response
scene_match = re.search(r"\*\*Scene:\*\*\s*(.*?)\s*\*\*Choices:\*\*", story, re.DOTALL | re.IGNORECASE)
choices_match = re.search(r"\*\*Choices:\*\*\s*(.*)", story, re.DOTALL | re.IGNORECASE)

scene_text = scene_match.group(1).strip() if scene_match else "Panic at Zava! The auditors are coming and nothing is labeled, retained, or audited!"
raw_choices = choices_match.group(1) if choices_match else ""

choices = [line.strip() for line in raw_choices.split("\n") if re.match(r"^\d+\.", line.strip())]

# Fallback choices if parsing fails
if len(choices) < n:
    fallback = [
        "1. Rush to apply sensitivity labels to all customer contracts",
        "2. Implement strict DLP policies blocking USB and email exfil",
        "3. Turn on full audit logging and hope for the best",
        "4. Set up retention policies for financial records"
    ]
    choices = fallback[:n]

# ------------------------------------------------------------------
# Display Scene & Choices
# ------------------------------------------------------------------
st.markdown(f"<div class='scene-box'><strong>Scene</strong><br><br>{scene_text}</div>", unsafe_allow_html=True)
st.markdown("### Your Move")

cols = st.columns(min(3, len(choices)))
for i, choice in enumerate(choices):
    with cols[i % len(cols)]:
        if st.button(choice, key=f"choice_{i}", use_container_width=True):
            lowered = choice.lower()

            # Score adjustments based on real Purview best practices
            if any(x in lowered for x in ["label", "sensitivity", "classify"]): 
                d = (18, -15)
            elif any(x in lowered for x in ["retention", "policy", "archive"]): 
                d = (15, -18)
            elif any(x in lowered for x in ["audit", "logging", "search"]): 
                d = (20, -20)
            elif any(x in lowered for x in ["dlp", "prevent", "block"]): 
                d = (22, -12)
            elif any(x in lowered for x in ["ediscovery", "investigation"]): 
                d = (17, -10)
            else: 
                d = (-10, 20)  # risky move

            st.session_state.compliance_score += d[0]
            st.session_state.risk += d[1]
            st.session_state.history.append(f"{choice} (+{d[0]} score, {d[1]:+} risk)")
            st.session_state.steps += 1

            st.session_state.compliance_score = max(0, min(100, st.session_state.compliance_score))
            st.session_state.risk = max(0, min(100, st.session_state.risk))
            st.rerun()

# ------------------------------------------------------------------
# Sidebar & Footer
# ------------------------------------------------------------------
with st.sidebar:
    st.header("Zava Audit Trail")
    for h in st.session_state.history:
        st.write(f"• {h}")
    st.caption(f"Powered locally by {LOCAL_MODEL}")

st.markdown("---")
st.caption("Microsoft Purview Quest • Fully Offline Edition • Powered by Local AI")