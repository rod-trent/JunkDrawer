import streamlit as st
import os
import requests
from dotenv import load_dotenv
import base64
import extra_streamlit_components as stx  # Kept for future use, but not needed here
import time
import streamlit.components.v1 as components  # For html rendering

# Load .env
load_dotenv()

# === CONFIG ===
GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    st.error("Please set GROK_API_KEY in your .env file")
    st.stop()

GROK_API_URL = "https://api.x.ai/v1/chat/completions"

st.set_page_config(page_title="Grok IR Playbook Generator", layout="wide")
st.title("Automated Incident Response Playbook Generator")
st.markdown("##### Powered by **Grok 4** (xAI) • MITRE ATT&CK • Adaptive Playbooks")

# Sidebar
with st.sidebar:
    st.header("Incident Input")
    incident_summary = st.text_area(
        "Incident Summary",
        placeholder="e.g., Ransomware encryption detected across 200+ endpoints, Cobalt Strike beacons observed",
        height=120
    )

    additional_context = st.text_area(
        "Additional Context (Optional)",
        placeholder="• Environment: Windows + Active Directory\n• Tools: Splunk, SentinelOne\n• Known TTPs: T1078, T1003.001",
        height=120
    )

    sophistication = st.selectbox(
        "Attacker Sophistication",
        ["Low", "Medium", "High", "Nation-State"],
        index=2
    )

    selected_model = st.selectbox(
        "Grok Model",
        ["grok-4", "grok-4.1", "grok-beta"],
        index=0
    )

    st.markdown("---")
    generate = st.button("Generate Playbook", type="primary", use_container_width=True)

# Main layout
col_main, col_flow = st.columns([2.2, 1.3])

if generate and incident_summary.strip():
    with st.spinner("Grok is building your incident response playbook..."):
        system_prompt = """You are a senior incident response commander and MITRE ATT&CK expert.
Generate highly actionable, enterprise-grade playbooks with clear phases, decision trees, and containment options.
Always include a Mermaid flowchart (flowchart TD syntax) at the end.
Use professional, concise language. Prioritize speed in ransomware and credential theft scenarios."""

        user_prompt = f"""Incident: {incident_summary}
Context: {additional_context or "Not provided"}
Attacker Level: {sophistication}

Generate a full playbook with:
1. Executive Summary
2. Initial Triage & Detection
3. Containment (Immediate + Full)
4. Eradication
5. Recovery & Hardening
6. Decision Branches
7. MITRE ATT&CK Mapping Table
8. Mermaid Flowchart (flowchart TD style)

Output in clean Markdown."""

        payload = {
            "model": selected_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4096
        }

        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }

        # Retry logic
        for attempt in range(3):
            try:
                resp = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=180)

                # Specific 404 handling with clean message
                if resp.status_code == 404:
                    st.error(
                        "### API 404 Error\n"
                        "Most common causes:\n"
                        "- Your API key is old/expired → **Regenerate it** at https://console.x.ai\n"
                        "- The model name is no longer supported → Try **grok-4** or **grok-4.1**\n"
                        "- Key created without Chat Completions permission → Create a new key and enable it\n\n"
                        "**Quick test command (run in terminal):**\n"
                        "```bash\n"
                        f"curl https://api.x.ai/v1/chat/completions \\\n"
                        f"  -H \"Authorization: Bearer {GROK_API_KEY[:10]}...\" \\\n"
                        "  -H \"Content-Type: application/json\" \\\n"
                        "  -d '{{\"model\":\"grok-4\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}}'\n"
                        "```"
                    )
                    st.stop()

                resp.raise_for_status()
                result = resp.json()
                full_response = result["choices"][0]["message"]["content"]

                # Store
                st.session_state.playbook_md = full_response

                # Extract Mermaid (case-insensitive search)
                mermaid_code = ""
                lower_response = full_response.lower()
                if "```mermaid" in lower_response:
                    start = lower_response.find("```mermaid") + 10
                    end = full_response.find("```", full_response.lower().find("```mermaid") + 10)
                    if end != -1:
                        mermaid_code = full_response[start:end].strip()

                clean_md = full_response.split("```mermaid")[0] if mermaid_code else full_response

                # Display
                with col_main:
                    st.markdown(clean_md, unsafe_allow_html=True)

                with col_flow:
                    st.subheader("Playbook Flowchart")
                    if mermaid_code:
                        # Use native Streamlit components.html for Mermaid
                        html_content = f"""
                        <div class="mermaid">{mermaid_code}</div>
                        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                        <script>
                            mermaid.initialize({{
                                startOnLoad: true,
                                theme: 'base',
                                themeVariables: {{ primaryColor: '#1d4ed8', secondaryColor: '#dc2626' }},
                                flowchart: {{ useMaxWidth: true }}
                            }});
                        </script>
                        """
                        components.html(html_content, height=700, scrolling=True)
                    else:
                        st.info("No flowchart in response")

                break  # Success

            except requests.exceptions.RequestException as e:
                if attempt == 2:
                    st.error(f"Failed after 3 attempts: {e}")
                else:
                    st.warning(f"Attempt {attempt+1} failed, retrying...")
                    time.sleep(2)

# Export & Refine
if "playbook_md" in st.session_state:
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.download_button("Download Markdown", st.session_state.playbook_md, "IR_Playbook.md", "text/markdown")
    with c2:
        b64 = base64.b64encode(st.session_state.playbook_md.encode()).decode()
        st.markdown(f'<a href="data:text/markdown;base64,{b64}" download="IR_Playbook.md">Download .md (alt)</a>', unsafe_allow_html=True)
    with c3:
        if st.button("Refine Playbook", use_container_width=True):
            st.session_state.refine_mode = True

# Refinement chat
if st.session_state.get("refine_mode"):
    st.markdown("### Refine Playbook")
    if prompt := st.chat_input("e.g., Add SOAR steps, Focus on cloud, Make shorter"):
        with st.spinner("Updating..."):
            payload = {
                "model": selected_model,
                "messages": [
                    {"role": "system", "content": "Refine the existing IR playbook. Return the full updated version."},
                    {"role": "user", "content": f"Original:\n{st.session_state.playbook_md}\n\nRequest: {prompt}"}
                ],
                "temperature": 0.2,
                "max_tokens": 4096
            }
            r = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=180)
            r.raise_for_status()
            st.session_state.playbook_md = r.json()["choices"][0]["message"]["content"]
            st.rerun()

# Footer
st.caption("Built with Grok 4 + Streamlit • For blue teams, by blue teams")