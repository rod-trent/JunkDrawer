import streamlit as st
import requests
import json
import os
import time
import subprocess
import sys
import psutil
from croniter import croniter
from datetime import datetime
from dotenv import load_dotenv

# ====================== SCRIPT DIRECTORY ======================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(SCRIPT_DIR, "agents"), exist_ok=True)
os.makedirs(os.path.join(SCRIPT_DIR, ".triggers"), exist_ok=True)

REGISTRY_FILE = os.path.join(SCRIPT_DIR, "agent_registry.json")
PID_FILE = os.path.join(SCRIPT_DIR, ".worker_pid")

load_dotenv()

st.sidebar.success(f"Everything saved here:\n`{SCRIPT_DIR}`")

# ========================= REGISTRY =========================
def load_registry():
    if not os.path.exists(REGISTRY_FILE):
        return []
    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except:
        return []

def save_registry(registry):
    try:
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)
        st.sidebar.success("agent_registry.json saved!")
    except Exception as e:
        st.sidebar.error(f"Save failed: {e}")

# ========================= WORKER =========================
def get_worker_pid():
    if not os.path.exists(PID_FILE):
        return None
    try:
        pid = int(open(PID_FILE).read().strip())
        p = psutil.Process(pid)
        return pid if p.is_running() and p.status() != psutil.STATUS_ZOMBIE else None
    except:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return None

def start_worker():
    if get_worker_pid():
        return True

    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS if os.name == "nt" else 0

    proc = subprocess.Popen(
        [sys.executable, "background_worker.py"],
        cwd=SCRIPT_DIR,
        creationflags=creationflags,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        shell=False
    )

    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))

    time.sleep(2)
    return get_worker_pid() is not None

def stop_worker():
    pid = get_worker_pid()
    if pid:
        try:
            if os.name == "nt":
                subprocess.call(['taskkill', '/F', '/PID', str(pid)], stdout=subprocess.DEVNULL)
            else:
                os.kill(pid, 9)
        except:
            pass
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

# ========================= SAFE AUTO-REFRESH =========================
worker_pid = get_worker_pid()

if worker_pid:
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = 0
    if time.time() - st.session_state.last_refresh > 15:
        st.session_state.last_refresh = time.time()
        st.rerun()

# ========================= UI =========================
st.set_page_config(page_title="Grok Agent Platform", layout="wide")
st.title("🦾 Grok Agent Platform")
st.caption("PID Display • User-Friendly Scheduler • Final Final Final • November 20, 2025")

# === WORKER STATUS WITH PID ===
status_text = f"**Worker**: 🟢 Running — PID `{worker_pid}`" if worker_pid else "**Worker**: 🔴 Stopped"

c1, c2 = st.sidebar.columns([5, 2])
with c1:
    st.markdown(status_text)
with c2:
    if worker_pid:
        if st.button("STOP Worker", key="stop_worker"):
            stop_worker()
            st.rerun()
    else:
        if st.button("START Worker", key="start_worker"):
            start_worker()
            st.rerun()

# ========================= ADD NEW AGENT - FRIENDLY DROPDOWN =========================
st.sidebar.header("Add New Agent")

with st.sidebar.form(key="add_agent_form", clear_on_submit=True):
    agent_name = st.text_input("Agent Name", placeholder="WeatherBot")
    source = st.radio("Source", ["Local Upload", "Remote URL"])

    uploaded_file = None
    url = None

    if source == "Local Upload":
        uploaded_file = st.file_uploader("Upload agent.py", type="py")
    else:
        url = st.text_input("Raw .py URL (GitHub raw, etc.)")

    # ------------------ Friendly Schedule Selector ------------------
    schedule_options = {
        "Every 5 minutes": "*/5 * * * *",
        "Every 10 minutes": "*/10 * * * *",
        "Every 15 minutes": "*/15 * * * *",
        "Every 30 minutes": "0,30 * * * *",
        "Every hour (at minute 0)": "0 * * * *",
        "Every 2 hours": "0 */2 * * *",
        "Every 6 hours": "0 */6 * * *",
        "Every 12 hours": "0 */12 * * *",
        "Once per day at midnight": "0 0 * * *",
        "Once per day at 8 AM": "0 8 * * *",
        "Once per day at 6 PM": "0 18 * * *",
        "Weekdays at 9 AM": "0 9 * * 1-5",
        "Mondays at 9 AM": "0 9 * * 1",
        "Custom cron expression": "custom"
    }

    selected = st.selectbox("Schedule", options=list(schedule_options.keys()), index=1)

    cron_expr = schedule_options[selected]

    if selected == "Custom cron expression":
        cron_expr = st.text_input(
            "Enter custom cron",
            value="*/10 * * * *",
            help="Minute Hour Day Month Weekday → e.g. 0 22 * * * = every day at 10 PM"
        )
    else:
        st.info(f"cron: `{cron_expr}`")

    submit_button = st.form_submit_button("🚀 SAVE + REGISTER AGENT", type="primary", use_container_width=True)

    if submit_button:
        if not agent_name.strip():
            st.error("Agent name is required")
        elif not croniter.is_valid(cron_expr):
            st.error("Invalid cron expression")
        elif source == "Local Upload" and not uploaded_file:
            st.error("Please upload a file")
        elif source == "Remote URL" and not url.strip():
            st.error("Please enter a URL")
        else:
            saved_path = os.path.join(SCRIPT_DIR, "agents", f"{agent_name}.py")

            if source == "Local Upload":
                with open(saved_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            else:
                try:
                    r = requests.get(url, timeout=15)
                    r.raise_for_status()
                    with open(saved_path, "w", encoding="utf-8") as f:
                        f.write(r.text)
                except Exception as e:
                    st.error(f"Download failed: {e}")
                    saved_path = None

            if saved_path and os.path.exists(saved_path):
                registry = load_registry()
                if any(a.get("name") == agent_name for a in registry):
                    st.error("Agent name already exists!")
                else:
                    registry.append({
                        "name": agent_name,
                        "path": saved_path,
                        "enabled": True,
                        "schedule": cron_expr.strip(),
                        "last_run": None
                    })
                    save_registry(registry)
                    st.success(f"Agent **{agent_name}** registered and saved!")
                    st.balloons()
            else:
                st.error("Failed to save agent file")

# ========================= ACTIVE AGENTS =========================
st.header("Active Agents")

registry = load_registry()
if not registry:
    st.info("No agents registered yet. Use the sidebar to add one!")
else:
    for agent in registry[:]:
        name = agent["name"]
        enabled = agent.get("enabled", True)
        sched = agent.get("schedule", "—")
        path = os.path.basename(agent["path"])
        
        status = "Idle"
        status_file = os.path.join(SCRIPT_DIR, f".status_{name}")
        if os.path.exists(status_file):
            try:
                with open(status_file) as f:
                    status = f.read().strip().split("|")[0]
            except:
                pass

        with st.expander(f"{'🟢' if enabled else '🔴'} **{name}** • {sched} • **{status}**", expanded=True):
            c1, c2, c3, c4 = st.columns([4, 2, 2, 2])
            with c1:
                st.code(path, language=None)
            with c2:
                toggled = st.toggle("Enabled", value=enabled, key=f"toggle_{name}")
                if toggled != enabled:
                    agent["enabled"] = toggled
                    save_registry(registry)
                    st.rerun()
            with c3:
                if st.button("Run Now", key=f"run_{name}"):
                    open(os.path.join(SCRIPT_DIR, ".triggers", f".trigger_{name}"), "a").close()
                    st.success("Triggered!")
            with c4:
                if st.button("Delete", key=f"del_{name}", type="secondary"):
                    for f in [agent["path"], status_file, os.path.join(SCRIPT_DIR, ".triggers", f".trigger_{name}")]:
                        if os.path.exists(f):
                            try:
                                os.remove(f)
                            except:
                                pass
                    registry = [a for a in registry if a["name"] != name]
                    save_registry(registry)
                    st.rerun()

# Manual refresh when worker is off
if not worker_pid:
    if st.button("🔄 Manual Refresh"):
        st.rerun()

st.caption("Grok Agent Platform • PID + Friendly Scheduler Edition • Absolutely Final • November 20, 2025 🦾")