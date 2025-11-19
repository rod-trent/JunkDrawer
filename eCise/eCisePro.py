# app.py - eCise Pro – Individual Delete Only (Clean & Perfect)
import streamlit as st
import requests
import json
import random
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# PDF Support (run once: pip install reportlab)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from io import BytesIO

# ========================= CONFIG =========================
EXERCISE_DATA_URL = "https://raw.githubusercontent.com/rod-trent/JunkDrawer/main/eCise/exercises_enriched_v2.json"
BASE_DIR = Path(__file__).resolve().parent
CACHE_PATH = BASE_DIR / "exercises_cache.json"
META_PATH = BASE_DIR / "exercises_cache.meta.json"
HISTORY_PATH = BASE_DIR / "workout_history.json"

st.set_page_config(page_title="eCise Pro", page_icon="💪", layout="centered")
st.title("💪 eCise Pro – Workout Generator & Tracker")

tab1, tab2 = st.tabs(["🏋️ Workout", "📈 History"])

# ======================= HELPERS ======================
def read_json(p):
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def write_json(p, data):
    try:
        with p.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except:
        pass

def normalize(data):
    if isinstance(data, dict):
        return {k: v or [] for k, v in data.items()}
    buckets = defaultdict(list)
    for ex in data or []:
        g = next((str(ex.get(k, "")) for k in ["group","muscle_group","category","bodypart"] if ex.get(k)), "Misc")
        buckets[g].append(ex)
    return dict(buckets)

def get_youtube_url(ex: dict) -> str:
    if "example_url" in ex and isinstance(ex["example_url"], dict):
        yt = ex["example_url"].get("youtube")
        if yt and isinstance(yt, str):
            return yt.strip()
    for v in ex.values():
        if isinstance(v, str) and ("youtube.com" in v or "youtu.be" in v):
            return v.strip()
    muscles = " ".join([str(m) for m in (ex.get("primary_muscles") or []) + (ex.get("secondary_muscles") or [])]).lower()
    name = ex.get("name", "").lower()
    fallback = {
        "back": "https://www.youtube.com/watch?v=6zRBe4sAmzY",
        "chest": "https://www.youtube.com/watch?v=IODxDxX7oi4",
        "bicep": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo",
        "tricep": "https://www.youtube.com/watch?v=6kAL2D6eP2U",
        "shoulder": "https://www.youtube.com/watch?v=qEwKCR5JCog",
        "quad": "https://www.youtube.com/watch?v=ACLX8dQwIHU",
        "hamstring": "https://www.youtube.com/watch?v=JCXUYuzwNrM",
        "glute": "https://www.youtube.com/watch?v=MC3C2Q2RoGs",
        "core": "https://www.youtube.com/watch?v=MKmrjGHiF2U",
    }
    for key, url in fallback.items():
        if key in muscles or key in name:
            return url
    return "https://www.youtube.com/watch?v=IODxDxX7oi4"

def format_steps(ex):
    steps = ex.get("how_to") or ex.get("steps") or ex.get("instructions") or ex.get("execution") or ""
    if isinstance(steps, list):
        clean = [s.strip() for s in steps if s and str(s).strip()]
        return "<br/>".join(f"{i+1}. {s}" for i, s in enumerate(clean)) if clean else ""
    if isinstance(steps, str) and steps.strip():
        lines = [l.strip() for l in steps.strip().split("\n") if l.strip()]
        return "<br/>".join(f"{i+1}. {l}" for i, l in enumerate(lines))
    return ""

# ======================= PDF GENERATOR ======================
def create_pdf(workout, title="eCise Workout"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BigTitle', fontSize=20, alignment=1, spaceAfter=30, fontName='Helvetica-Bold'))
    story = []
    story.append(Paragraph(title, styles['BigTitle']))
    story.append(Paragraph(datetime.now().strftime("%B %d, %Y"), styles['Normal']))
    story.append(Spacer(1, 20))
    for i, ex in enumerate(workout, 1):
        story.append(Paragraph(f"{i}. {ex.get('name', 'Unknown')}", styles['Heading2']))
        if steps := format_steps(ex):
            story.append(Paragraph("Steps:", styles['Normal']))
            story.append(Paragraph(steps, styles['Normal']))
        info = []
        eq = ex.get("equipment")
        if eq and str(eq).lower() != "bodyweight":
            info.append(f"Equipment: {eq if isinstance(eq,str) else ', '.join(eq)}")
        prim = ex.get("primary_muscles")
        if prim:
            p = ", ".join(prim) if isinstance(prim,list) else prim
            info.append(f"Primary: {p}")
        info.append(f"YouTube: {get_youtube_url(ex)}")
        story.append(Paragraph(" | ".join(info), styles['Italic']))
        story.append(Spacer(1, 20))
        data = [["Sets", "Reps", "Weight (kg)", "Notes"]]
        for _ in range(4): data.append(["", "", "", ""])
        t = Table(data)
        t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        story.append(t)
        story.append(Spacer(1, 30))
    doc.build(story)
    buffer.seek(0)
    return buffer

# ======================= LOAD DATA ======================
@st.cache_data(ttl=86400)
def load_exercises():
    cached = read_json(CACHE_PATH)
    if cached: return cached
    try:
        headers = {}
        meta = read_json(META_PATH) or {}
        if meta.get("ETag"): headers["If-None-Match"] = meta["ETag"]
        if meta.get("Last-Modified"): headers["If-Modified-Since"] = meta["Last-Modified"]
        r = requests.get(EXERCISE_DATA_URL, headers=headers, timeout=15)
        if r.status_code == 304: return cached
        r.raise_for_status()
        data = normalize(r.json())
        write_json(CACHE_PATH, data)
        write_json(META_PATH, {k: r.headers[k] for k in ("ETag","Last-Modified") if k in r.headers})
        return data
    except:
        st.toast("Offline mode")
    return {"Misc": []}

exercises = load_exercises()

# ======================= WORKOUT TAB ======================
with tab1:
    with st.expander("🎒 Equipment (bodyweight always included)", expanded=True):
        all_eq = set()
        for lst in exercises.values():
            for ex in lst:
                eq = ex.get("equipment")
                if eq and str(eq).lower() != "bodyweight":
                    if isinstance(eq, list):
                        all_eq.update(str(e).strip().lower() for e in eq)
                    else:
                        all_eq.add(str(eq).strip().lower())
        selected = st.multiselect("What do you have?", sorted(all_eq), format_func=str.capitalize)

    have = {e.lower() for e in selected}

    filtered = {}
    for group, lst in exercises.items():
        good = []
        for ex in lst:
            req = set()
            eq = ex.get("equipment")
            if eq:
                req = {str(e).strip().lower() for e in (eq if isinstance(eq,list) else [eq])}
                req.discard("bodyweight")
            if req.issubset(have):
                good.append(ex)
        if good:
            filtered[group] = good

    if not filtered:
        st.error("No exercises available")
        st.stop()

    st.markdown("### Number of exercises")
    col_num, col_btn = st.columns([2, 1])
    with col_num:
        num_ex = st.number_input("How many", 1, 25, 7, label_visibility="collapsed")
    with col_btn:
        generate = st.button("🎲 Generate Workout", type="primary", use_container_width=True)

    if generate:
        workout = []
        for g in filtered.values():
            if g: workout.append(random.choice(g))
        while len(workout) < num_ex:
            workout.append(random.choice(random.choice(list(filtered.values()))))
        random.shuffle(workout)
        st.session_state.workout = workout
        st.rerun()

    if "workout" in st.session_state:
        workout = st.session_state.workout
        st.success(f"{len(workout)} exercises ready!")

        default_title = f"My Workout – {datetime.now().strftime('%b %d, %Y')}"
        pdf_title = st.text_input("PDF Title (optional)", value=default_title)
        pdf_buffer = create_pdf(workout, title=pdf_title)
        st.download_button(
            label="📄 Download as PDF",
            data=pdf_buffer,
            file_name=f"{pdf_title.replace(' ', '_')[:50]}.pdf",
            mime="application/pdf"
        )

        logged = []
        for i, ex in enumerate(workout, 1):
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{i}. {ex.get('name', 'Unknown')}**")
                    if steps := format_steps(ex):
                        st.markdown("**Steps:**")
                        st.markdown(steps.replace("<br/>", "\n"))

                    info = []
                    eq = ex.get("equipment")
                    if eq and str(eq).lower() != "bodyweight":
                        info.append(f"**Eq:** {eq if isinstance(eq,str) else ', '.join(eq)}")
                    prim = ex.get("primary_muscles")
                    if prim:
                        p = ", ".join(prim) if isinstance(prim,list) else prim
                        info.append(f"**Primary:** {p}")
                    if info:
                        st.caption(" • ".join(info))

                    ca, cb, cc = st.columns(3)
                    sets = ca.number_input("Sets", 1, 10, 3, key=f"s{i}")
                    reps = cb.number_input("Reps", 1, 50, 10, key=f"r{i}")
                    weight = cc.number_input("Weight kg", 0.0, 300.0, 0.0, 2.5, key=f"w{i}")
                    logged.append({"name": ex["name"], "sets": sets, "reps": reps, "weight": weight if weight > 0 else None})

                with c2:
                    st.markdown(f"[🎥 Watch]({get_youtube_url(ex)})")

        col_title, col_save = st.columns([3, 1])
        with col_title:
            save_title = st.text_input("Workout Title (for history)", placeholder="e.g. Full Body Blast")
        with col_save:
            save = st.button("💾 Save Workout", type="primary", use_container_width=True)

        if save:
            title = save_title.strip() or f"Workout – {datetime.now().strftime('%b %d, %Y %H:%M')}"
            hist = read_json(HISTORY_PATH) or []
            hist.append({
                "title": title,
                "date": datetime.now().isoformat(),
                "exercises": logged
            })
            write_json(HISTORY_PATH, hist)
            st.success(f"Saved as **{title}**!")
            del st.session_state.workout
            st.rerun()

# ======================= HISTORY TAB – Individual Delete Only ======================
with tab2:
    st.header("Workout History")

    hist = read_json(HISTORY_PATH) or []

    if not hist:
        st.info("No saved workouts yet")
    else:
        # Newest first
        for idx, entry in enumerate(reversed(hist)):
            real_idx = len(hist) - 1 - idx
            title = entry.get("title", "Untitled Workout")
            dt = datetime.fromisoformat(entry["date"]).strftime("%b %d, %Y • %H:%M")

            col1, col2 = st.columns([6, 1])
            with col1:
                with st.expander(f"**{title}** – {dt}", expanded=False):
                    vol = 0
                    for e in entry["exercises"]:
                        line = f"**{e['name']}** — {e['sets']}×{e['reps']}"
                        if e['weight']:
                            line += f" @ {e['weight']}kg"
                            vol += e['sets'] * e['reps'] * e['weight']
                        st.write(line)
                    if vol:
                        st.metric("Total Volume Lifted", f"{vol:,.0f} kg")
            with col2:
                if st.button("🗑️", key=f"del_{real_idx}"):
                    hist.pop(real_idx)
                    write_json(HISTORY_PATH, hist)
                    st.success("Workout deleted!")
                    st.rerun()

st.caption("eCise Pro • Individual delete only • PDF • Custom titles • YouTube videos • 100% local & offline-ready")