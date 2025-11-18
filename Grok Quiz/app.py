import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import json
import os

from utils.flashcard_generator import extract_text_from_pdf, generate_flashcards
from utils.anki_export import export_to_anki

st.set_page_config(page_title="Grok Flashcard & Quiz Master", layout="wide")
st.title("🧠 Grok-Powered Flashcard & Quiz Master")

# Session state initialization
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "review_log" not in st.session_state:
    st.session_state.review_log = {}  # card_front -> {"last": datetime, "interval": 1, "ef": 2.5}
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "quiz_total" not in st.session_state:
    st.session_state.quiz_total = 0

tab1, tab2, tab3 = st.tabs(["📤 Upload & Generate", "🃏 Review Flashcards", "🧪 Adaptive Quiz"])

with tab1:
    st.header("Upload PDF or Enter Topic")
    uploaded_file = st.file_uploader("Upload textbook PDF", type="pdf")
    topic = st.text_area("Or just type a topic/subject (e.g., Quantum Mechanics, Python OOP, World War II)")

    num_cards = st.slider("Number of flashcards", 10, 100, 30)

    if st.button("🚀 Generate Flashcards with Grok"):
        if not uploaded_file and not topic:
            st.error("Please upload a PDF or enter a topic")
        else:
            with st.spinner("Grok is reading and generating flashcards..."):
                if uploaded_file:
                    text = extract_text_from_pdf(uploaded_file)
                    st.success(f"Extracted {len(text)} characters from PDF")
                else:
                    text = topic

                cards = generate_flashcards(text, num_cards)
                st.session_state.flashcards = cards
                st.success(f"Generated {len(cards)} flashcards!")

                df = pd.DataFrame(cards)
                st.dataframe(df, use_container_width=True)

                # Export options
                col1, col2 = st.columns(2)
                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button("Download CSV", csv, "flashcards.csv", "text/csv")
                with col2:
                    if st.button("Export to Anki (.apkg)"):
                        path = export_to_anki(f"Grok Deck - {topic[:30]}", cards)
                        with open(path, "rb") as f:
                            st.download_button("Download Anki Deck", f, os.path.basename(path), "application/octet-stream")
                        os.unlink(path)

with tab2:
    st.header("Spaced Repetition Review")
    if not st.session_state.flashcards:
        st.info("Generate flashcards first!")
    else:
        now = datetime.now()
        due_cards = []
        for card in st.session_state.flashcards:
            key = card["front"]
            log = st.session_state.review_log.get(key, {"last": None, "interval": 0, "ef": 2.5})
            if not log["last"] or (now - log["last"]).days >= log["interval"]:
                due_cards.append((card, key))

        if not due_cards:
            st.balloons()
            st.success("🎉 You're all caught up!")
        else:
            card, key = due_cards[0]
            with st.container():
                st.subheader("Card")
                st.markdown(f"**Q:** {card['front']}")
                if st.button("Show Answer"):
                    st.markdown(f"**A:** {card['back']}")
                    col1, col2, col3 = st.columns(3)
                    if col1.button("Again (1 day)"):
                        st.session_state.review_log[key] = {"last": now, "interval": 1, "ef": 1.3}
                        st.rerun()
                    if col2.button("Good"):
                        interval = max(1, int(log["interval"] * log["ef"]))
                        st.session_state.review_log[key] = {"last": now, "interval": interval, "ef": log["ef"]}
                        st.rerun()
                    if col3.button("Easy (10+ days)"):
                        interval = max(10, int(log["interval"] * log["ef"] * 1.3))
                        st.session_state.review_log[key] = {"last": now, "interval": interval, "ef": log["ef"] + 0.2}
                        st.rerun()

            st.write(f"{len(due_cards)-1} more cards due today")

with tab3:
    st.header("Adaptive Quiz Mode")
    if not st.session_state.flashcards:
        st.info("Generate flashcards first!")
    else:
        if st.button("Start 10-Question Quiz"):
            st.session_state.quiz_cards = st.session_state.flashcards.copy()
            import random
            random.shuffle(st.session_state.quiz_cards)
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_total = 0
            st.session_state.show_answer = False

        if "quiz_index" in st.session_state:
            idx = st.session_state.quiz_index
            total_questions = 10

            if idx >= total_questions:
                accuracy = st.session_state.quiz_score / st.session_state.quiz_total
                st.success(f"Quiz Complete! Score: {st.session_state.quiz_score}/{st.session_state.quiz_total} ({accuracy:.0%})")
                if accuracy < 0.6:
                    st.warning("Struggling? Let's review weak areas next time.")
                elif accuracy < 0.8:
                    st.info("Good effort! Keep practicing.")
                else:
                    st.balloons()
                    st.success("Excellent! You're mastering this topic!")

                if st.button("New Quiz"):
                    st.rerun()
            else:
                card = st.session_state.quiz_cards[idx]
                st.write(f"Question {idx+1}/{total_questions}")
                st.markdown(f"**Q:** {card['front']}")

                user_answer = st.text_input("Your answer:", key=f"q{idx}")
                if st.button("Submit Answer"):
                    st.session_state.show_answer = True
                    st.markdown(f"**Correct Answer:** {card['back']}")

                    if user_answer.strip().lower() in card["back"].lower() or len(user_answer) > 10:
                        st.success("Correct!")
                        st.session_state.quiz_score += 1
                    else:
                        st.error("Incorrect")
                    st.session_state.quiz_total += 1

                    if st.button("Next Question"):
                        st.session_state.quiz_index += 1
                        st.session_state.show_answer = False
                        st.rerun()