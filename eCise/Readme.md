# 🏋️‍♂️ eCise: A Smart, Self-Updating Workout Generator Built with Python  
### *“Because even your Python scripts need to lift.”*

If you’ve ever opened your gym app and thought, *“Why am I still doing the same chest workout from 2019?”* — you’re not alone. That’s exactly why I built **eCise**: a lightweight, Python-based workout generator that automatically stays fresh by pulling live exercise data from GitHub.

This isn’t just another random workout generator. It’s a script that:
- Fetches updated, structured exercise data from the cloud  
- Caches it for offline use  
- Automatically categorizes exercises by muscle group  
- Generates time- or exercise-based routines  
- And now — displays deep, trainer-level details for every movement.

Let’s walk through what makes **eCise** unique, how it works, and how you can use or extend it yourself.

---

## 🧠 The Idea Behind eCise

I wanted a command-line fitness assistant that behaves like a real coach:
- Suggest workouts based on **time available** or **number of exercises**  
- Randomize sessions so no two routines are the same  
- Pull **the latest exercises**, not static data baked into the code  
- Stay **usable offline**, even when the network is down  

The result is a modular Python app that’s smart enough to fetch its own data — and resilient enough to work without it.

---

## ⚙️ How It Works

At its core, eCise retrieves exercise information from a structured JSON file hosted on GitHub:

📂 **Data source:**  
[`exercises_enriched_v2.json`](https://github.com/rod-trent/JunkDrawer/blob/main/eCise/exercises_enriched_v2.json)

Each entry includes not just a name and description, but also:
- Equipment used  
- Primary and secondary muscle groups  
- Step-by-step *how-to*  
- Difficulty level  
- Recommended rep scheme  
- Injury considerations  
- YouTube or video demo link  

These fields make it easy to generate comprehensive, educational workout routines — not just a list of exercises.

---

## 🧩 Smart Fetching and Caching

The script supports three intelligent data modes:

1. **Online Fetch (Default)**  
   Connects to GitHub, retrieves the latest exercise JSON, and saves it locally.  

2. **Cached Mode**  
   Checks your local cache — if the data hasn’t changed (via ETag / Last-Modified headers), it reuses the cache, saving time and bandwidth.  

3. **Offline Mode**  
   If you’re traveling, disconnected, or GitHub is down, eCise automatically falls back to a built-in mini database so you can still train without disruption.  

Want to force an update? Run:

```bash
python eCise.py --download

