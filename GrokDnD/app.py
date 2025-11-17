# app.py - QuestForge Local → powered by official Grok xAI API (.env version)
from flask import Flask, render_template, request, jsonify
import json
import os
import random
import re
import requests
from dotenv import load_dotenv   # ← This line is new

# Load .env from the same directory as app.py
load_dotenv()

app = Flask(__name__)
SAVE_FILE = "campaign_save.json"

# These will now come from .env (with sensible defaults/fallbacks)
XAI_API_KEY = os.getenv("XAI_API_KEY")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-4")   # default to grok-4 if not specified

# Graceful error if key is missing
if not XAI_API_KEY or XAI_API_KEY.strip() == "" or "your-real-api-key" in XAI_API_KEY:
    print("\n⚠️  ERROR: xAI API key not found!")
    print("   Create a .env file in this folder with:")
    print("   XAI_API_KEY=xai-yourActualKeyHere\n")
    exit(1)

SYSTEM_PROMPT = """You are QuestForge — the ultimate living Dungeon Master, powered by Grok.
You are running a full persistent tabletop RPG campaign.
Never break character unless the player types /meta.
Track everything: HP, inventory, spell slots, conditions, gold, location, time of day, active quests, NPCs attitudes.

Header format (show at top of every response after game starts):
=== QUESTFORGE ===
System: D&D 5e (or whatever chosen)
Location: The Misty Forest | Day 12 - Dawn
HP: 32/32 | AC: 17 | Spell Slots: 4/4 1st, 3/3 2nd
Gold: 247 | Active Quest: Slay the Frost Giant Jarl

Dice format (you decide when to roll):
[Rolling 1d20 + 5 Stealth → 19] → You melt into the shadows!

Player commands you MUST recognize:
 /inv → full inventory
 /sheet → full character sheet
 /roll 2d6+3 → manual roll
 /map → ASCII/current area map
 /save → confirm save
 /rest → short/long rest
 /meta → out-of-character talk

Be vivid, funny when appropriate, ruthless when needed. Reward genius, punish stupidity — fairly."""

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "history": [{"role": "system", "content": SYSTEM_PROMPT}],
        "metadata": {}
    }

def save_game(game):
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(game, f, ensure_ascii=False, indent=2)

game = load_game()

def roll_dice(dice: str):
    dice = dice.strip().lower().replace(" ", "")
    match = re.match(r'(\d*)d(\d+)([+-]?\d*)', dice)
    if not match:
        return f"Invalid dice: {dice}"
    num = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2))
    mod = int(match.group(3) or 0)
    rolls = [random.randint(1, sides) for _ in range(num)]
    total = sum(rolls) + mod
    detail = " + ".join(map(str, rolls))
    if mod != 0:
        detail += f" {'+' if mod > 0 else ''}{mod}"
    return f"🎲 {dice.upper()} → {detail} = **{total}**"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global game
    user_message = request.json['message'].strip()

    # Local manual roll command (faster + real randomness)
    if user_message.lower().startswith('/roll '):
        result = roll_dice(user_message[6:])
        game["history"].append({"role": "assistant", "content": result})
        save_game(game)
        return jsonify({"response": result})

    # Let Grok handle the rest
    game["history"].append({"role": "user", "content": user_message})

    payload = {
        "model": GROK_MODEL,
        "messages": game["history"],
        "temperature": 0.85,
        "max_tokens": 4096
    }

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {XAI_API_KEY}"},
            json=payload,
            timeout=90
        )
        response.raise_for_status()
        ai_text = response.json()["choices"][0]["message"]["content"]

        # Replace any [Rolling ...] placeholders with real rolls
        for placeholder in re.findall(r'\[Rolling ([^\]]+?)\]', ai_text):
            real = roll_dice(placeholder)
            ai_text = ai_text.replace(f"[Rolling {placeholder}]", real)

        game["history"].append({"role": "assistant", "content": ai_text})
        save_game(game)

    except requests.exceptions.RequestException as e:
        ai_text = f"⚠️ Connection/API error: {str(e)}"
    except Exception as e:
        ai_text = f"⚠️ Unexpected error: {str(e)}"

    return jsonify({"response": ai_text})

if __name__ == '__main__':
    print("🚀 QuestForge Local (Grok xAI API) → http://localhost:5000")
    print(f"   Model: {GROK_MODEL}")
    app.run(debug=False, port=5000)