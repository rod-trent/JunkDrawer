# 🔥 Roast My Fitness: A Savage AI Fitness Coach with Grok That Will Destroy Your Excuses (and Then Fix You)

Look, we've all been there. You download yet another fitness app, input your stats, and get some bland, cookie-cutter plan that sounds like it was written by a robot who’s never seen a donut. "Eat salad. Do squats. Be better." Yawn.

But what if the robot *actually* roasted you first—like a drill sergeant crossed with a stand-up comedian who’s seen your browser history?

That’s exactly what I built this weekend: **Roast My Fitness** — a free Streamlit app powered by the real xAI Grok API that takes your pathetic stats, your worst eating crimes, and your laundry list of excuses… and verbally annihilates you before handing over a legit 4-week training program + meal plan.

### Why I Built This (Instead of Doing Leg Day)

I’m tired of polite fitness advice.

- Normal apps: “You can do it! 🌟”
- Grok in this app: “You’re 85 kg of broken dreams and family-size chip bags. The only thing you’ve been lifting is the remote. Congrats, you peaked in high school.”

It’s the motivational kick in the butt we all secretly need.

And because it’s Grok, the roast is *personalized*. You confess that Coke is your breakfast? It will remember. You say your favorite excuse is “gym clothes are dirty”? It will never let you forget.

Then—because we’re not monsters—it flips the switch and gives you:

- A brutal but actually good 4-week workout program (sets, reps, progression)
- A full weekly meal plan with macros, calories, and dead-simple recipes
- One final motivational burn to send you off crying… into the squat rack

### How It Works (The Fun Part)

1. You fill out the form with your age, height, weight, goal (“Look good naked” is a popular choice), activity level (“Professional couch athlete”), training experience, equipment, and—most importantly—your **dietary sins** and **excuses**.
2. Hit “🔥 ROAST ME & FIX MY LIFE 🔥”
3. Grok loads the flamethrower and delivers a response that will make you laugh, cry, and finally delete Uber Eats.

Example output snippet from a real user (names changed to protect the guilty):

> “Listen up, 32-year-old human landfill. At 178 cm and 92 kg you’re basically a walking advertisement for ‘what not to do’. Your ‘activity level’? Fridge raider. Bro, the only raid you’re doing is on the leftover pizza at 2 AM. And Coke for breakfast? That’s not a meal, that’s a war crime…  
> …Anyway, here’s your 4-week program, you absolute disaster. Follow it or stay shaped like a Teletubby.”

It’s savage. It’s hilarious. And the plans are legitimately solid because Grok knows its stuff.

### The Tech (For the Nerds)

- **Streamlit** — because who has time for React when you just want to roast people?
- **xAI Grok API** — using the official endpoint (`https://api.x.ai/v1/chat/completions`) and the latest model available.
- Your xAI API key (grab one free at https://console.x.ai — they give credits to start)
- A little retry logic because sometimes the API gets excited and needs a nap.

The whole thing is ~150 lines. I literally built it in an afternoon while procrastinating my own workout.

### Try It Right Now (It’s Free)

Deployed and live: https://github.com/rod-trent/JunkDrawer/tree/main/Roast%20My%20Fitness  
(If Hugging Face Spaces or Streamlit Cloud hugs it to death from traffic, I’ll spin up a better host.)

Warning: This app will hurt feelings. Side effects may include:
- Sudden urge to meal prep
- Deleting snack apps
- Actual gym attendance
- Laughing so hard you snort protein shake

### The Code (Steal It, Improve It, Make It Meaner)

Here’s the full `app.py` — copy, paste, add your API key, deploy it yourself:

```python
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
```

(Full code in the gist/repo linked below if you want the pretty version.)

https://github.com/rod-trent/JunkDrawer/tree/main/Roast%20My%20Fitness 

### Final Burn

If you’re still reading this instead of opening the app and getting roasted… well, that tells me everything I need to know about your discipline.

Go get destroyed. Then get jacked.

🔥 See you in the gym (or on the couch crying — your choice).

— Your friendly neighborhood AI builder who definitely didn’t skip arms this week

P.S. Share your best roasts in the replies. I need new material. 😈
