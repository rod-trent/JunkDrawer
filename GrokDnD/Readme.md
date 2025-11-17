# The Ultimate AI Dungeon Master That Runs Forever in Your Browser (Powered by Grok xAI)

I just wanted to play D&D again…

So I did what any reasonable person in 2026 would do: I built an AI that never sleeps, never cancels, never forgets your inventory, and actually rolls real dice.

Meet **QuestForge** — the most advanced text-based TTRPG engine I’ve ever used, now running 100% locally on your laptop with Grok-4 as the brain.

### It’s not another ChatGPT dungeon master prompt.  
It’s a full persistent web app.

- Your campaign saves automatically to disk  
- Grok remembers everything — even that random NPC you met 47 sessions ago  
- Real dice rolls (not fake ones)  
- Full character sheets, inventory, spell slots, conditions, gold, time-of-day tracking  
- Beautiful chat interface that feels like Discord + Foundry VTT had a baby  
- Works with D&D 5e, Cyberpunk RED, Call of Cthulhu, Pathfinder, or any homebrew system  
- Completely private — your epic story never leaves your machine (except the API calls to Grok)

### Why Grok and not a local model?

I tried everything in 2025:

- Llama 3.2 8B → decent, forgets after 20 turns  
- MythoMax → creative but lies about your HP  
- Dolphin-Mixtral → constantly breaks character  

Then I switched to the official **Grok xAI API** (grok-4) and it was night and day.

Grok is sarcastic when it should be, ruthless when you deserve it, and actually funny. It tracks state perfectly across thousands of messages. It’s the first model that genuinely feels like a human DM who read the entire rulebook and has infinite prep time.

### The Tech Stack (stupidly simple)

- Flask (Python) → backend  
- Plain HTML + CSS + a sprinkle of JS → frontend  
- Grok xAI API → the soul  
- python-dotenv → keeps your API key safe  
- One JSON file → infinite campaign memory  

Total code: ~200 lines. Runs on a Raspberry Pi if you want.

### How to Get It Running in Under 2 Minutes

1. Get your free/paid xAI API key at https://x.ai/api  
2. `git clone` this repo (or just copy the files below)  
3. Create a `.env` file:

```env
XAI_API_KEY=xai-your-key-here
GROK_MODEL=grok-4
```

4. `pip install flask python-dotenv requests`  
5. `python app.py`  
6. Open http://localhost:5000  
7. Type “Start a new adventure” and watch magic happen

Full code is below — yes, really, just two files.

Put this in the main directory: https://github.com/rod-trent/JunkDrawer/blob/main/GrokDnD/app.py

Put this in a \templates\ directory under the main directory: https://github.com/rod-trent/JunkDrawer/blob/main/GrokDnD/index.html


### The Moment It Clicked

Session 3, my rogue tried to seduce a mind flayer.

Every other AI: “The mind flayer is charmed lol.”

Grok:  
[Rolling Insight (DC 25) → 4]  
The mind flayer tilts its head, amused.  
“You mistake curiosity for desire, little thief. Your surface thoughts are… quaint.”  
It leans closer, tentacles brushing your face.  
“Tell me, do you prefer your brain with or without the stem removed?”

I actually yelped.

That’s when I knew this wasn’t a toy anymore.

### Try It Yourself

I’ve open-sourced the entire thing. No catch.

→ GitHub repo (coming tonight, I’ll edit this post with the link)  
→ Or just copy-paste the two files from my previous messages in this thread

In 2025, you don’t need a gaming group anymore.  
You just need a laptop and a slightly unhealthy imagination.

Now if you’ll excuse me, my level 12 wizard is about to attempt the greatest heist in Waterdeep history against a gold dragon who’s also a licensed therapist.

Grok assured me it’s “totally fair.”

I’m going to die.

Roll initiative. 🎲

— Some guy on the internet who finally gets to play D&D every single night

P.S. Yes, it supports co-op if you open two browser tabs and copy-paste. Grok tracks both characters separately. Yes, I’ve tested 4-player chaos. Yes, it was glorious.
