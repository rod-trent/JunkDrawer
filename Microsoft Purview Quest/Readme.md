# Microsoft Purview Quest – The Fun Way to Master Microsoft Purview (Local Version)

I just published a little Streamlit game that has quickly become my favorite way to teach (and learn) Microsoft Purview in 15–20 minutes flat.

Link: https://github.com/rod-trent/JunkDrawer/tree/main/Microsoft%20Purview%20Quest

## What is “Microsoft Purview Quest”?

It’s a 20-scene interactive story/game where you play the new Information Protection lead at a fictional company called “Zava”.  
You have exactly 30 days until a major compliance audit. Every day a new data-protection horror scenario appears (real things that actually happen in companies every day):

- Sales just emailed a 5 GB customer database via Gmail  
- Finance is manually deleting old records  
- An executive is emailing unencrypted credit-card numbers  
- Someone is printing sensitive contracts  
- Guest users have full SharePoint access  
- …and 15 more equally terrifying (but very common) situations.

For each scenario you get 3 possible actions. Pick the right Purview feature and your Compliance Score goes up and Risk goes down. Pick the wrong one and… well, let’s just say you might not survive until the audit.

It’s gamified learning with instant feedback, confetti cannons, and a dramatic “You’re fired!” screen if you do too poorly.

## Why this app is surprisingly valuable

1. **Muscle memory for Purview features** – After one play-through you will instantly remember that  
   → DLP + sensitivity labels stops Gmail exfil  
   → Retention labels + policies are the right way to handle Finance deletions  
   → Communication Compliance catches execs emailing credit cards  
   → Insider Risk Management is what you turn on when you see nightly exfiltration  
   …and 16 more mappings.

2. **Perfect for brown-bag sessions, onboarding, or lunch & learns** – Takes ~15 minutes, everyone screams and laughs when someone picks “Like the LinkedIn post with PII”.

3. **Zero cost, zero cloud dependencies** – This version is 100 % local. No Azure, no OpenAI credits, no internet required after the first `pip install`.

4. **Great interview or certification prep tool** – I’ve already used it in real interviews (“Walk me through how you would solve these five scenarios…”).

## Technical Requirements (super light)

- Python 3.8+
- Streamlit (`pip install streamlit`)
- That’s literally it. No external APIs.

Optional: a tiny logo called `ViewieSmall.png` in the same folder (it falls back to a placeholder if missing).

## How to Run It Locally

```bash
# 1. Clone or download the single Python file
git clone https://github.com/rod-trent/JunkDrawer.git
cd "JunkDrawer/Microsoft Purview Quest"

# 2. Install Streamlit (one time)
pip install streamlit

# 3. Run it
streamlit run "PurviewQuest_NoLLM.py"
```

Your browser will automatically open http://localhost:8501 and the game starts immediately.

## How to Play

- You start at Compliance 40 / Risk 80 (pretty bad shape).
- Every day you get a new incident and three choices.
- The choices are randomized each play-through so you can’t memorize positions.
- Immediate feedback appears at the top of the next turn telling you exactly why the choice was good or catastrophic.
- Try to reach Day 1 (the audit) with Compliance ≥ 85 and Risk ≤ 35 to get the legendary “CISO OF THE YEAR” ending with confetti.
- When you finish (win or lose) just click “New Quest – Play Again”.

## Customization Ideas (because it’s just Python)

The whole thing is one ~350-line file, so hacking it is trivial:

- Add your own scenarios (just append to the `SCENES` list)
- Change scoring weights
- Replace the logo with your company mascot
- Add sound effects (yes, people have already done that)
- Translate to other languages

## Future version (already in progress)

I’m building “Purview Quest – AI Edition” that uses an LLM to:

- Generate completely new random scenarios every time
- Accept free-text answers instead of multiple choice
- Give natural-language explanations
- Scale difficulty based on your current score

That version will live in a separate file and will require an OpenAI/Azure key, but this local version will always stay free and offline-capable.

## Final Thoughts

In an industry that loves death-by-PowerPoint training, this little game has been the single most effective way I’ve found to get people to actually remember which Purview capability solves which real-world problem.

Try it with your team next week. I guarantee at least one person will pick “Offer auditors coffee” on the final day and everyone will lose it laughing.

Repository again:  
https://github.com/rod-trent/JunkDrawer/tree/main/Microsoft%20Purview%20Quest

Happy defending (and may your Compliance score be ever high and your Risk score ever low)! 🚀

– Rod Trent
