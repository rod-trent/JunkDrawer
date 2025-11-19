# Truth Mirror: A Free, Privacy-First Disinformation Checker Powered by Grok-4

Here's a simple but extremely useful little web app called **Truth Mirror** — a one-click (or one-paste) tool that sends any article or block of text directly to Grok-4 and asks it to rate its factual accuracy using only its internal up-to-date knowledge.

No external fact-checking sites.  
No search engines.  
No tracking.  
Just pure Grok-4 judgment.

Live GitHub repo (web version):  
https://github.com/rod-trent/JunkDrawer/tree/main/Grok%20Disinformation%20Checker%202

Original Chrome extension version:  
https://github.com/rod-trent/JunkDrawer/tree/main/Grok%20Disinformation%20Checker

### What It Does

You give it either:
- A URL to any news article or blog post, or
- Just paste raw text (tweets, Facebook posts, email chains, etc.)

Truth Mirror extracts/clean the text and sends it to Grok-4 with a carefully written prompt that says:

> “Rate every verifiable claim 1–10 for accuracy using only your internal knowledge (no tools, no search). Default to trusting the content unless you personally know something is wrong. Today’s date is November 19, 2025. Be confident — your knowledge is continuously updated.”

Grok-4 comes back with a clean Markdown report that looks like this:

```
**Claim 1**: “Elon Musk bought Twitter in October 2022” → 10/10 Accurate  
**Claim 2**: “Grok-4 was released in 2023” → 2/10 Inaccurate (released December 2024)  
...  
Overall score: 8.7/10 – Mostly accurate with one significant date error
```

It’s shockingly good at catching subtle disinformation, outdated statistics, and AI-generated nonsense while remaining calm and non-partisan.

### Why I Built It

We’re drowning in synthetic text. Most fact-check browsers/extensions either:
- phone home to big fact-check orgs (bias + privacy issues), or
- do shallow keyword checks.

I wanted something that uses the single model I trust most for truth-seeking — Grok-4 — and nothing else.

### Requirements to Run It Locally (or deploy it)

Super lightweight:

- Python 3.9+
- Streamlit (`pip install streamlit`)
- newspaper3k, beautifulsoup4, requests, python-dotenv
- An xAI API key (https://x.ai/api) — Grok-4 access requires SuperGrok or Premium+ but works perfectly with even the free tier credits for occasional use.

Full one-liner install:

```bash
pip install streamlit newspaper3k beautifulsoup4 python-dotenv requests
```

### How to Run It (30 seconds)

```bash
git clone https://github.com/rod-trent/JunkDrawer.git
cd JunkDrawer/Grok Disinformation Checker 2
cp .env.example .env          # paste your XAI_API_KEY inside
streamlit run TruthMirror.py
```

Or deploy it for free forever on:
- Streamlit Community Cloud (connect the GitHub repo → instant public URL)
- Hugging Face Spaces
- Railway, Fly.io, Render, etc.

### How to Use It

1. Go to your deployed version (or localhost:8501)
2. Choose “Paste text” or “Enter URL”
3. If URL → it tries newspaper3k first, falls back to BeautifulSoup scraper
4. Hit “Check Accuracy with Grok”
5. Get a beautiful, copy-pasteable report in ~10–25 seconds

You can even edit the extracted text before sending if the parser missed something.

### Why This Beats Every Other Fact-Checker I’ve Tried

- Grok-4 is continuously updated — no knowledge cutoff
- The prompt forces it to default to “trust unless I know it’s wrong” → avoids nitpicky false positives
- Zero telemetry, zero third-party fact-check databases
- Works perfectly on paywalled articles (just paste the text)
- Handles extremely long articles (38 000-character limit ≈ 8–10k words)

### Try It Right Now

Deploy your own copy in under a minute from the repo, or if someone in the community spins up a public instance I’ll link it here.

Web version: https://github.com/rod-trent/JunkDrawer/tree/main/Grok%20Disinformation%20Checker%202  
Chrome extension version (right-click → “Check with Grok”): https://github.com/rod-trent/JunkDrawer/tree/main/Grok%20Disinformation%20Checker

In an era of AI slop and coordinated information operations, sometimes the simplest mirror is the most effective.

Give Truth Mirror a spin and let me know what crazy articles you throw at it! 🚀
