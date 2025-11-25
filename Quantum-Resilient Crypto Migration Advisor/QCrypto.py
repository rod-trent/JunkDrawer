# app.py
import streamlit as st
import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime
import base64
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec

load_dotenv()

# ========================= CONFIG =========================
XAI_API_KEY = os.getenv("XAI_API_KEY")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
MODEL = "grok-2-128k"  # or "grok-beta" depending on access

headers = {
    "Authorization": f"Bearer {XAI_API_KEY}",
    "Content-Type": "application/json"
}

st.set_page_config(page_title="Quantum-Resilient Crypto Migration Advisor", layout="wide")
st.title("🔬 Quantum-Resilient Crypto Migration Advisor")
st.markdown("**Powered by Grok xAI** • Prepare your systems before quantum breaks everything.")

# ========================= SIDEBAR =========================
with st.sidebar:
    st.header("Upload Crypto Assets")
    uploaded_files = st.file_uploader(
        "Drop PEM/DER keys, certificates, or OpenSSL configs",
        accept_multiple_files=True,
        type=["pem", "crt", "cer", "key", "der", "conf", "cfg"]
    )
    
    st.markdown("---")
    st.caption("NIST PQC Winners (Round 4, 2024–2025)")
    st.success("• ML-KEM (Kyber) → Key Encapsulation\n"
               "• ML-DSA (Dilithium) → Signatures\n"
               "• SLH-DSA (Sphincs+) → Stateless Signatures\n"
               "• FN-DSA (Falcon) → Compact Signatures")

# ========================= ANALYSIS FUNCTIONS =========================
def parse_key_file(file_content: bytes):
    try:
        # Try private key
        key = serialization.load_pem_private_key(file_content, password=None)
        if isinstance(key, rsa.RSAPrivateKey):
            bits = key.key_size
            return {"type": "RSA Private Key", "bits": bits, "vulnerable": bits <= 4096}
        elif isinstance(key, ec.EllipticCurvePrivateKey):
            curve = key.curve.name
            return {"type": f"EC Private Key ({curve})", "curve": curve, "vulnerable": curve in ["secp256r1", "secp384r1", "secp521r1"]}
    except:
        pass
    
    try:
        # Try certificate
        cert = x509.load_pem_x509_certificate(file_content)
        pubkey = cert.public_key()
        if isinstance(pubkey, rsa.RSAPublicKey):
            return {"type": "RSA Certificate", "bits": pubkey.key_size, "vulnerable": pubkey.key_size <= 4096}
        elif isinstance(pubkey, ec.EllipticCurvePublicKey):
            curve = pubkey.curve.name
            return {"type": f"EC Certificate ({curve})", "curve": curve, "vulnerable": True}
    except:
        return {"type": "Unknown / Config", "vulnerable": None}

    return {"type": "Binary/File", "vulnerable": None}

def call_grok(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 4000
    }
    try:
        r = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Grok API Error: {str(e)}"

# ========================= MAIN APP =========================
if uploaded_files:
    assets = []
    for f in uploaded_files:
        content = f.read()
        info = parse_key_file(content)
        info["name"] = f.name
        info["size"] = len(content)
        assets.append(info)

    st.subheader("🩺 Audit Results")
    vulnerable_count = sum(1 for a in assets if a.get("vulnerable"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Assets", len(assets))
    with col2:
        st.metric("Quantum-Vulnerable", vulnerable_count, delta=f"{vulnerable_count/len(assets)*100:.0f}% risk" if assets else None)
    with col3:
        st.metric("Estimated CRQC Break Year", "2031–2035" if vulnerable_count else "Post-2040")

    if vulnerable_count > 0:
        st.error(f"🚨 {vulnerable_count} asset(s) vulnerable to Shor's algorithm on a cryptographically relevant quantum computer (CRQC).")
        st.info("Harvest-now-decrypt-later attacks are already in progress by nation-states.")

    if st.button("🚀 Generate Quantum Migration Roadmap (via Grok xAI)", type="primary"):
        with st.spinner("Grok is analyzing your keys and building a custom migration plan..."):
            system_prompt = {
                "role": "system",
                "content": "You are a world-leading post-quantum cryptography migration expert. Be precise, practical, and opinionated. Use NIST PQC standards (ML-KEM, ML-DSA, SLH-DSA). Favor hybrid schemes for 2025–2030 transition. Include real code snippets (OpenSSL 3.0+, liboqs, cryptography.io, Go). Structure output with clear phases and timelines."
            }

            user_prompt = {
                "role": "user",
                "content": f"""Analyze these cryptographic assets and create a detailed, phased migration plan to NIST-approved post-quantum algorithms.

Assets detected:
{json.dumps(assets, indent=2)}

Requirements:
- Assess harvest-now-decrypt-later risk
- Recommend hybrid (classical + PQC) for 2025–2030
- Final target: pure PQC by 2035
- Prioritize ML-KEM-768 and ML-DSA-65 unless size is critical
- Include exact OpenSSL commands and code snippets
- Provide a timeline slider visualization description
- Estimate cost and effort per phase

Output in clear Markdown with tables and code blocks."""
            }

            grok_response = call_grok([system_prompt, user_prompt])

            st.success("Migration Roadmap Generated by Grok xAI")
            st.markdown(grok_response)

            # Interactive Threat Timeline
            st.subheader("🕰️ Quantum Threat Timeline")
            year = st.spinner_slider(
                "Drag to see quantum readiness impact",
                min_value=2025,
                max_value=2040,
                value=2030,
                step=1
            )

            timeline_prompt = {
                "role": "user",
                "content": f"Summarize in 3 bullet points what happens to the uploaded keys in {year} if no migration occurs vs if the roadmap is fully implemented."
            }
            timeline = call_grok([system_prompt, user_prompt, timeline_prompt])
            st.markdown(timeline)

else:
    st.info("👈 Upload your private keys, certificates, or OpenSSL configs to begin.")
    st.markdown("""
### Example Use Cases
- Audit your VPN (IPsec/IKEv2, OpenVPN) keys
- Migrate TLS certificates (Nginx, Apache, HAProxy)
- Prepare SSH, code signing, or blockchain wallets
- Compliance: CNSI, BSI TR-02102-1, NSA CNSA 2.0
    """)

# ========================= FOOTER =========================
st.markdown("---")
st.caption("Quantum-Resilient Crypto Migration Advisor • Built with ❤️ and Grok xAI • Not financial advice • Use at your own risk")