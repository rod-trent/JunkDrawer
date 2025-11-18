import streamlit as st
import pandas as pd
from datetime import datetime
import os
import random

from utils.flashcard_generator import extract_text_from_pdf, generate_flashcards
from utils.anki_export import export_to_anki

st.set_page_config(page_title="Grok Flashcard & Quiz Master", layout="wide")
st.title("🧠 Grok Flashcard & Quiz Master")
st.caption("Because manually making Anki cards is so 2024")

# Session state
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "review_log" not in st.session_state:
    st.session_state.review_log = {}

tab1, tab2, tab3 = st.tabs(["📤 Generate Cards", "🃏 Spaced Repetition", "🧪 Adaptive Quiz"])

# ====================== TAB 1: Generate ======================
with tab1:
    st.header("Upload PDF or Type a Topic")
    uploaded_file = st.file_uploader("Textbook PDF", type="pdf")
    topic = st.text_area("Or just describe the topic (e.g., Quantum Computing, Roman History, Django)")

    num_cards = st.slider("How many flashcards?", 10, 100, 40)

    if st.button("🚀 Generate with Grok", type="primary", use_container_width=True):
        if not uploaded_file and not topic:
            st.error("Upload a PDF or type a topic!")
        else:
            with st.spinner("Grok is reading and creating perfect cards..."):
                if uploaded_file:
                    text = extract_text_from_pdf(uploaded_file)
                    st.success(f"Extracted {len(text):,} characters")
                else:
                    text = topic

                cards = generate_flashcards(text, num_cards)
                st.session_state.flashcards = cards
                st.success(f"Generated {len(cards)} amazing flashcards!")

                df = pd.DataFrame(cards)
                st.dataframe(df, width="stretch")  # Fixed for 2026+

                # Exports
                col1, col2 = st.columns(2)
                with col1:
                    csv = df.to_csv(index=False).encode()
                    st.download_button("📄 Download CSV", csv, "flashcards.csv", "text/csv")

                with col2:
                    deck_name = (topic or uploaded_file.name).split(".")[0][:50]
                    if st.button("🃏 Export to Anki (.apkg)"):
                        path = export_to_anki(f"Grok - {deck_name}", cards)
                        with open(path, "rb") as f:
                            st.download_button("Download Anki Deck", f, f"{deck_name}.apkg", "application/octet-stream")
                        os.unlink(path)

# ====================== TAB 2: Review ======================
with tab2:
    st.header("Spaced Repetition Review")
    if not st.session_state.flashcards:
        st.info("Generate some cards first!")
    else:
        now = datetime.now()
        due = []
        for card in st.session_state.flashcards:
            key = card["front"]
            log = st.session_state.review_log.get(key, {"last": None, "interval": 0, "ef": 2.5})
            if not log["last"] or (now - log["last"]).days >= log["interval"]:
                due.append((card, key, log))

        if not due:
            st.balloons()
            st.success("You're all caught up! Come back tomorrow 🎉")
        else:
            card, key, log = due[0]
            st.subheader("Due Card")
            st.markdown(f"**Q:** {card['front']}")
            if st.button("👁 Show Answer"):
                st.markdown(f"**A:** {card['back']}")
                c1, c2, c3 = st.columns(3)
                if c1.button("Again 😅"):
                    st.session_state.review_log[key] = {"last": now, "interval": 1, "ef": max(1.3, log["ef"]-0.2)}
                    st.rerun()
                if c2.button("Good ✅"):
                    new_interval = max(1, int(log["interval"] * log["ef"]))
                    st.session_state.review_log[key] = {"last": now, "interval": new_interval, "ef": log["ef"]}
                    st.rerun()
                if c3.button("Easy 🏆"):
                    new_interval = max(6, int(log["interval"] * log["ef"] * 1.3))
                    st.session_state.review_log[key] = {"last": now, "interval": new_interval, "ef": log["ef"]+0.15}
                    st.rerun()

            st.caption(f"{len(due)-1} more due today • Total cards: {len(st.session_state.flashcards)}")

# ====================== TAB 3: Quiz ======================
with tab3:
    st.header("Adaptive Quiz Mode")
    if not st.session_state.flashcards:
        st.info("Generate cards first!")
    else:
        if st.button("Start 10-Question Quiz", type="primary"):
            st.session_state.quiz_cards = random.sample(st.session_state.flashcards, len(st.session_state.flashcards))
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_total = 0

        if "quiz_idx" in st.session_state:
            idx = st.session_state.quiz_idx
            if idx >= 10:
                acc = st.session_state.quiz_score / 10
                st.success(f"Quiz finished! {st.session_state.quiz_score}/10 ({acc:.0%})")
                if acc >= 0.9: st.balloons()
                if st.button("Another Quiz"): st.rerun()
            else:
                card = st.session_state.quiz_cards[idx]
                st.write(f"### Question {idx+1}/10")
                st.markdown(f"**{card['front']}**")
                ans = st.text_input("Your answer", key=f"ans{idx}")
                if st.button("Submit"):
                    if ans.strip().lower() in card["back"].lower() or len(ans) > 15:
                        st.success("Correct!")
                        st.session_state.quiz_score += 1
                    else:
                        st.error(f"Wrong. Correct: {card['back']}")
                    st.session_state.quiz_total += 1
                    if st.button("Next →"):
                        st.session_state.quiz_idx += 1
                        st.rerun()