# PurviewQuest_20_Scenes_WITH_FEEDBACK_FIXED.py
import streamlit as st
import os
import base64
import random

st.set_page_config(page_title="Microsoft Purview Quest", page_icon="cloud", layout="wide")

# ------------------------------------------------------------------
# Confetti
# ------------------------------------------------------------------
def confetti():
    st.markdown("""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <script>
    function launchConfetti() {
        var duration = 5 * 1000;
        var end = Date.now() + duration;
        (function frame() {
            confetti({ particleCount: 7, angle: 60, spread: 55, origin: { x: 0 } });
            confetti({ particleCount: 7, angle: 120, spread: 55, origin: { x: 1 } });
            if (Date.now() < end) requestAnimationFrame(frame);
        }());
    }
    launchConfetti();
    </script>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# CSS + Feedback Styling
# ------------------------------------------------------------------
st.markdown("""
<style>
    .header-block {text-align: center; margin: 60px 0 30px 0; line-height: 1.2;}
    .header-block img {vertical-align: middle; margin-right: 20px; width: 110px; height: auto;}
    .header-block h1 {display: inline-block; vertical-align: middle; margin: 0;
                      font-size: 3.8rem !important; font-weight: bold;
                      background: linear-gradient(90deg, #00d4ff, #0068ff);
                      -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .subtitle {text-align: center; font-size: 1.4rem; color: #bbb; margin: 10px 0 30px 0;}
    .scene-box {background: rgba(10,25,50,0.9); padding: 2rem; border-radius: 15px;
                border: 2px solid #00d4ff; box-shadow: 0 0 25px #00d4ff50; margin-bottom: 30px;}
    .day-badge {background: linear-gradient(90deg, #00d4ff, #0068ff); color: white; padding: 0.6rem 1.2rem;
                border-radius: 30px; font-size: 1.6rem; font-weight: bold;}
    .feedback-good {background: #0f5132; color: #d4edda; padding: 1rem; border-radius: 10px; margin: 10px 0; text-align: center; font-weight: bold;}
    .feedback-bad {background: #842029; color: #f8d7da; padding: 1rem; border-radius: 10px; margin: 10px 0; text-align: center; font-weight: bold;}
    .feedback-neutral {background: #664d03; color: #fff3cd; padding: 1rem; border-radius: 10px; margin: 10px 0; text-align: center; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# SESSION STATE – FIXED FOREVER!
# ------------------------------------------------------------------
if "compliance_score" not in st.session_state:
    st.session_state.compliance_score = 40
    st.session_state.risk = 80
    st.session_state.step = 0
    st.session_state.history = []
    st.session_state.last_feedback = None  # ← FIXED!

# ------------------------------------------------------------------
# LOGO – Always Works
# ------------------------------------------------------------------
logo_path = "ViewieSmall.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
        logo_data_url = f"data:image/png;base64,{logo_b64}"
else:
    logo_data_url = "https://via.placeholder.com/110x110/0068ff/ffffff?text=Viewie"

st.markdown(f"""
<div class="header-block">
    <img src="{logo_data_url}" width="110">
    <h1>Microsoft Purview Quest</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("<p class='subtitle'>30 days until audit • Can you save Zava from total compliance disaster?</p>", unsafe_allow_html=True)
st.divider()

# ------------------------------------------------------------------
# Metrics
# ------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    color = "#00ff9d" if st.session_state.compliance_score >= 70 else "#ff2d55"
    st.markdown(f"**Compliance**<br><span style='color:{color};font-size:1.8rem;font-weight:bold'>{st.session_state.compliance_score}/100</span>", unsafe_allow_html=True)
with c2:
    color = "#00ff9d" if st.session_state.risk <= 40 else "#ff2d55"
    st.markdown(f"**Risk Level**<br><span style='color:{color};font-size:1.8rem;font-weight:bold'>{st.session_state.risk}/100</span>", unsafe_allow_html=True)
with c3:
    day = max(1, 30 - st.session_state.step)
    st.markdown(f"<div class='day-badge'>Day {day}</div>", unsafe_allow_html=True)
with c4:
    st.progress(st.session_state.step / 20.0)

# ------------------------------------------------------------------
# Show Last Feedback
# ------------------------------------------------------------------
if st.session_state.last_feedback:
    feedback_text, is_good = st.session_state.last_feedback
    if is_good:
        st.markdown(f"<div class='feedback-good'>{feedback_text}</div>", unsafe_allow_html=True)
    elif "DISASTER" in feedback_text or "FIRED" in feedback_text:
        st.markdown(f"<div class='feedback-bad'>{feedback_text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='feedback-neutral'>{feedback_text}</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 20 FULL SCENES (All here!)
# ------------------------------------------------------------------
SCENES = [
    ("Sales shared a 5GB customer DB via personal Gmail.", [
        ("Activate DLP + sensitivity labels", 26, -24),
        ("Send a reminder email", -10, 18),
        ("Ignore – they’re trusted", -35, 40)
    ]),
    ("Finance deleting old records manually.", [
        ("Deploy retention policies + labels", 28, -26),
        ("Let them delete – saves cost", -38, 48),
        ("Tell them to zip and store", -15, 20)
    ]),
    ("Executive emailing credit card numbers.", [
        ("Enable Communication Compliance", 27, -22),
        ("Suggest password-protected ZIP", -30, 35),
        ("Forward to security", 10, -8)
    ]),
    ("Nightly data exfiltration detected.", [
        ("Enable Insider Risk Management", 30, -30),
        ("Run audit log search", 22, -18),
        ("It’s probably backups", -45, 55)
    ]),
    ("Auditors arrive in 72 hours!", [
        ("Run Information Protection scanner", 29, -25),
        ("Enable Data Map auto-classify", 27, -22),
        ("Update résumé", -60, 70)
    ]),
    ("Employee posting PII on LinkedIn.", [
        ("Block with DLP + train users", 28, -23),
        ("Like the post", -50, 60),
        ("Comment 'Great work!'", -55, 65)
    ]),
    ("Old SharePoint sites full of PII.", [
        ("Use Data Lifecycle + access reviews", 30, -27),
        ("Delete everything >5 years", -40, 50),
        ("Leave it alone", -45, 55)
    ]),
    ("Marketing using customer data for AI training.", [
        ("Apply trainable classifiers + block", 32, -30),
        ("Let them – innovation!", -55, 75),
        ("Ask to anonymize", 15, -10)
    ]),
    ("Legal needs all emails about 'Project Phoenix'.", [
        ("Use eDiscovery Premium + Content Search", 30, -25),
        ("Tell them to search Outlook", -45, 50),
        ("Say it was deleted", -70, 85)
    ]),
    ("Someone printing sensitive contracts.", [
        ("Enable DLP for printing + watermarking", 26, -20),
        ("Install printer locks", 10, 5),
        ("Nothing – paper is safe", -40, 45)
    ]),
    ("Old laptops being sold on eBay.", [
        ("Enforce device compliance + BitLocker", 28, -24),
        ("Wipe remotely", 20, -15),
        ("Trust the buyer", -50, 60)
    ]),
    ("Guest users have full access to SharePoint.", [
        ("Run Access Reviews + restrict guests", 27, -22),
        ("It’s fine – they’re partners", -40, 45),
        ("Remove all guests", 15, 10)
    ]),
    ("Teams chat exporting customer data.", [
        ("Enable DLP for Teams + retention", 29, -26),
        ("Block export", 25, -20),
        ("Allow – collaboration!", -45, 55)
    ]),
    ("Unclassified files in OneDrive.", [
        ("Auto-apply sensitivity labels", 30, -28),
        ("Manual labeling campaign", 15, -10),
        ("Ignore – users know best", -50, 60)
    ]),
    ("HR storing passports in public folder.", [
        ("Apply HR sensitivity label template", 32, -30),
        ("Move to secure location", 20, -15),
        ("It’s internal – no problem", -55, 70)
    ]),
    ("Vendor requesting full tenant access.", [
        ("Use Privileged Identity Management", 30, -25),
        ("Give them Global Admin", -70, 90),
        ("Say no", 20, 10)
    ]),
    ("Old service accounts with no owner.", [
        ("Run Inactive Account cleanup", 26, -20),
        ("Leave them – might be needed", -35, 40),
        ("Delete all", 15, 15)
    ]),
    ("Public Power BI reports with PII.", [
        ("Enable sensitivity labels in Power BI", 28, -24),
        ("Make them private", 20, -15),
        ("It’s just dashboards", -45, 55)
    ]),
    ("Contractor using personal device.", [
        ("Enforce Intune + conditional access", 30, -28),
        ("Allow – they’re trusted", -50, 65),
        ("Block all contractors", 10, 20)
    ]),
    ("Final audit day. The moment of truth.", [
        ("Open Purview – everything perfect", 40, -40),
        ("Panic and hide", -80, 100),
        ("Offer auditors coffee", -20, 25)
    ])
]

# ------------------------------------------------------------------
# Game Over
# ------------------------------------------------------------------
if st.session_state.step >= len(SCENES):
    confetti()
    if st.session_state.compliance_score >= 85 and st.session_state.risk <= 35:
        st.success("LEGENDARY VICTORY! CISO OF THE YEAR! VIEWIE FOREVER!")
    elif st.session_state.compliance_score >= 60:
        st.warning("You survived! Zava is compliant… barely.")
    else:
        st.error("FIRED. Viewie is crying in the cloud.")

    st.markdown(f"""
    <div class='scene-box' style='text-align:center;font-size:1.5rem'>
        <strong>FINAL RESULT</strong><br><br>
        Compliance: {st.session_state.compliance_score}/100<br>
        Risk Level: {st.session_state.risk}/100<br><br>
        <em>Your path:</em><br>
        {' → '.join(st.session_state.history)}
    </div>
    """, unsafe_allow_html=True)

    if st.button("New Quest – Play Again", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.stop()

# ------------------------------------------------------------------
# Current Scene + INSTANT FEEDBACK
# ------------------------------------------------------------------
scene_text, choices = SCENES[st.session_state.step]
shuffled = choices.copy()
random.shuffle(shuffled)

st.markdown(f"<div class='scene-box'><strong>Day {30 - st.session_state.step}</strong><br><br>{scene_text}</div>", unsafe_allow_html=True)
st.markdown("### Your Move")

cols = st.columns(3)
for i, (text, comp, risk) in enumerate(shuffled):
    with cols[i]:
        if st.button(text, key=text, use_container_width=True):
            # Feedback logic
            if comp >= 25 and risk <= -20:
                feedback = f"EXCELLENT! Best Purview practice! (+{comp} Compliance, {risk} Risk)"
                good = True
            elif comp >= 15:
                feedback = f"SOLID CHOICE! Good move. (+{comp} Compliance, {risk:+} Risk)"
                good = True
            elif comp >= 0:
                feedback = f"OKAY… could be better. (+{comp} Compliance, {risk:+} Risk)"
                good = False
            elif risk >= 50:
                feedback = f"DISASTER! This will cost millions! ({comp:+} Compliance, +{risk} Risk)"
                good = False
            else:
                feedback = f"RISKY MOVE! ({comp:+} Compliance, +{risk} Risk)"
                good = False

            st.session_state.last_feedback = (feedback, good)
            st.session_state.history.append(text)
            st.session_state.compliance_score = max(0, min(100, st.session_state.compliance_score + comp))
            st.session_state.risk = max(0, min(100, st.session_state.risk + risk))
            st.session_state.step += 1
            st.rerun()

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    st.header("Zava Audit Trail")
    for h in st.session_state.history:
        st.write(f"• {h}")
    st.caption("20 Scenes • Instant Feedback • Perfect")

st.caption("Microsoft Purview Quest • Viewie Approved")