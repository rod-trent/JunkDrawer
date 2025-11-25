import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from utils import query_grok

# Load .env file
load_dotenv()

# ============================
# Page Config
# ============================
st.set_page_config(page_title="Threat Actor Empathy Simulator", layout="wide")
st.title("Threat Actor Empathy Simulator")
st.markdown("### Think like an elite attacker. Build defenses that actually work.")

# ============================
# API Key Check – ONLY from .env
# ============================
if not os.getenv("GROK_API_KEY"):
    st.error(
        """
        GROK_API_KEY not found!

        Create a file named `.env` in the same folder with this line:

        GROK_API_KEY=your_real_key_here

        Then restart the app.
        """
    )
    st.stop()

# ============================
# Session State Initialization
# ============================
defaults = {
    "game_id": None,
    "history": [],
    "score": 100,
    "stage": 0,
    "target": "",
    "room_code": "SOLO",
    "player_name": "Defender"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================
# Sidebar – Game Setup
# ============================
with st.sidebar:
    st.header("Simulation Setup")

    mode = st.radio("Mode", ["Solo", "Multiplayer (Team Exercise)"])

    if mode == "Multiplayer (Team Exercise)":
        st.session_state.room_code = st.text_input("Room Code", value=st.session_state.room_code).upper()[:8]
        st.session_state.player_name = st.text_input("Your Name/Role", value=st.session_state.player_name)
    else:
        st.session_state.room_code = "SOLO"
        st.session_state.player_name = "Defender"

    st.session_state.target = st.text_area(
        "Target Organization",
        placeholder="Example: Mid-size fintech, 500 employees, Okta with SMS fallback, public GitHub, remote workforce",
        height=150,
        value=st.session_state.target
    ).strip()

    if st.button("Start New Simulation", type="primary", use_container_width=True):
        if not st.session_state.target:
            st.error("Please describe the target organization.")
        else:
            st.session_state.game_id = datetime.now().strftime("%Y%m%d-%H%M%S")
            st.session_state.history = []
            st.session_state.score = 100
            st.session_state.stage = 0
            st.success("Attack simulation started!")
            st.rerun()

# ============================
# Main Game Logic
# ============================
if st.session_state.game_id:
    st.markdown(
        f"**Room:** `{st.session_state.room_code}` │ "
        f"**Player:** {st.session_state.player_name} │ "
        f"**Defense Score:** `{st.session_state.score}/100`"
    )

    system_prompt = f"""
You are an elite cybercriminal attacking this organization:
{st.session_state.target}

Be realistic, creative, and follow real-world MITRE ATT&CK TTPs.
Never provide exploit code — only high-level tactics.
After every defender action, explain impact on timeline, cost, detection risk, and success chance.

End your response with exactly this format:
---
1. First attacker option
2. Second attacker option
3. Third attacker option
"""

    # First attacker message
    if not st.session_state.history:
        with st.chat_message("assistant"):
            with st.spinner("Performing reconnaissance..."):
                resp = query_grok([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Begin the attack campaign from reconnaissance."}
                ], temperature=0.8)
                st.session_state.history.append({"role": "assistant", "content": resp})
                st.markdown(resp)

    # Show conversation history
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Extract the three attacker choices
    last_attacker_msg = None
    for msg in reversed(st.session_state.history):
        if msg["role"] == "assistant":
            last_attacker_msg = msg["content"]
            break

    if last_attacker_msg and "---" in last_attacker_msg:
        choices_text = last_attacker_msg.split("---")[-1]
        choices = []
        for line in choices_text.split("\n"):
            line = line.strip()
            if line and line[0].isdigit() and "." in line:
                choice = line.split(".", 1)[1].strip()
                choices.append(choice)

        if len(choices) >= 3:
            st.markdown("### Your move — How do you respond as defender?")
            cols = st.columns(3)
            for i, choice in enumerate(choices[:3]):
                if cols[i].button(choice, key=f"choice_{st.session_state.stage}_{i}", use_container_width=True):
                    # Defender's action
                    with st.chat_message("user"):
                        st.markdown(f"**Defender action:** {choice}")

                    # Attacker reacts
                    with st.chat_message("assistant"):
                        with st.spinner("Attacker adapting..."):
                            prompt = f"Defender responded with: {choice}\nContinue the campaign realistically and end with --- followed by 3 new options."
                            messages = [{"role": "system", "content": system_prompt}]
                            messages += [{"role": h["role"], "content": h["content"]} for h in st.session_state.history]
                            messages.append({"role": "user", "content": prompt})

                            resp = query_grok(messages, temperature=0.85)

                            # Simple scoring
                            r = resp.lower()
                            if any(w in r for w in ["detected","blocked","failed","delayed","mitigated"]):
                                st.session_state.score = min(100, st.session_state.score + 15)
                            if any(w in r for w in ["success","compromised","persistence","exfiltrated","encrypted","ransom"]):
                                st.session_state.score = max(0, st.session_state.score - 20)

                            st.session_state.history.append({"role": "user", "content": f"Defender: {choice}"})
                            st.session_state.history.append({"role": "assistant", "content": resp})
                            st.session_state.stage += 1
                            st.rerun()

    # Game Over
    if st.session_state.score <= 30:
        st.error("BREACH COMPLETE — The attacker won.")
        st.balloons()
        if st.button("Start New Game", type="primary"):
            st.session_state.game_id = None
            st.session_state.history = []
            st.session_state.score = 100
            st.session_state.stage = 0
            st.rerun()

else:
    st.info("Set up your target in the sidebar → Click **Start New Simulation**")
   

st.caption("Threat Actor Empathy Simulator — Powered by Grok xAI")