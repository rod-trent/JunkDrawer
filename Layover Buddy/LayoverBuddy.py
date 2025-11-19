import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI
import datetime

load_dotenv()

# Configure Grok client (OpenAI-compatible)
client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url=os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
)

# Page config
st.set_page_config(
    page_title="Airport Layover Buddy",
    page_icon="✈️",
    layout="centered"
)

st.title("✈️ Airport Layover Buddy")
st.markdown("Tell me your layover city and how much time you have — I’ll build the perfect itinerary in seconds. Powered by Grok (xAI).")

# Sidebar inputs
with st.sidebar:
    st.header("Layover Details")
    
    city = st.text_input("Layover City (e.g., Singapore, Istanbul, Doha)", placeholder="Tokyo")
    airport_code = st.text_input("Airport Code (optional, helps accuracy)", placeholder="HND")
    
    layover_hours = st.slider("Layover Duration", 2, 24, 6, help="Minimum realistic layover is ~2h")
    layover_minutes = st.slider("Extra Minutes", 0, 59, 0)
    total_minutes = layover_hours * 60 + layover_minutes
    
    delay_minutes = st.number_input("Flight Delay Adjustment (± minutes)", value=0, step=5,
                                    help="Positive = delayed (more time), negative = earlier departure")
    
    adjusted_minutes = total_minutes + delay_minutes
    
    preferences = st.multiselect(
        "Priorities (optional)",
        ["Food & Restaurants", "Iconic Sights", "Lounge / Nap", "Shopping", "Quick & Relaxed", "Adventurous"],
        default=["Food & Restaurants", "Iconic Sights", "Lounge / Nap"]
    )
    
    travel_style = st.radio("Travel Style", ["Budget", "Comfort", "Luxury"], horizontal=True)

# Main app
if st.button("🚀 Generate Optimized Itinerary", type="primary", use_container_width=True):
    if not city:
        st.error("Please enter a layover city.")
    else:
        # Format time nicely
        hours = adjusted_minutes // 60
        mins = adjusted_minutes % 60
        time_str = f"{hours}h {mins}m" if mins else f"{hours}h"
        
        with st.status("Asking Grok to maximize your layover…") as status:
            st.write("Crafting the perfect plan…")
            
            prompt = f"""
You are an expert airport layover optimizer.
User has a layover in {city.strip()} {'(airport: ' + airport_code.strip() + ')' if airport_code else ''}.
They have exactly {adjusted_minutes} minutes ({time_str}) of usable time at the airport/city.
Travel style: {travel_style}.
Top priorities: {', '.join(preferences) if preferences else 'balanced'}.

Rules:
- Account for immigration, security, transport to/from city center (train/taxi/metro times and costs).
- Include exact lounge names if they have access (Priority Pass, credit card, airline status unknown — list best options).
- Recommend 1–3 food options (street food → Michelin depending on style).
- Include quick iconic sights or experiences possible in the timeframe.
- Suggest nap/power-nap spots or capsules if needed.
- Always leave a safe buffer (at least 90–120 min before boarding).
- Format as a beautiful timed itinerary with emojis and bold times.
- If delay made it too short (<3h), suggest only airport options.

Current date context: November 2025. Use latest known info.
Respond in markdown.
"""

            stream = client.chat.completions.create(
                model="grok-4",          # or "grok-3" if you don't have Grok-4 access
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                stream=True
            )

            # Streaming response
            response_placeholder = st.empty()
            full_response = ""
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            status.update(label="Itinerary ready!", state="complete", expanded=False)

# Footer
st.caption("Built with ❤️ using Grok (xAI) + Streamlit | Delay updates are instant — just change the slider and hit Generate again.")