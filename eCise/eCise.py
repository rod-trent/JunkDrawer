import requests
import random
import json
import sys
from pathlib import Path
from collections import defaultdict

# ===== Configuration =====
EXERCISE_DATA_URL = "https://raw.githubusercontent.com/rod-trent/JunkDrawer/main/eCise/exercises_enriched_v2.json"
BASE_DIR = Path(__file__).resolve().parent
CACHE_PATH = BASE_DIR / "exercises_cache.json"
META_PATH = BASE_DIR / "exercises_cache.meta.json"

# ===== Minimal fallback data (guarantees offline usability) =====
FALLBACK_EXERCISES = {
    "Chest": [
        {
            "name": "Flat Barbell Bench Press",
            "description": "Lie on a flat bench holding a barbell. Lower to chest; press back up.",
            "youtube_link": "https://www.youtube.com/watch?v=rT7DgCr-3pg"
        },
        {
            "name": "Push-Ups",
            "description": "Plank position; lower chest near floor; push back up.",
            "youtube_link": "https://www.youtube.com/watch?v=IODxDxX7oi4"
        }
    ],
    "Back": [
        {
            "name": "Pull-Ups",
            "description": "Hang from bar; pull until chin passes bar; lower with control.",
            "youtube_link": "https://www.youtube.com/watch?v=eGo4IYlbE5g"
        }
    ],
    "Legs": [
        {
            "name": "Barbell Squats",
            "description": "Bar on back; squat to parallel; stand tall.",
            "youtube_link": "https://www.youtube.com/watch?v=Dy28eq2PjcY"
        }
    ],
    "Arms": [
        {
            "name": "Barbell Curls",
            "description": "Underhand grip; curl to chest; lower slowly.",
            "youtube_link": "https://www.youtube.com/watch?v=kwG2ipFRgfo"
        }
    ],
    "Core": [
        {
            "name": "Plank",
            "description": "Forearms + toes; body straight; hold.",
            "youtube_link": "https://www.youtube.com/watch?v=pSHjTRCQxIw"
        }
    ]
}

# ===== JSON I/O helpers =====
def _read_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _write_json(path: Path, data):
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# ===== Cache helpers =====
def _load_from_cache():
    data = _read_json(CACHE_PATH)
    if isinstance(data, dict) and data:
        print("📦 Loaded exercises from local cache.")
        return data
    return None

def _save_cache(data, headers):
    if not isinstance(data, dict) or not data:
        return
    _write_json(CACHE_PATH, data)
    meta = {}
    if "ETag" in headers:
        meta["ETag"] = headers["ETag"]
    if "Last-Modified" in headers:
        meta["Last-Modified"] = headers["Last-Modified"]
    if meta:
        _write_json(META_PATH, meta)

def _conditional_headers():
    meta = _read_json(META_PATH)
    if not isinstance(meta, dict):
        return {}
    headers = {}
    if "ETag" in meta:
        headers["If-None-Match"] = meta["ETag"]
    if "Last-Modified" in meta:
        headers["If-Modified-Since"] = meta["Last-Modified"]
    return headers

# ===== Data normalization =====
def _normalize_exercises(data):
    """
    Accept either:
      - dict[str, list[exercise]]  (already grouped)
      - list[exercise] with a grouping key -> converts to dict of lists
    Tries common grouping keys if needed: 'group', 'muscle_group', 'category', 'bodypart'.
    """
    if isinstance(data, dict):
        # assume already {group: [ex, ex]}
        return {k: (v or []) for k, v in data.items() if isinstance(v, list)}
    elif isinstance(data, list):
        # try to group by a likely key on each item
        group_keys = ["group", "muscle_group", "muscleGroup", "category", "bodypart", "body_part"]
        buckets = defaultdict(list)
        for item in data:
            if not isinstance(item, dict):
                continue
            group_val = None
            for gk in group_keys:
                if gk in item and item[gk]:
                    group_val = str(item[gk])
                    break
            if not group_val:
                group_val = "Misc"
            buckets[group_val].append(item)
        return dict(buckets)
    else:
        return {}

# ===== Fetch with caching / download =====
def load_exercises(force_download=False):
    """
    Load exercise data with caching and conditional requests.
    If `force_download` is True, bypasses cache metadata and pulls new data.
    Fallback order: GitHub -> cache -> built-in minimal dataset.
    """
    print("🔎 Loading exercise data...")

    if force_download:
        print("♻️ Forced download requested — bypassing cache.")
        try:
            resp = requests.get(EXERCISE_DATA_URL, timeout=10)
            resp.raise_for_status()
            raw = resp.json()
            data = _normalize_exercises(raw)
            if data:
                print("✅ Fresh data fetched from GitHub.")
                _save_cache(data, resp.headers)
                return data
            else:
                print("⚠️ GitHub returned data but it could not be normalized.")
        except Exception as e:
            print(f"⚠️ Download failed: {e}")
        cached = _load_from_cache()
        if cached:
            return cached
        print("➡️ Falling back to built-in dataset.")
        return FALLBACK_EXERCISES

    # Normal cached mode
    try:
        headers = _conditional_headers()
        resp = requests.get(EXERCISE_DATA_URL, headers=headers, timeout=10)
        if resp.status_code == 304:
            cached = _load_from_cache()
            if cached:
                print("✅ Cache is up to date (304 Not Modified).")
                return cached
            # If metadata exists without cache, fetch without conditions
            resp = requests.get(EXERCISE_DATA_URL, timeout=10)

        resp.raise_for_status()
        raw = resp.json()
        data = _normalize_exercises(raw)
        if data:
            print("✅ Loaded latest exercise data from GitHub.")
            _save_cache(data, resp.headers)
            return data
        print("⚠️ Received data from GitHub but could not normalize it.")
    except Exception as e:
        print(f"⚠️ Network/parse error: {e}")

    cached = _load_from_cache()
    if cached:
        return cached

    print("➡️ Falling back to built-in dataset.")
    return FALLBACK_EXERCISES

# ===== Equipment helpers =====
def get_unique_equipment(exercises_by_group):
    equipments = set()
    for group, exs in exercises_by_group.items():
        for ex in exs:
            eq = ex.get("equipment")
            if eq is None or not eq:
                continue
            if isinstance(eq, list):
                temp_set = {str(e).strip().lower() for e in eq if str(e).strip()}
            else:
                temp_set = {str(eq).strip().lower()} if str(eq).strip() else set()
            for e in temp_set:
                if e != "bodyweight":
                    equipments.add(e)
    return sorted(list(equipments))

def filter_exercises_by_equipment(exercises_by_group, selected_eq):
    if selected_eq is None:
        return {k: v[:] for k, v in exercises_by_group.items()}
    new_data = defaultdict(list)
    for group, exs in exercises_by_group.items():
        for ex in exs:
            eq = ex.get("equipment")
            if eq is None:
                eq_set = set()
            elif isinstance(eq, list):
                eq_set = {str(e).strip().lower() for e in eq if str(e).strip()}
            else:
                eq_set = {str(eq).strip().lower()} if str(eq).strip() else set()
            if eq_set == {"bodyweight"}:
                eq_set = set()
            if eq_set.issubset(selected_eq):
                new_data[group].append(ex)
    return dict(new_data)

# ===== Workout generation =====
def generate_workout(exercises_by_group, num_exercises=None, time_available=None):
    groups = list(exercises_by_group.keys())
    if not groups:
        print("No exercise data found.")
        return []

    if time_available is not None:
        # ~10 minutes per exercise (sets + rest)
        time_per_exercise = 10
        num_exercises = max(len(groups), time_available // time_per_exercise)

    if num_exercises is None:
        num_exercises = len(groups)

    if num_exercises < len(groups):
        print(f"Warning: Number of exercises ({num_exercises}) < number of groups ({len(groups)}).")
        selected_groups = random.sample(groups, num_exercises)
        workout = [random.choice(exercises_by_group[g]) for g in selected_groups if exercises_by_group[g]]
    else:
        # one from each group
        workout = [random.choice(exercises_by_group[g]) for g in groups if exercises_by_group[g]]
        # add extras randomly to reach target
        for _ in range(max(0, num_exercises - len(workout))):
            g = random.choice(groups)
            if exercises_by_group[g]:
                workout.append(random.choice(exercises_by_group[g]))

    random.shuffle(workout)
    return workout

# ===== Output formatting =====
def _format_val(v):
    """Best-effort pretty-printer: lists -> comma-separated, dicts -> JSON, None/'' -> 'N/A'."""
    if v is None or v == "":
        return "N/A"
    if isinstance(v, list):
        # Flatten list of strings or list of dicts with common label keys
        try:
            if v and isinstance(v[0], dict):
                keys = ["name", "muscle", "label", "title"]
                parts = []
                for item in v:
                    if not isinstance(item, dict):
                        parts.append(str(item))
                        continue
                    picked = None
                    for k in keys:
                        if k in item and item[k]:
                            picked = item[k]
                            break
                    parts.append(str(picked) if picked is not None else json.dumps(item, ensure_ascii=False))
                return ", ".join(parts)
            return ", ".join(str(x) for x in v)
        except Exception:
            return ", ".join(str(x) for x in v)
    if isinstance(v, dict):
        if "name" in v and isinstance(v["name"], (str, int, float)):
            return str(v["name"])
        return json.dumps(v, ensure_ascii=False)
    return str(v)

def print_workout_sheet(workout):
    """Print the generated workout with enriched details when available."""
    print("\nYour Custom Workout Routine")
    print("===========================")
    print("Perform 3 sets of 8–12 reps for each exercise unless otherwise specified.\n")

    for i, ex in enumerate(workout, 1):
        name = ex.get("name", "Unknown Exercise")
        # Prefer explicit 'how_to' as description if present; else 'description'
        desc = ex.get("how_to") or ex.get("description") or "No description available."
        youtube = ex.get("youtube_link") or ex.get("video") or "N/A"

        equipment = ex.get("equipment")
        primary = ex.get("primary_muscles")
        secondary = ex.get("secondary_muscles")
        how_to = ex.get("how_to")
        difficulty = ex.get("difficulty")
        rep_scheme = ex.get("recommended_rep_scheme")
        injuries = ex.get("injury_considerations")

        print(f"{i}. {name}")
        print(f"   Description: {_format_val(desc)}")
        print(f"   YouTube Video: {_format_val(youtube)}")

        # Enriched fields (only print if present)
        if equipment is not None:
            print(f"   Equipment: {_format_val(equipment)}")
        if primary is not None:
            print(f"   Primary Muscles: {_format_val(primary)}")
        if secondary is not None:
            print(f"   Secondary Muscles: {_format_val(secondary)}")
        if how_to is not None and how_to != desc:
            print(f"   How To: {_format_val(how_to)}")
        if difficulty is not None:
            print(f"   Difficulty: {_format_val(difficulty)}")
        if rep_scheme is not None:
            print(f"   Recommended Rep Scheme: {_format_val(rep_scheme)}")
        if injuries is not None:
            print(f"   Injury Considerations: {_format_val(injuries)}")

        print()  # blank line between exercises

# ===== Main entry point =====
def main():
    force_download = "--download" in sys.argv
    print("Welcome to the Workout Routine Generator!")
    exercises_by_group = load_exercises(force_download=force_download)

    if not exercises_by_group:
        print("❌ Unable to load exercises.")
        sys.exit(1)

    # Prompt for equipment
    unique_eq = get_unique_equipment(exercises_by_group)
    if unique_eq:
        print("\nAvailable equipment options:")
        for i, eq in enumerate(unique_eq, 1):
            print(f"{i}. {eq.capitalize()}")
        user_input = input("Enter the equipment you have available (comma-separated numbers or names, or 'none' for bodyweight only, or 'all' for any): ").strip().lower()
    else:
        user_input = 'none'  # Default to none if no equipment found
        print("\nNo specific equipment found in data. Using bodyweight only.")

    if user_input == 'all':
        selected_eq = None
    elif user_input == 'none':
        selected_eq = set()
    else:
        parts = [p.strip() for p in user_input.split(',') if p.strip()]
        selected_eq = set()
        for p in parts:
            if p.isdigit():
                try:
                    idx = int(p) - 1
                    if 0 <= idx < len(unique_eq):
                        selected_eq.add(unique_eq[idx])
                except ValueError:
                    pass
            elif p in unique_eq:
                selected_eq.add(p)

    exercises_by_group = filter_exercises_by_equipment(exercises_by_group, selected_eq)

    if not exercises_by_group:
        print("❌ No exercises available with the selected equipment.")
        sys.exit(1)

    choice = input("Select mode: (1) Number of exercises, (2) Time available (in minutes): ").strip()
    if choice == "1":
        num = int(input("Enter number of exercises: ").strip())
        workout = generate_workout(exercises_by_group, num_exercises=num)
    elif choice == "2":
        time = int(input("Enter time available (in minutes): ").strip())
        workout = generate_workout(exercises_by_group, time_available=time)
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    print_workout_sheet(workout)

if __name__ == "__main__":
    main()
