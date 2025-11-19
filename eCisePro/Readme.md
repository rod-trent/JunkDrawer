# eCise Pro

A few months ago I threw together a quick Python script called **[eCise](https://github.com/rod-trent/JunkDrawer/tree/main/eCise)** – a super-simple command-line workout generator that pulled exercises from a JSON file I scraped together, let you filter by equipment, and spat out a random workout. It worked, I used it every day, but… typing commands every time got old fast.

So I spent the last couple of weeks rebuilding it from the ground up as a real little web app with Streamlit.

Meet **eCise Pro** – now with a beautiful interface, PDF export, workout logging, history tracking, YouTube demo links, and (most importantly) **individual workout deletion only** because I’m tired of accidentally nuking my entire history when I just want to remove one bad session.

→ Live demo / code: https://github.com/rod-trent/JunkDrawer/blob/main/eCisePro/eCisePro.py  
(just copy the single file, run `streamlit run eCisePro.py` and you’re good)

### What you need to run it
```bash
pip install streamlit requests reportlab
```

That’s literally it. No database, no accounts, no cloud – everything is stored locally in JSON files next to the script:
- `exercises_cache.json` – the exercise database (auto-downloaded & cached)
- `workout_history.json` – your saved workouts

Works 100% offline after the first launch.

### Key Features (vs the old CLI version)

| Feature                      | Old eCise.py (CLI)       | New eCise Pro (this one)                              |
|------------------------------|--------------------------|-------------------------------------------------------|
| Interface                    | Terminal only            | Clean Streamlit web UI, works on phone too            |
| Equipment filter             | Yes                      | Yes + multiselect with nice capitalization           |
| Random workout generation    | Yes                      | Same logic but now shuffles + lets you pick 1–25 ex.  |
| YouTube demo videos          | Manual search            | Auto-detected + smart fallbacks per muscle group      |
| PDF export                   | No                       | Yes – beautiful printable PDF with tables for logging |
| Log sets/reps/weight         | No                       | Yes – right under each exercise                       |
| Save completed workouts     | No                       | Yes – with custom title                               |
| History page                 | No                       | Yes – newest first, expandable, total volume metric   |
| Delete workouts              | N/A                      | Individual delete only (no “clear all” button!)       |
| Offline-ready                | Yes                      | Yes – caches everything locally                       |

### How to use it in 30 seconds

1. Run `streamlit run eCisePro.py`
2. Pick whatever equipment you have today (dumbbells, barbell, cable, etc. – bodyweight always included)
3. Choose how many exercises you want (default 7)
4. Hit **Generate Workout**
5. Fill in sets/reps/weight as you go, watch the YouTube demo if you forgot form
6. Give the workout a name and hit **Save Workout**
7. Download a clean PDF for the gym printer if you want
8. Check History tab later and delete only the sessions you hate

### What I’m already thinking about for v2 (and I’m very open to requests!)

- Mobile/PWA version – so I can just open it on my phone at the gym without screenshots
- Better YouTube curation – right now it auto-detects or falls back to my personal favorite videos; happy to crowd-source better ones
- Way more exercises & smarter equipment tagging (bands, kettlebells, machines, etc.)
- Import from Garmin/Apple Health/Strava – auto-log the workout there when I save it
- Progressive overload suggestions (“last time you did 3×10@80kg on this…”)
- Warm-up / cool-down auto-add
- Maybe a “focus day” mode (push / pull / legs / upper / lower / full-body presets)

If any of that sounds useful to you, or if you have your own ideas (seriously – no idea is too small), drop an issue on the repo or ping me on X @rodtrent. I use this app myself every single training day, so anything that makes it better for you will probably make it better for me too.

Enjoy the gains! 💪

P.S. Yes, the name is intentionally dumb. “eCise” is just “exercise” with the x in the middle because I thought it looked cool at 2 a.m. No regrets.
