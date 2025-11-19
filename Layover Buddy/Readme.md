# Airport Layover Buddy: Turn Boring Layovers into Mini-Adventures with Grok

I hate long layovers… but I also hate wasting them.

You know the feeling: 6–12 hours in a random city, too short for a proper trip, too long to just sit in a plastic chair eating overpriced airport sushi. Until now, most of us either (a) nap in a lounge, (b) wander aimlessly, or (c) doom-scroll X while praying for free Wi-Fi.

I decided to fix that.

Introducing **Airport Layover Buddy** – a tiny Streamlit app powered by Grok (xAI) that instantly builds you a hyper-optimized, realistic itinerary for almost any layover in the world.

Link: https://github.com/rod-trent/JunkDrawer/tree/main/Layover%20Buddy  
(Deploy it yourself in under 2 minutes – instructions below)

### What It Actually Does

You tell the app four simple things:

1. Layover city (e.g., Singapore, Istanbul, Dubai, Tokyo…)
2. Airport code (optional but improves accuracy)
3. How many hours/minutes you really have on the ground
4. Your priorities and travel style

Hit the big blue button → Grok spins up and returns a beautiful, timed markdown itinerary that looks like this (example: 7-hour layover in Doha):

**✈️ Your 7h 30m Doha Layover Adventure (Luxury + Food & Sights focus)**  
🛬 14:20 – Clear immigration & collect luggage (30 min)  
🚕 14:50 – Private transfer to Souq Waqif (25 min, ~$30)  
☕ 15:15 – 16:30 – Souq Waqif stroll + Arabic coffee & dates at Al Jasra  
🍽 16:30 – 17:45 – Early dinner at Damasca One (Syrian, excellent shisha terrace)  
🕌 17:45 – 18:15 – Quick photo stop at Museum of Islamic Art (stunning from outside at sunset)  
🚕 18:15 – 18:55 – Return to HAMAD International  
🛋 19:00 – 20:20 – Al Mourjan Business Lounge (The Garden area – quiet, showers, à la carte dining)  
🛫 21:50 – Boarding with plenty of buffer

Every plan factors in real transit times, immigration realities, current lounge options, and always leaves a safe 90–120 minute buffer before boarding.

### Why Grok Instead of Other Models?

I tested GPT-4o, Claude 3.5, Gemini 1.5 Pro, and Grok-4 side-by-side.

- GPT-4o and Claude hallucinate lounge names half the time.
- Gemini is overly cautious and suggests you “just stay in the airport” for anything under 10 hours.
- Grok-4 actually understands travel nuance, knows the difference between Priority Pass lounges and airline-specific ones, and writes in a fun, human style without being told to.

Plus… it’s just faster and cheaper via the xAI API right now.

### Requirements (Super Minimal)

You need exactly three things:

1. Python 3.9+
2. A free or paid xAI/Grok API key → https://x.ai/api
3. That’s it.

Install dependencies:

```bash
pip install streamlit openai python-dotenv
```

Create a `.env` file in the folder:

```
GROK_API_KEY=your_key_here
GROK_BASE_URL=https://api.x.ai/v1   # optional, default works
```

Run it locally:

```bash
streamlit run LayoverBuddy.py
```

Or deploy instantly to Streamlit Community Cloud, Railway, Fly.io, etc. (it’s one file + .env).

### How to Use It

1. Enter city (and airport code if you know it – helps a lot for cities with multiple airports).
2. Slide the layover time – it combines hours + minutes.
3. Use the “Flight Delay Adjustment” slider if your inbound is late or outbound moved earlier.
4. Pick your priorities (you can select multiple).
5. Choose Budget / Comfort / Luxury.
6. Smash the 🚀 button.

The itinerary streams in real-time, and you can tweak any slider and regenerate instantly – perfect when your gate agent says “we’re delayed another 90 minutes.”

### My Favorite Real-World Uses So Far

- 5h 20m in Helsinki → perfect sauna + cinnamon bun plan at Löyly  
- 9h in Istanbul → Grand Bazaar + Bosphorus ferry + best kebap in Sultanahmet  
- 4h in Singapore (red-eye arrival) → straight to Jewel Changi nap pods + kaya toast plan  
- 11h overnight in Seoul → actually worth leaving ICN for Myeongdong street food

Even for super-tight layovers (<4h) it gracefully says “Nope, stay airside – here are the three best lounges and where to get decent ramen.”

### Try It Yourself

Repo: https://github.com/rod-trent/JunkDrawer/tree/main/Layover%20Buddy

Deploy it, throw it on your phone’s home screen as a PWA, and never waste another layover again.

Safe travels, and may your layovers always be long enough for at least one great meal.
