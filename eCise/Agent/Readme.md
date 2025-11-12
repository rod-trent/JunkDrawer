
# 🧠 Deploying and using the eCise CrewAI Agent  
### *“Because even your Python agents need to lift.”*

---

## 💪 What Is eCise CrewAI?

**eCise** started as a simple Python script that generates randomized, balanced workout routines using live exercise data from GitHub.  

Now, it’s evolved into a **CrewAI agent** — an intelligent, modular fitness assistant that can be run, orchestrated, and reused in complex AI workflows.  

This guide shows you exactly how to deploy and run the **CrewAI version of eCise**, whether locally or as part of a multi-agent Crew.

---

## ⚙️ Step 1: Prerequisites

Make sure you have:

- **Python 3.10+**
- **pip** and **virtualenv**
- A working **CrewAI** installation (v0.28 or later)

If you haven’t used CrewAI before, install it globally:

```bash
pip install crewai crewai-tools
```

---

## 🗂️ Step 2: Project Structure

Download the prepared ZIP file from the repo:

📦 [ecise_crewai_yaml.zip](sandbox:/mnt/data/ecise_crewai_yaml.zip)

Then unzip it:

```bash
unzip ecise_crewai_yaml.zip
cd ecise_crewai
```

Your directory should look like this:

```
ecise_crewai/
├── crew.yaml
├── tasks.yaml
├── requirements.txt
└── tools/
    └── ecise_tool.py
```

---

## 🧩 Step 3: Install Dependencies

Create a new virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

---

## 🧠 Step 4: Understanding `crew.yaml`

Here’s what the main configuration does:

- Defines the **Crew** (`eCise Crew`)
- Creates a single **agent** called `Workout Coach`
- Uses the **Python tool** `ecise_tool.py` to generate routines
- Accepts three input fields:  
  - `mode` → `"by_exercises"` or `"by_time"`  
  - `value` → number of exercises or minutes  
  - `refresh` → optional boolean for fresh data fetch

The key section:

```yaml
tasks:
  - id: generate_plan
    agent: coach
    inputs:
      mode: "{{mode}}"
      value: "{{value}}"
      refresh: "{{refresh|false}}"
    output_file: "output/workout.md"
```

This task runs your tool and writes the generated Markdown workout plan to `output/workout.md`.

---

## 🧰 Step 5: Running the Agent

If you’re using the **CrewAI CLI**, you can launch it directly:

```bash
crew run crew.yaml   --inputs mode=by_exercises value=7 refresh=false
```

Or, to generate a time-based routine:

```bash
crew run crew.yaml   --inputs mode=by_time value=45
```

If successful, you’ll see something like:

```
✅ Task: generate_plan
Agent: Workout Coach
Output written to output/workout.md
```

---

## 📄 Step 6: Output Example

Open `output/workout.md` — it’ll look something like this:

```markdown
# Your Custom Workout Routine

_Perform 3 sets of 8–12 reps for each exercise unless otherwise specified._

## 1. Flat Barbell Bench Press
- **Description:** Lie on a flat bench holding a barbell. Lower to chest; press back up.
- **YouTube/Video:** https://www.youtube.com/watch?v=rT7DgCr-3pg
- **Equipment:** Barbell, Bench
- **Primary Muscles:** Chest
- **Secondary Muscles:** Triceps, Shoulders
- **Difficulty:** Intermediate
- **Recommended Rep Scheme:** 3x8–10
- **Injury Considerations:** Avoid excessive arching; use a spotter.
```

---

## 🌐 Step 7: How the Agent Works

The tool behind the agent (`ecise_tool.py`) does the heavy lifting:

1. **Fetches live exercise data** from:  
   [https://github.com/rod-trent/JunkDrawer/blob/main/eCise/exercises_enriched_v2.json](https://github.com/rod-trent/JunkDrawer/blob/main/eCise/exercises_enriched_v2.json)
2. **Caches** it locally for offline use  
3. **Normalizes** the data into muscle groups  
4. **Generates random, balanced workouts**  
5. **Outputs** a detailed Markdown routine with:
   - Equipment
   - Primary/secondary muscles
   - Difficulty
   - Reps
   - How-to
   - Injury considerations
   - YouTube link

If GitHub is offline or the fetch fails, the tool automatically falls back to a minimal built-in dataset — meaning it always works, online or offline.

---

## 🧪 Step 8: Integrating Into a Multi-Agent Crew

You can easily extend this by adding the `coach` agent to a larger multi-agent setup.

For example, pair it with:

- A **Nutrition Planner Agent**  
- A **Progress Tracker Agent**  
- A **Data Visualizer Agent**  

CrewAI’s YAML makes it easy to combine them into a single automated health system.

---

## 🧼 Step 9: Reset or Refresh Cache

If you want to clear old exercise data and fetch fresh entries:

```bash
crew run crew.yaml   --inputs mode=by_exercises value=5 refresh=true
```

This forces a re-download from GitHub and updates the local cache.

---

## 🚀 Step 10: Customize and Expand

You can enhance eCise CrewAI by:

- Changing the **output format** (Markdown → PDF → HTML)
- Adding **voice output** (Text-to-Speech)
- Using a **schedule task** to automatically generate a daily routine
- Deploying via **Docker** for server use

---

## ❤️ Why This Matters

This CrewAI agent shows how simple Python scripts can evolve into **autonomous, reusable AI units**.  

With YAML-driven orchestration, eCise can run standalone or as part of a larger wellness automation — bridging **fitness**, **data**, and **AI** seamlessly.

---

### 🏁 Summary

| Step | Action |
|------|--------|
| 1 | Install Python & CrewAI |
| 2 | Unzip `ecise_crewai_yaml.zip` |
| 3 | Install requirements |
| 4 | Run the agent with CrewAI |
| 5 | View `output/workout.md` |
| 6 | Extend with other AI agents |

---

### 🧠 Final Thought

> *You don’t need a gym app full of ads to stay motivated — you just need one good Python agent.*  
> Build it once. Automate it forever. 🏋️‍♂️
