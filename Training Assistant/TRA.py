import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
from utils.grok_client import grok_chat
from utils.pdf_processor import extract_text_from_pdf
from utils.generators import create_anki_deck, generate_mindmap

st.set_page_config(page_title="Training Assistant", layout="wide")
st.title("Training Research Assistant")
st.markdown("### Powered by Grok")

# Session state
if "ready" not in st.session_state:
    st.session_state.ready = False
    st.session_state.topic = ""
    st.session_state.sections = {}
    st.session_state.deck = None

# Sidebar
with st.sidebar:
    mode = st.radio("Mode", ["Topic Only", "Upload PDF"])
    if mode == "Topic Only":
        topic = st.text_input("Enter topic", "Example: Azure AZ-104")
    else:
        uploaded_file = st.file_uploader("Upload textbook PDF", type="pdf")
        topic = st.text_input("Topic name", "My Course")
    go = st.button("Generate Package", type="primary")

# Grok call
def ask_grok(prompt):
    try:
        resp = grok_chat([{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    except:
        return "Error: Could not reach Grok."

# Fresh YouTube — 100% real
def get_youtube(topic):
    try:
        q = topic.replace(" ", "+") + "+tutorial+OR+course+site:youtube.com"
        r = requests.get(f"https://www.google.com/search?q={q}", 
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True)[:15]:
            h = a["href"]
            if "youtube.com/watch" in h and "/url?q=" in h:
                url = h.split("/url?q=")[1].split("&")[0]
                title = a.get_text(strip=True)[:80]
                links.append(f"- [{title}]({url})")
        return links[:8] or [f"- [Search: {topic} on YouTube](https://youtube.com/results?search_query={topic.replace(' ', '+')})"]
    except:
        return [f"- [Search: {topic} on YouTube](https://youtube.com/results?search_query={topic.replace(' ', '+')})"]

# Generate only once
if go and not st.session_state.ready:
    if not topic.strip():
        st.error("Enter a topic!")
        st.stop()

    with st.spinner("Grok-4 is creating your full training package..."):
        pdf = ""
        if "Upload" in mode and uploaded_file:
            pdf = extract_text_from_pdf(uploaded_file)

        # NO TRIPLE QUOTES — ONLY SAFE STRING CONCAT
        prompt = (
            "Create a complete training package for: " + topic + "\n\n" +
            ("Use this textbook content:\n" + pdf[:28000] if pdf else "") +
            "\n\nReply with exactly these sections:\n\n" +
            "## Mind Map JSON\n```json\n{\"title\": \"" + topic + "\", \"children\": [...]}\n```\n\n" +
            "## 8-Week Training Plan\nDaily schedule.\n\n" +
            "## Practice Exams & Labs\nBest resources.\n\n" +
            "## Flashcards\n50 Anki cards as list:\n[[\"Q1\",\"A1\"],[\"Q2\",\"A2\"],...]"
        )

        answer = ask_grok(prompt)

        sec = {"Mind Map JSON": "", "8-Week Training Plan": "", "Practice Exams & Labs": "", "Flashcards": ""}
        cur = None
        for line in answer.splitlines():
            if line.startswith("## "):
                h = line[3:].strip()
                cur = "8-Week Training Plan" if "8-Week" in h else "Practice Exams & Labs" if "Practice" in h or "Labs" in h else h
            elif cur in sec:
                sec[cur] += line + "\n"

        # Fresh YouTube
        yt = get_youtube(topic)
        sec["YouTube Resources"] = "## YouTube Resources\nLatest videos:\n\n" + "\n".join(yt)

        # Flashcards
        cards = []
        raw = sec["Flashcards"]
        if raw.startswith("["):
            try:
                data = json.loads(raw)
                for x in data:
                    if len(x) >= 2:
                        cards.append((str(x[0]), str(x[1]), ""))
            except: pass

        # Anki deck
        deck_file = None
        if cards:
            deck_file = create_anki_deck(topic, cards[:200])

        # Save to session
        st.session_state.update({
            "ready": True,
            "topic": topic,
            "sections": sec,
            "deck": deck_file
        })

# Display — stays forever
if st.session_state.ready:
    sec = st.session_state.sections
    topic = st.session_state.topic

    st.success("Package ready!")

    c1, c2 = st.columns([1.4, 1])

    with c1:
        st.subheader("Mind Map")
        j = sec.get("Mind Map JSON", "")
        if "```json" in j:
            j = j.split("```json")[1].split("```")[0].strip()
        try:
            st.plotly_chart(generate_mindmap(topic, json.loads(j)), use_container_width=True)
        except:
            st.code(j[:1000])

        st.subheader("8-Week Plan")
        st.markdown(sec.get("8-Week Training Plan", "_none_"))

        st.subheader("Fresh YouTube Videos")
        st.markdown(sec["YouTube Resources"])

    with c2:
        st.subheader("Anki Flashcards")
        if st.session_state.deck:
            with open(st.session_state.deck, "rb") as f:
                st.download_button("Download Anki Deck", f, st.session_state.deck)
        else:
            st.info("No cards")

        st.subheader("Practice Exams & Labs")
        st.markdown(sec.get("Practice Exams & Labs", "_none_"))

    full = "# " + topic + "\n\n"
    for t,c in sec.items():
        if c.strip():
            full += "## " + t + "\n" + c + "\n\n"
    st.download_button("Download Full Plan", full, f"{topic.replace(' ','_')}_Plan.md", "text/markdown")

    if st.button("New Package"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

else:
    st.info("Enter a topic → click Generate → get your full package instantly")