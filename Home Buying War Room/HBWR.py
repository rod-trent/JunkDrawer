import streamlit as st
import openai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

GROK_KEY = os.getenv("GROK_API_KEY")
if not GROK_KEY:
    st.error("Add GROK_API_KEY to your .env file → https://console.x.ai")
    st.stop()

client = openai.OpenAI(api_key=GROK_KEY, base_url="https://api.x.ai/v1")

st.set_page_config(page_title="Home Buying War Room", layout="wide", page_icon="house")
st.title("Home Buying War Room")
st.markdown("### 100% Grok-4 • Deep Due Diligence • 3 Killer Questions • No MLS Drama")

address = st.text_input(
    "Property Address (any format)",
    placeholder="123 Main St, Austin TX • etc."
)

launch = st.button("LAUNCH WAR ROOM", type="primary", use_container_width=True)

if launch:
    if not address.strip():
        st.error("Enter an address")
        st.stop()

    with st.spinner("Grok-4 is running deep due diligence and arming you with killer questions..."):
        prompt = f"""
Property address: {address}

Using your latest knowledge (November 2025), analyze this exact location and return ONLY valid JSON with these keys:

{{
  "flood_risk": "Low - outside any FEMA flood zone",
  "crime_level": "38% below national average",
  "school_ratings": "Elementary: 9/10 • Middle: 9/10 • High: 10/10 (GreatSchools)",
  "future_development": "New mixed-use project 1.2mi east opening 2026; highway expansion 0.8mi north by 2028",
  "top_red_flags": "1. Backyard abuts busy road\\n2. Original 2005 HVAC\\n3. Minor foundation note 2019",
  "killer_questions": [
    "The HVAC is original from 2005 — has it been replaced or serviced recently?",
    "With the backyard facing a busy road, how noticeable is traffic noise inside?",
    "Regarding the 2019 foundation inspection note, can you provide the full report?"
  ]
}}
"""

        resp = client.chat.completions.create(
            model="grok-4",              # Switched to grok-4 for advanced reasoning
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )

        raw = resp.choices[0].message.content.strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            raw = match.group(0)

        try:
            data = json.loads(raw)
        except:
            st.error("Grok returned invalid JSON. Raw output:")
            st.code(raw)
            st.stop()

    # ===================== PURE GROK DISPLAY =====================
    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.success(f"War Room Complete — {address}")
        st.subheader("Grok-4 Due Diligence")
        st.write(f"**Flood Risk** → {data.get('flood_risk', 'N/A')}")
        st.write(f"**Crime Level** → {data.get('crime_level', 'N/A')}")
        st.write(f"**Schools** → {data.get('school_ratings', 'N/A')}")
        st.write(f"**Future Development** → {data.get('future_development', 'N/A')}")
        st.write(f"**Top Red Flags**\n{data.get('top_red_flags', 'None detected')}")

    with col2:
        st.subheader("Your 3 Killer Questions")
        for i, q in enumerate(data.get("killer_questions", [])[:3], 1):
            st.error(f"**Question #{i}**")
            st.markdown(f"> {q}")
            st.divider()

    st.balloons()
    st.success("You are now lethally armed, @rodtrent. Go dominate the negotiation. 🔥")

else:
    st.info("Enter any U.S. address → hit **LAUNCH WAR ROOM** → win.")
    st.caption("100% Grok-4 • No external APIs • Frontier intelligence")