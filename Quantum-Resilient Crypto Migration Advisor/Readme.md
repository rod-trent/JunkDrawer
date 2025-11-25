# **Meet “QCrypto”: Your Personal Post-Quantum Crypto Migration Advisor**  
(Powered by Grok xAI)

If you’ve been putting off post-quantum migration because “it’s complicated,” “the standards aren’t final,” or “I’ll deal with it later,” then your excuses just expired.

Meet QCrypto — the open, free Streamlit app that instantly audits your RSA/ECDSA keys and certificates, then hands you a bespoke, Grok xAI–generated migration roadmap to NIST’s finalized post-quantum standards (ML-KEM, ML-DSA, SLH-DSA).

**Permanent home & source (always free, no sign-up, no paywall):**  
https://github.com/rod-trent/JunkDrawer/tree/main/Quantum-Resilient%20Crypto%20Migration%20Advisor

Live demo (hosted forever): https://qcrypto.streamlit.app  
Or run it 100% locally — your private keys never leave your machine.

### What happens in under a minute

1. Drag-and-drop any PEM/DER private keys, certificates, or OpenSSL configs  
2. Instantly see which assets are vulnerable to Shor’s algorithm (spoiler: almost everything still is)  
3. Click one button → Grok xAI analyzes exactly what you uploaded and returns a complete, phased migration plan including:
   - Hybrid schemes for safe 2025–2030 transition
   - Exact OpenSSL 3.3+ / liboqs commands
   - Python, Go, and Rust code snippets
   - Timeline, cost, and effort estimates
   - An interactive “what happens in year X if I do nothing” slider

### Why right now (November 2025) is the moment

- NIST FIPS 203/204/205 (ML-KEM, ML-DSA, SLH-DSA) are official  
- OpenSSL + liboqs supports them in production today  
- Google, Cloudflare, and BSI are already shipping hybrid certificates in 2025  
- Harvest-now-decrypt-later attacks are real and happening right now

The tech is ready. The standards are done. The attackers are already collecting.

### Real example output (Grok-generated)

```markdown
Phase 1 – 2025–2026: Hybrid Defense (Zero downtime)
→ TLS: ML-KEM-768 + existing RSA-3072
→ OpenSSL one-liner for hybrid key:
  openssl genpkey -algorithm ML-KEM-768 > mlkem_priv.pem && cat rsa3072_priv.pem mlkem_priv.pem > hybrid_priv.pem

Phase 3 – 2033–2035: Pure PQC
→ Drop RSA/ECDSA completely → ML-DSA-65 signatures + ML-KEM-768 key exchange
```

### Who needs this yesterday

- Anyone running TLS (Kubernetes, Nginx, HAProxy, CDN edge)  
- VPN/IPsec/WireGuard/OpenVPN administrators  
- SSH CA and code-signing key owners  
- Blockchain projects still on secp256k1  
- Teams facing CNSA 2.0, BSI TR-02102, or ETSI PQC deadlines

### Get it now — permanently yours

GitHub (full source, always free):  
https://github.com/rod-trent/JunkDrawer/tree/main/Quantum-Resilient%20Crypto%20Migration%20Advisor

Live version: https://qcrypto.streamlit.app

Local install (2 commands):
```bash
git clone https://github.com/rod-trent/JunkDrawer.git
streamlit run "Quantum-Resilient Crypto Migration Advisor/QCrypto.py"
```

The quantum clock is ticking louder every month.  
QCrypto turns “I should probably do something” into “here’s exactly what to do next Tuesday.”

Hope it saves you (and your keys) before 2035.

See you on the post-quantum side. 🔬


