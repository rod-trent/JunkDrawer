# Build Your Own 24/7 AI Travel Price-Watch Agent with Grok-4 and Streamlit

**Grok Travel Agent** — a completely free, local, privacy-first Streamlit app that plans your trip, finds current flight + hotel prices, adds the trip to your calendar, shows the weather forecast, and then watches prices 24/7 and alerts you the moment they drop significantly.

Here’s what it looks like in action:

- You type: “Paris from Cincinnati, third week of February 2026, Tuesday to Sunday”
- It instantly understands → CVG → CDG, exact dates, check-in/check-out
- Shows Google Flights / Hotels / Maps deep-links
- Gives you a 7-day weather forecast
- Lets you download an .ics calendar file
- You click one big button → it starts checking prices every 15 minutes forever (even if you close the browser tab)
- The second a flight drops more than 8%, you get a toast notification

All of this running on your own machine, no third-party accounts, no data sent anywhere except to xAI’s API.

### Get the App Right Now

The complete, ready-to-run code is available here:  
🔗 https://github.com/rod-trent/JunkDrawer/tree/main/Travel%20Agent

Just download `trip_agent.py`, add your `.env` with your xAI API key, and you’re good to go!

### Tech Stack
- Python 3.9+
- Streamlit
- OpenAI Python library (pointed at xAI’s endpoint)
- Grok-4 model (`grok-4` via https://api.x.ai/v1)
- python-dotenv, icalendar, standard library only

### Requirements

You only need two things:

1. An xAI API key (get one at https://x.ai/api)
2. Python environment

Install the dependencies:

```bash
pip install streamlit openai python-dotenv icalendar
```

### How to Run It (super simple)

```bash
# 1. Download from GitHub
git clone https://github.com/rod-trent/JunkDrawer.git
cd "JunkDrawer/Travel Agent"

# Or just download the single file directly from the link above

# 2. Create .env
echo "XAI_API_KEY=your_xai_api_key_here" > .env

# 3. Run
streamlit run trip_agent.py
```

Open http://localhost:8501 and start planning!

### Full Feature List

- Natural language trip planning (one-sentence input)
- Automatic airport code resolution
- One-way or round-trip support
- Multi-adult / multi-room ready
- Instant Google Flights / Hotels / Maps deep links
- 7-day weather forecast for the destination
- Downloadable .ics calendar file
- Persistent trip saving
- 24/7 background price monitoring (daemon thread)
- Real-time price lookup using Grok-4’s live web access
- Price-drop alerts (>8% drop)
- Toast notifications + auto-refresh
- Latest best flight + hotel with direct booking links
- “Start Over” button

### How It Actually Works (the magic)

1. Grok-4 parses your natural language into perfect structured JSON (airport codes included!)
2. Live price checks are done by simply asking Grok-4 to “search live prices RIGHT NOW” — it has real-time web access, so no scrapers needed
3. A background Python thread runs forever, checking every 15 minutes and triggering Streamlit toasts on drops

### Final Thoughts

This is hands-down the most useful personal travel tool I’ve built. It stays accurate forever because Grok-4 handles all the live data — zero maintenance required.

Go grab it from the GitHub link above and let your next trip basically book itself when the price is right.

Happy travels ✈️

– Rod Trent (@rodtrent)  
November 20, 2025
