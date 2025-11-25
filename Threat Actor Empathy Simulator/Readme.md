# Threat Actor Empathy Simulator – Now Powered by Grok

A new open-source tool that lets you **think exactly like an elite attacker** – and instantly see how your defenses hold up (or crumble).

I just released the **Threat Actor Empathy Simulator** – a Streamlit app that turns red-team thinking into an interactive, real-time game using **Grok (xAI)** as the adversary brain.

Live code & permanent home:  
https://github.com/rod-trent/JunkDrawer/tree/main/Threat%20Actor%20Empathy%20Simulator

## What It Is

It’s a defensive exercise disguised as a game.

You describe a target organization (your own, a client’s, or a fictional one).  
Grok becomes a highly realistic, creative, MITRE ATT&CK-aware threat actor.  
It starts from reconnaissance and continuously adapts to every defensive move you make.

At each turn the attacker gives you **exactly three realistic next moves**. You pick the one you would actually detect or block in real life. Grok then tells you how the attacker pivots, what delays or costs they incur, whether they get caught, or if they quietly succeed.

You get a running **Defense Score (0–100)**. When it drops to ≤30, the attacker wins and you get the dreaded “BREACH COMPLETE” screen (with balloons, because attackers celebrate).

## Why This Is Actually Valuable

Most tabletop or red-team exercises suffer from two problems:

1. The facilitator runs out of creativity after the third move.
2. Defenders stay in “blue fantasy land” – they assume every control works perfectly.

This tool eliminates both.

- Grok never gets tired and has up-to-date TTP knowledge (including 2024–2025 trends).
- It forces defenders to commit to a choice and see realistic outcomes.
- You experience the **attacker’s cost/benefit calculus** in real time: “MFA with SMS fallback? Cool, I’ll just vishing the helpdesk or wait for the Sim-Swap campaign I already started.”
- Perfect for security awareness workshops, incident response tabletops, architecture reviews, or just personal growth.

I’ve already seen defenders go from “We have Okta, we’re fine” to “Wait… we need WebAuthn and number matching yesterday” in under 15 minutes.

## Features

- Solo or Multiplayer (team exercise) mode with room codes
- Persistent session state – come back later, keep playing the same campaign
- Realistic scoring (defensive wins add points, compromises subtract)
- Strictly high-level TTPs – no exploit code is ever shown
- Fully local – your API key and target description never leave your machine

## Requirements

- Python 3.9+
- A Grok API key (get one at https://x.ai/api)
- About 2 minutes of setup

## How to Run It Locally (2-minute setup)

```bash
# 1. Clone the repo (or just download the two files)
git clone https://github.com/rod-trent/JunkDrawer.git
cd "JunkDrawer/Threat Actor Empathy Simulator"

# 2. Create virtual env (optional but recommended)
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# 3. Install requirements
pip install streamlit python-dotenv requests

# 4. Create your .env file in the same folder
echo "GROK_API_KEY=your_grok_api_key_here" > .env

# 5. Run it
streamlit run taes.py
```

The app will open in your browser (usually http://localhost:8501).

## How to Play

1. In the sidebar, describe your target as realistically as possible  
   Example:  
   “Mid-size US fintech, 800 employees, Okta with SMS fallback for MFA, public GitHub repos, remote-first workforce, CrowdStrike EDR, Microsoft 365 E5 license but no Defender for Identity, uses Slack and Zoom”

2. Choose Solo or Multiplayer → Click **Start New Simulation**

3. Grok begins reconnaissance and gives you three realistic next attacker moves.

4. Pick the one you believe your team would actually catch or block.

5. Watch the attacker adapt (or succeed). Repeat until you either win by driving the attacker’s ROI to zero or lose when your score drops too low.

Pro tip: the more honest and detailed your target description, the scarier (and more valuable) the simulation becomes.

## Multiplayer / Workshop Mode

- Everyone joins the same Room Code
- Take turns being the defender or just discuss as a group
- Great for security team off-sites or client workshops

## Why Grok Instead of Other Models?

I tested GPT-4o, Claude 3.5, and Grok.  
Grok won by a mile on two dimensions that matter for red-teaming:

1. Creativity & realism of TTP chaining
2. Willingness to be evil (other models often refuse or water down attacks)

Grok happily simulates supply-chain attacks via malicious PyPI packages, living-off-the-land with Kerberos ticket games, or long-term subversion of backup systems – exactly what elite actors do.

## Go Break Your Defenses (Safely)

Link again: https://github.com/rod-trent/JunkDrawer/tree/main/Threat%20Actor%20Empathy%20Simulator

Run it against your own environment today. I promise at least one “Oh no…” moment per session.

And when (not if) the attacker wins, remember: better to lose in a browser tab than in the news.

Happy defending! 🔒

– Rod Trent
