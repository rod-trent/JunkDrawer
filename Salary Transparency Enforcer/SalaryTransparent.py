import streamlit as st
import requests
import re
import os
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    st.error("GROK_API_KEY missing. Get one at https://x.ai/api")
    st.stop()

GROK_API_URL = "https://api.x.ai/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
SCRAPE_HEADERS = {"User-Agent": "Mozilla/5.0"}

# === FINAL EMAIL FORMATTER ===
def format_email_perfectly(raw_text):
    if not raw_text:
        return "Subject: Counter-Offer\n\n[Email body failed to generate]"

    # Remove any stray markdown junk
    text = re.sub(r'\*{1,3}', '', raw_text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'`', '', text)

    # Split into lines and clean
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    subject = "Counter-Offer"
    body_lines = []
    in_body = False

    for line in lines:
        if line.lower().startswith("subject:"):
            subject = line.replace("Subject:", "").replace("subject:", "").strip()
        elif "Dear" in line or "Hi" in line or "Hello" in line:
            in_body = True
            body_lines.append(line)
        elif in_body:
            body_lines.append(line)

    # Ensure proper paragraph spacing
    formatted_body = ""
    current_para = []

    for line in body_lines:
        if line.lower().startswith(("best regards", "thank you", "sincerely", "warm regards", "kind regards")):
            if current_para:
                formatted_body += " ".join(current_para) + "\n\n"
                current_para = []
            formatted_body += line + "\n"
        elif line == "":
            if current_para:
                formatted_body += " ".join(current_para) + "\n\n"
                current_para = []
        else:
            current_para.append(line)

    if current_para:
        formatted_body += " ".join(current_para) + "\n\n"

    return f"**Subject:** {subject}\n\n{formatted_body.strip()}"

# === STYLE ===
st.set_page_config(page_title="Salary Transparency Enforcer", page_icon="money", layout="centered")
st.markdown("""
<style>
    .big-title {font-size: 2.6rem !important; font-weight: 800; text-align: center;}
    .subtitle {font-size: 1.2rem !important; text-align: center; color: #aaa; margin-bottom: 2rem;}
    .job-detail {font-size: 1.4rem !important; font-weight: 600;}
    .email-box {
        background-color: #0e1117; padding: 32px; border-radius: 12px;
        border-left: 6px solid #00ff9d; font-size: 1.15rem; line-height: 2;
        font-family: 'Segoe UI', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="big-title">Salary Transparency Enforcer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Powered 100% by Grok-4</p>', unsafe_allow_html=True)

def grok_call(prompt, max_tokens=600, temp=0.7):
    payload = {"model": "grok-4", "messages": [{"role": "user", "content": prompt}],
               "temperature": temp, "max_tokens": max_tokens}
    for _ in range(3):
        try:
            r = requests.post(GROK_API_URL, json=payload, headers=HEADERS, timeout=120)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except:
            pass
    st.error("Grok unreachable.")
    st.stop()

if "job" not in st.session_state: st.session_state.job = None
if "salary" not in st.session_state: st.session_state.salary = None

tab1, tab2 = st.tabs(["Paste Text", "Scrape URL"])

with tab1:
    text = st.text_area("Paste full job description:", height=300, label_visibility="collapsed")
    if st.button("Step 1 → Parse with Grok", type="primary", use_container_width=True):
        if text:
            with st.spinner("Parsing..."):
                content = grok_call(f"Extract ONLY JSON: {{'company':'','title':'','location':'','hides_salary':true/false}}\nText: {text[:12000]}", 300, 0.1)
                m = re.search(r'\{.*\}', content, re.DOTALL)
                st.session_state.job = json.loads(m.group(0))
                st.rerun()

with tab2:
    url = st.text_input("Or paste job URL:", label_visibility="collapsed")
    if st.button("Step 1 → Scrape & Parse", type="primary", use_container_width=True):
        if url:
            with st.spinner("Scraping..."):
                try:
                    s = requests.Session()
                    s.headers.update(SCRAPE_HEADERS)
                    r = s.get(url, timeout=40, allow_redirects=True)
                    r.raise_for_status()
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for t in soup(["script", "style", "nav", "footer", "aside"]):
                        t.decompose()
                    page_text = soup.get_text(separator=" ", strip=True)
                except:
                    st.error("Scrape failed. Paste text instead.")
                    st.stop()
            with st.spinner("Grok parsing..."):
                content = grok_call(f"Extract ONLY JSON: {{'company':'','title':'','location':'','hides_salary':true/false}}\nText: {page_text[:12000]}", 300, 0.1)
                m = re.search(r'\{.*\}', content, re.DOTALL)
                st.session_state.job = json.loads(m.group(0))
                st.rerun()

if st.session_state.job:
    job = st.session_state.job
    st.success("Job Parsed")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<p class='job-detail'>Company<br><b>{job['company']}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<p class='job-detail'>Role<br><b>{job['title']}</b></p>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<p class='job-detail'>Location<br><b>{job['location']}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<p class='job-detail'>Hides Salary?<br><b>{'Yes' if job['hides_salary'] else 'No'}</b></p>", unsafe_allow_html=True)

    if job['hides_salary']:
        st.warning("They’re hiding the salary — time to fight back.")

    if not st.session_state.salary:
        if st.button("Step 2 → Get Real Salary Data", type="primary", use_container_width=True):
            with st.spinner("Researching 2025 data..."):
                data = grok_call(f"Latest 2025 salary for {job['title']} at {job['company']} in {job['location']}. Return ONLY JSON: {{'base':int,'total_comp':int,'low':int,'high':int,'source':'string'}}", 250, 0.3)
                m = re.search(r'\{.*\}', data, re.DOTALL)
                st.session_state.salary = json.loads(m.group(0))
                st.rerun()
    else:
        salary = st.session_state.salary
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Base", f"${salary['base']:,}")
        col2.metric("Total Comp", f"${salary['total_comp']:,}")
        col3.metric("Range", f"${salary['low']:,}–${salary['high']:,}")
        st.caption(f"Source: {salary['source']}")

        st.divider()
        offer = st.number_input("Their offer (base salary)", min_value=50000, value=135000, step=5000)

        if st.button("Generate Counter-Offer Email", type="primary", use_container_width=True):
            with st.spinner("Grok writing your perfect email..."):
                raw = grok_call(f"""
                Write a professional counter-offer email.
                Start with: Subject: Counter-Offer for [Title] at [Company]
                Then greeting, 3-4 short paragraphs, closing.
                Counter 20-25% above ${offer:,}.
                Market data: base ${salary['base']:,}, total ${salary['total_comp']:,}.
                Tone: grateful, confident, data-driven.
                End with Best regards, [Your Name]
                """, 700, 0.7)
                email = format_email_perfectly(raw)

            st.subheader("Your Counter-Offer Email")
            st.markdown(f"<div class='email-box'>{email.replace('**', '<b>').replace('**', '</b>')}</div>", unsafe_allow_html=True)
            st.download_button("Download Draft", email,
                              file_name=f"Counter_{job['company']}_{job['title'][:20].replace(' ', '')}.txt",
                              mime="text/plain")
            st.balloons()
            st.success("Perfect, human-readable email — ready to send!")

else:
    st.info("Paste job text or URL → Step 1")

st.caption("Powered by Grok-4")