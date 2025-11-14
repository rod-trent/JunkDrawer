# 🏋️‍♂️ eCise: A Smart, Self-Updating Workout Generator Built with Python  
### *“Because even your Python scripts need to lift.”*

If you’ve ever opened your gym app and thought, *“Why am I still doing the same chest workout from 2019?”* — you’re not alone. That’s exactly why I built **eCise**: a lightweight, Python-based workout generator that automatically stays fresh by pulling live exercise data from GitHub.

This isn’t just another random workout generator. It’s a script that:

- Fetches updated, structured exercise data from the cloud  
- Caches it for offline use  
- Automatically categorizes exercises by muscle group  
- Generates time- or exercise-based routines  
- And now — displays deep, trainer-level details for every movement  

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

At its core, **eCise** retrieves exercise information from a structured JSON file hosted on GitHub:

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

### 1. Online Fetch (Default)
Connects to GitHub, retrieves the latest exercise JSON, and saves it locally.  

### 2. Cached Mode
Checks your local cache — if the data hasn’t changed (via ETag / Last-Modified headers), it reuses the cache, saving time and bandwidth.  

### 3. Offline Mode
If you’re traveling, disconnected, or GitHub is down, eCise automatically falls back to a built-in mini database so you can still train without disruption.  

Want to force an update? Run:

```bash
python eCise.py --download
```

This wipes the cache and downloads the freshest data.

---

## 💪 Generating a Custom Workout

You can generate a session based on **number of exercises** or **time available**:

```bash
$ python eCise.py
Welcome to the Workout Routine Generator!
Select mode: (1) Number of exercises, (2) Time available (in minutes): 2
Enter time available (in minutes): 45
```

Each workout is randomly drawn from all muscle groups, ensuring balance across your program.

It will also prompt for the equipment you have available.

### Example Output

```text
Your Custom Workout Routine
===========================
Perform 3 sets of 8–12 reps for each exercise unless otherwise specified.

1. Flat Barbell Bench Press
   Description: Lie on a flat bench holding a barbell. Lower to chest; press back up.
   Equipment: Barbell, Bench
   Primary Muscles: Chest
   Secondary Muscles: Triceps, Shoulders
   Difficulty: Intermediate
   Recommended Rep Scheme: 3x8–10
   Injury Considerations: Avoid excessive arching; use a spotter.
   YouTube Video: https://www.youtube.com/watch?v=rT7DgCr-3pg
```

---

## 🧰 Key Technical Features

- **Dynamic Data Loading** – Pulls exercises from a GitHub-hosted JSON file in real time  
- **Cache Management** – Uses ETag/Last-Modified headers for conditional fetching  
- **Offline Fallback** – Loads from a local cache or built-in fallback set  
- **Flexible Routine Generator** – Builds workouts by time or by exercise count  
- **Detailed Output** – Includes all relevant training information — perfect for study or instruction  
- **Cross-Platform** – Works on any system with Python 3.7+ and internet access  

---

## 🖥️ Installation & Usage

Clone the repository or copy `eCise.py` to your machine:

```bash
git clone https://github.com/rod-trent/JunkDrawer.git
cd JunkDrawer/eCise
python eCise.py
```

Optional flags:

```bash
--download    # Force a fresh download
```

Default behavior uses cached or fallback data.

### Dependencies

```bash
pip install requests
```

That’s it — no extra frameworks, no web front end, just a clean and intelligent CLI tool.

---

## 🚀 Future Ideas

- Export workouts as PDF or .docx  
- Add weekly split generation (Push/Pull/Legs, Upper/Lower)  
- Build a lightweight web dashboard using FastAPI  
- Integrate progress tracking and performance logging  

---

## ❤️ Why This Matters

For developers, **eCise** shows how to combine small, powerful Python techniques:

- Working with remote JSON data  
- Implementing HTTP caching  
- Structuring robust fallbacks  
- Presenting rich output without over-engineering  

For fitness enthusiasts, it’s a **living workout library** — a command-line coach that updates itself over time.

---

## 🔗 Try It Yourself

💾 **Repo:** [GitHub – rod-trent/JunkDrawer/eCise](https://github.com/rod-trent/JunkDrawer/tree/main/eCise)  
📄 **Script:** `eCise.py`  
🌐 **JSON Source:** [`exercises_enriched_v2.json`](https://github.com/rod-trent/JunkDrawer/blob/main/eCise/exercises_enriched_v2.json)

---

> *This project blends automation with education — the same way we should approach training. Don’t just move weight; understand why and how.*  
> With **eCise**, your code and your workouts both keep evolving. 💪
