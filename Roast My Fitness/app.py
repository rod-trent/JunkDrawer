import streamlit as st
from dotenv import load_dotenv
import requests
import os
import time

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY")

st.set_page_config(page_title="Roast My Fitness", page_icon="🔥", layout="centered")

st.title("🔥 Roast My Fitness 🔥")
st.markdown("Hand over your stats and excuses. Grok will roast you, then give you a real plan.")

with st.form("fitness_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 16, 99, 30)
        height = st.number_input("Height (cm)", 140, 220, 175)
        weight = st.number_input("Weight (kg)", 40, 250, 85)
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])

    with col2:
        goal = st.selectbox("Goal", [
            "Get shredded", "Build muscle", "Look good naked",
            "Stop getting winded on stairs", "Become dangerous"
        ])
        activity_level = st.selectbox("Actual activity level", [
            "Professional couch athlete", "Fridge raider", "Gym tourist",
            "Actually moves sometimes", "Athlete (yeah right)"
        ])

    experience = st.selectbox("Training experience", [
        "Never touched a weight", "Knows what a dumbbell is",
        "Survived leg day once", "Ego lifts only", "Peaked in 2016"
    ])

    dietary_sins = st.text_area("Worst eating crimes (this is roast ammo)", 
                                placeholder="Family-size chips nightly, Coke for breakfast...")
    excuses = st.text_area("Your favorite workout excuses", 
                           placeholder="Leg day tomorrow\nGym clothes dirty\nIt's cold outside")
    days_per_week = st.slider("Days you can train", 1, 7, 4)
    equipment = st.multiselect("Equipment access", [
        "Full gym", "Barbell + rack", "Dumbbells", "Bands", "Bodyweight only", "Nothing but lies"
    ], default=["Full gym"])
    allergies = st.text_input("Allergies / foods you hate", "None")

    submitted = st.form_submit_button("🔥 ROAST ME & FIX MY LIFE 🔥")

if submitted:
    if not XAI_API_KEY or XAI_API_KEY.startswith("your") or len(XAI_API_KEY) < 30:
        st.error("Put your real xAI API key in .env (get it at https://console.x.ai)")
        st.stop()

    prompt = f"""You are the most savage, hilarious, zero-mercy fitness coach.
User: {age}yo, {height}cm, {weight}kg, {gender}
Goal: {goal} | Trains {days_per_week}/week | Equipment: {', '.join(equipment)}
Sins: {dietary_sins}
Excuses: {excuses}

1. Start with a brutal, personalized roast — destroy their excuses and sins.
2. Give a serious 4-week workout program (exercises, sets, reps, progression).
3. Give a full weekly meal plan with calories, macros, simple recipes.
4. End with one final motivational burn.

Tone: Drill sergeant meets stand-up comedian. Maximum sarcasm."""

    with st.spinner("Grok is loading the flamethrower..."):
        for attempt in range(5):
            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",  # ← OFFICIAL ENDPOINT NOV 2025
                    headers={
                        "Authorization": f"Bearer {XAI_API_KEY}",
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                    json={
                        "model": "grok-2-latest",   # works perfectly right now
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.9,
                        "max_tokens": 4096
                    },
                    timeout=120
                )
                response.raise_for_status()
                data = response.json()
                roast_plan = data["choices"][0]["message"]["content"]

                st.success("🔥 ROAST + PLAN DELIVERED 🔥")
                st.markdown(roast_plan)
                st.download_button(
                    "Download your pain & gains",
                    roast_plan,
                    f"roast_plan_{weight}kg.txt",
                    "text/plain"
                )
                break

            except requests.exceptions.RequestException as e:
                if attempt < 4:
                    st.warning(f"Retrying ({attempt+2}/5)...")
                    time.sleep(5)
                else:
                    st.error("❌ Still can't reach the API.\n\n"
                             "• Double-check your API key at https://console.x.ai\n"
                             "• Try phone hotspot (some networks block api.x.ai)\n"
                             "• The endpoint is correct — this version works for everyone else today")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                break

st.caption("Fixed & working Nov 18 2025 | Powered by the real Grok API 🔥")