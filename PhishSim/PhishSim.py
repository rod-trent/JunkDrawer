import streamlit as st
import requests
import json
import random
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")

# xAI API endpoint
API_URL = "https://api.x.ai/v1/chat/completions"

# Updated model name (grok-beta was deprecated on 2025-09-15)
MODEL_NAME = "grok-3"  # Recommended replacement; if you have access to Grok 4, change to "grok-4"

# Function to generate message using xAI API
def generate_message(is_phishing, industry, difficulty):
    if is_phishing:
        prompt = f"Generate a realistic phishing {difficulty} email or message in the {industry} industry. Make it deceptive and include common phishing elements like urgent requests, fake links, or attachments. Do not indicate it's phishing."
    else:
        prompt = f"Generate a legitimate {difficulty} email or message in the {industry} industry. Make it normal and professional without any suspicious elements."
    
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error generating message: {response.status_code} - {response.text}"

# Function to get feedback using xAI API
def get_feedback(message, is_phishing, user_guess):
    prompt = f"The following message is {'phishing' if is_phishing else 'legitimate'}: '{message}'. The user guessed it was {'phishing' if user_guess else 'legitimate'}. Provide detailed feedback on why it's phishing or not, and tips to spot similar ones."
    
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error getting feedback: {response.status_code} - {response.text}"

# User data file
USER_DATA_FILE = "user_data.json"

# Load user data
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Save user data
def save_user_data(user_data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(user_data, f)

# Leaderboard file
LEADERBOARD_FILE = "leaderboard.json"

# Load leaderboard
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return []

# Save leaderboard
def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f)

# Level system
def get_level(score):
    if score < 10:
        return "Beginner", "🟢"
    elif score < 25:
        return "Intermediate", "🔵"
    elif score < 50:
        return "Advanced", "🟣"
    elif score < 100:
        return "Expert", "🔴"
    else:
        return "Master", "⚫"

# Comprehensive Badges
BADGES = {
    "First Win": "Correctly identify your first phishing attempt.",
    "Streak Master": "Achieve a streak of 5 correct answers in a row.",
    "Unbreakable": "Achieve a streak of 10 correct answers in a row.",
    "Legendary Streak": "Achieve a streak of 20 correct answers in a row.",
    "Industry Expert": "Score 10 correct answers in a single industry.",
    "All-Rounder": "Become Industry Expert in 3 different industries.",
    "Daily Challenger": "Log in and play on a new day.",
    "Week Warrior": "Play on 7 consecutive days.",
    "Hard Mode Hero": "Correctly identify 10 Hard difficulty messages.",
    "Perfect Round": "Get 10 correct answers in a single session without any mistakes.",
    "Phishing Hunter": "Correctly flag 50 phishing emails.",
    "Safe Keeper": "Correctly identify 50 legitimate emails.",
    "Graduated": "Reach the Master level (100+ points).",
}

# Streamlit app
st.title("🔒 AI-Powered Phishing Simulator and Trainer")

# User login
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.markdown("### Supply a username to track progress, badges, and leaderboard")
    user_name = st.text_input("Enter your username:")
    if st.button("Continue"):
        if user_name.strip():
            user_data = load_user_data()
            if user_name not in user_data:
                user_data[user_name] = {
                    "score": 0,
                    "streak": 0,
                    "max_streak": 0,
                    "badges": [],
                    "industry_scores": {},  # {industry: correct_count}
                    "last_login": None,
                    "consecutive_days": 0,
                    "hard_correct": 0,
                    "phishing_correct": 0,
                    "legit_correct": 0,
                    "session_correct": 0,
                    "session_mistakes": 0,
                }
            st.session_state.user = user_name
            
            # Load persistent data into session state
            u = user_data[user_name]
            st.session_state.score = u["score"]
            st.session_state.streak = u["streak"]
            st.session_state.badges = u["badges"][:]
            st.session_state.industry_scores = u.get("industry_scores", {})
            st.session_state.hard_correct = u.get("hard_correct", 0)
            st.session_state.phishing_correct = u.get("phishing_correct", 0)
            st.session_state.legit_correct = u.get("legit_correct", 0)
            # Session-specific (reset on new login)
            st.session_state.session_correct = 0
            st.session_state.session_mistakes = 0
            
            save_user_data(user_data)
            st.rerun()
        else:
            st.error("Please enter a username.")
else:
    st.success(f"Welcome back, {st.session_state.user}!")

# Update daily login and consecutive days
if st.session_state.user:
    user_data = load_user_data()
    u = user_data[st.session_state.user]
    today = datetime.now().date()
    
    if u["last_login"] is None or u["last_login"] != str(today):
        last_login_date = datetime.strptime(u["last_login"], "%Y-%m-%d").date() if u["last_login"] else None
        if last_login_date == today - timedelta(days=1):
            u["consecutive_days"] += 1
        elif last_login_date != today:
            u["consecutive_days"] = 1  # New streak
        
        u["last_login"] = str(today)
        
        # Award Daily Challenger only once ever
        if "Daily Challenger" not in u["badges"]:
            u["badges"].append("Daily Challenger")
            st.session_state.badges.append("Daily Challenger")
            st.balloons()
            st.success(f"🏆 Badge Earned: **Daily Challenger**")
        
        save_user_data(user_data)

# Sidebar
st.sidebar.header("Settings")
industry = st.sidebar.selectbox("Industry", ["General", "Finance", "Healthcare", "Retail", "Tech"])
difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
st.sidebar.markdown("---")
if st.sidebar.button("Training Modules"):
    st.session_state.page = "training"
if st.sidebar.button("Leaderboard"):
    st.session_state.page = "leaderboard"
if st.sidebar.button("My Profile & Badges"):
    st.session_state.page = "profile"

# Session state defaults
if "page" not in st.session_state:
    st.session_state.page = "main"
if "message" not in st.session_state:
    st.session_state.message = None
if "is_phishing" not in st.session_state:
    st.session_state.is_phishing = None
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "round" not in st.session_state:
    st.session_state.round = 0

# Main page
if st.session_state.page == "main" and st.session_state.user:
    level_name, level_emoji = get_level(st.session_state.score)
    st.markdown(f"**Level:** {level_emoji} {level_name} | **Score:** {st.session_state.score} | **Streak:** 🔥 {st.session_state.streak}")

    if st.button("🎯 Generate New Message"):
        st.session_state.is_phishing = random.choice([True, False])
        st.session_state.message = generate_message(st.session_state.is_phishing, industry, difficulty.lower())
        st.session_state.feedback = None
        st.session_state.round += 1

    if st.session_state.message:
        st.subheader("Incoming Message:")
        st.text_area("Message", st.session_state.message, height=250, label_visibility="collapsed")
        
        col1, col2 = st.columns(2)
        user_guess = None
        
        if col1.button("🚨 This is Phishing", use_container_width=True):
            user_guess = True
        if col2.button("✅ This is Legitimate", use_container_width=True):
            user_guess = False

        if user_guess is not None:
            correct = (st.session_state.is_phishing == user_guess)
            user_data = load_user_data()
            u = user_data[st.session_state.user]
            new_badges = []

            if correct:
                st.success("🎉 Correct!")
                st.session_state.score += 1
                u["score"] += 1
                st.session_state.streak += 1
                u["streak"] += 1
                if u["streak"] > u.get("max_streak", 0):
                    u["max_streak"] = u["streak"]

                st.session_state.session_correct += 1
                u["session_correct"] = st.session_state.session_correct

                # Counters
                u["industry_scores"][industry] = u["industry_scores"].get(industry, 0) + 1
                st.session_state.industry_scores = u["industry_scores"]

                if difficulty == "Hard":
                    u["hard_correct"] += 1
                    st.session_state.hard_correct = u["hard_correct"]

                if st.session_state.is_phishing:
                    u["phishing_correct"] += 1
                    st.session_state.phishing_correct = u["phishing_correct"]
                else:
                    u["legit_correct"] += 1
                    st.session_state.legit_correct = u["legit_correct"]

                # === Robust Badge Checks ===
                if "First Win" not in u["badges"] and st.session_state.score >= 1:
                    new_badges.append("First Win")

                if st.session_state.streak >= 5 and "Streak Master" not in u["badges"]:
                    new_badges.append("Streak Master")
                if st.session_state.streak >= 10 and "Unbreakable" not in u["badges"]:
                    new_badges.append("Unbreakable")
                if st.session_state.streak >= 20 and "Legendary Streak" not in u["badges"]:
                    new_badges.append("Legendary Streak")

                if u["industry_scores"].get(industry, 0) >= 10 and "Industry Expert" not in u["badges"]:
                    new_badges.append("Industry Expert")

                expert_count = sum(1 for v in u["industry_scores"].values() if v >= 10)
                if expert_count >= 3 and "All-Rounder" not in u["badges"]:
                    new_badges.append("All-Rounder")

                if u["consecutive_days"] >= 7 and "Week Warrior" not in u["badges"]:
                    new_badges.append("Week Warrior")

                if u["hard_correct"] >= 10 and "Hard Mode Hero" not in u["badges"]:
                    new_badges.append("Hard Mode Hero")

                if st.session_state.session_correct >= 10 and st.session_state.session_mistakes == 0 and "Perfect Round" not in u["badges"]:
                    new_badges.append("Perfect Round")

                if u["phishing_correct"] >= 50 and "Phishing Hunter" not in u["badges"]:
                    new_badges.append("Phishing Hunter")

                if u["legit_correct"] >= 50 and "Safe Keeper" not in u["badges"]:
                    new_badges.append("Safe Keeper")

                if st.session_state.score >= 100 and "Graduated" not in u["badges"]:
                    new_badges.append("Graduated")

            else:
                st.error("❌ Incorrect")
                st.session_state.streak = 0
                u["streak"] = 0
                st.session_state.session_mistakes += 1
                u["session_mistakes"] = st.session_state.session_mistakes

            # Award new badges
            for badge in new_badges:
                if badge not in u["badges"]:
                    u["badges"].append(badge)
                    st.session_state.badges.append(badge)
                    st.balloons()
                    st.success(f"🏆 New Badge Earned: **{badge}** — {BADGES[badge]}")

            st.session_state.feedback = get_feedback(st.session_state.message, st.session_state.is_phishing, user_guess)
            save_user_data(user_data)
            st.rerun()

        if st.session_state.feedback:
            st.subheader("Detailed Feedback")
            st.write(st.session_state.feedback)

    # Real-time email analyzer
    st.markdown("---")
    st.subheader("📧 Real-Time Email Analyzer")
    email_text = st.text_area("Paste a suspicious email here for instant analysis:")
    if st.button("Analyze Email"):
        with st.spinner("Analyzing..."):
            prompt = f"Analyze the following email and determine if it's phishing. Explain signs and give a confidence score: '{email_text}'"
            headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
            data = {"model": MODEL_NAME, "messages": [{"role": "user", "content": prompt}], "temperature": 0.5}
            response = requests.post(API_URL, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                st.write(response.json()["choices"][0]["message"]["content"])
            else:
                st.error(f"Analysis failed: {response.status_code} - {response.text}")

# Training page
elif st.session_state.page == "training":
    st.subheader("📚 Training Modules")
    st.write("### Common Phishing Signs")
    st.write("- Urgency or threats")
    st.write("- Unexpected requests for credentials")
    st.write("- Mismatched or suspicious links")
    st.write("- Grammar/spelling errors")
    st.write("- Generic greetings")
    if st.button("Back"):
        st.session_state.page = "main"
        st.rerun()

# Leaderboard page
elif st.session_state.page == "leaderboard":
    st.subheader("🏆 Global Leaderboard (Top 10)")
    leaderboard = load_leaderboard()
    if leaderboard:
        df = pd.DataFrame(leaderboard)
        st.table(df)
    else:
        st.info("No scores submitted yet.")
    if st.button("Back"):
        st.session_state.page = "main"
        st.rerun()

# Profile page
elif st.session_state.page == "profile" and st.session_state.user:
    st.subheader(f"👤 Profile: {st.session_state.user}")
    level_name, level_emoji = get_level(st.session_state.score)
    st.write(f"**Level:** {level_emoji} {level_name}")
    st.write(f"**Total Score:** {st.session_state.score}")
    st.write(f"**Best Streak:** {load_user_data()[st.session_state.user].get('max_streak', 0)}")
    st.write(f"**Consecutive Days:** {load_user_data()[st.session_state.user]['consecutive_days']}")

    st.markdown("### 🏆 Your Badges")
    user_badges = load_user_data()[st.session_state.user]["badges"]
    if user_badges:
        cols = st.columns(4)
        for i, badge in enumerate(sorted(user_badges)):
            with cols[i % 4]:
                st.markdown(f"**{badge}**  \n{BADGES.get(badge, '')}")
    else:
        st.info("No badges yet — keep playing!")

    if st.button("Back"):
        st.session_state.page = "main"
        st.rerun()

else:
    st.info("Supply a username to start training.")