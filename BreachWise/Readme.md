# BreachWise: Your Personal Data-Breach Guardian Powered by HaveIBeenPwned + Grok xAI

BreachWise is a beautiful, 100% open-source, self-contained web application that instantly reveals if your email has been compromised in any known data breach… and then hands the results to Grok (xAI) for an intelligent, human-readable risk assessment.

Permanent home & source code:  
https://github.com/rod-trent/JunkDrawer/tree/main/BreachWise

This is not a hosted SaaS. This is a tool you run yourself — exactly the way it should be when you’re dealing with sensitive emails and breach data.

## What Breach Wise Actually Is

BreachWise is a single-file Streamlit app (BreachWise.py) plus a few tiny supporting files that:

1. Queries HaveIBeenPwned (HIBP) for every breach an email appears in  
2. Visualizes your personal breach timeline with an interactive Plotly chart  
3. Sends the breach details to Grok (xAI) for a customized, plain-English risk analysis  
4. Generates a gorgeous, professional PDF report with one click — complete with timeline and full Grok assessment

All of this happens locally on whatever machine or server you choose to run it on. Zero data ever leaves your control unless you explicitly send it to the HIBP and xAI APIs (using your own keys).

## Why This Matters More Than Ever in 2025

- 18+ billion accounts exposed and counting  
- Credential stuffing remains the #1 attack vector  
- Most people have no idea which of their decades-old breaches actually matter today  

Knowing you’re pwned is useless if you don’t know what to do next.  
BreachWise doesn’t just say “you’re in 12 breaches” — it tells you which ones are dangerous right now and exactly what actions to take.

## Feature Highlights

- Instant, respectful HIBP lookups (proper headers, rate-limiting aware)  
- Interactive breach timeline (reversed chronological order, just like a Gantt chart)  
- Real-time Grok xAI personalized risk analysis  
- One-click professional PDF report generation (timeline + full Grok analysis)  
- Sidebar showing the 5 most recent global breaches  
- Clean “no breaches” celebration with balloons  
- Fully client-side capable when keys are provided  
- No telemetry, no logging, no accounts, no data retention  
- Works perfectly on desktop and mobile browsers  

## Tech Stack (All Open Source)

- Python + Streamlit  
- HaveIBeenPwned API  
- Grok xAI API  
- Plotly Express (interactive charts)  
- pdfkit + wkhtmltopdf (PDF reports)  
- python-dotenv for clean, secure credential handling  

## Requirements to Run (You Control Everything)

### Software
```bash
Python 3.9+
pip install streamlit pandas plotly pdfkit python-dotenv hibp-client
```

### PDF Generation
- Windows: wkhtmltopdf installed (auto-detects common paths)  
- Linux/macOS: wkhtmltopdf in PATH  
  (apt install wkhtmltopdf / brew install wkhtmltopdf)

### API Keys (Both Free for Personal/Reasonable Use)
1. HaveIBeenPwned API key → https://haveibeenpwned.com/API/Key  
2. Grok xAI API key → https://console.x.ai

### Secure Credential Storage (No Streamlit secrets, no cloud lock-in)

Create a .env file in the BreachWise directory:

```env
HIBP_API_KEY=your-hibp-key-here
GROK_API_KEY=your-xai-grok-key-here
```

That’s it. Your keys never leave your machine.

## How to Deploy & Run (100% Self-Hosted)

### Option 1 — Run Locally (Instant)

```bash
git clone https://github.com/rod-trent/JunkDrawer.git
cd JunkDrawer/BreachWise
cp .env.example .env          # add your real keys
pip install -r requirements.txt   # (or just the packages above)
streamlit run BreachWise.py
```

Open http://localhost:8501 and start checking.

### Option 2 — Deploy Anywhere You Want

Because it’s just Python + Streamlit, you can deploy it literally anywhere:

- Your own VPS (Ubuntu, Docker coming soon)  
- Render, Railway, Fly.io, Northflank, Deta Space  
- Company intranet server  
- Raspberry Pi in your home lab  
- Even a private Hugging Face Space (if you want)

No dependency on Streamlit Community Cloud. No vendor lock-in. Ever.

## How to Use It (30-Second User Guide)

1. Launch the app  
2. Type any email address  
3. Click “Check for Breaches”  
4. Instantly see:  
   - Clean → balloons + happy Grok message  
   - Compromised → full timeline + Grok’s prioritized action plan  
5. Click “Download My Breach Report (PDF)” — ready to save or email

Real example of what Grok tells users:

> “The 2012 LinkedIn breach is your biggest risk — if you’ve ever reused that password, change it everywhere today. The Adobe and Canva incidents only leaked your email, so no urgent password action is needed. You still don’t have 2FA enabled on your Microsoft account — turn it on immediately; that’s your weakest link right now.”

## Privacy & Security Philosophy

- Your email never hits my server — it only goes directly to HIBP and xAI via your own API keys  
- Nothing is logged, tracked, or stored  
- You own the code, the keys, and the instance  
- Open source → audit it, fork it, improve it

## What’s Next (Contributions Very Welcome!)

- Bulk CSV email checking  
- Pwned Passwords integration  
- Domain search (company breach exposure)  
- Multiple Grok personas (“Explain like I’m 5” / “Red-team mode”)  

## Final Thought

In an age of endless breaches, the least we deserve is a tool that’s beautiful, honest, private, and actually helpful.

BreachWise is that tool — and now it’s yours to run, host, and trust completely.

Go check your email (and your parents’, and your team’s) right now.

https://github.com/rod-trent/JunkDrawer/tree/main/BreachWise

Stay safe out there.  

